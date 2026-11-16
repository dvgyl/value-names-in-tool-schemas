"""Sealed storage for the main-study runs (REVISION-12.md section 3).

A run is sealed when its folder name starts with "em". A sealed run never writes a model answer to disk as plain text.
It writes the public fields of each answer (status, usage, served model, stop reason, and whether the text parses as
a JSON object) in plain text, and everything else encrypted.

Encryption: a fresh 256-bit secret per Sealer encrypts each blob with `openssl enc` (AES-256-CBC, PBKDF2). The secret
is written only wrapped with the operator's RSA public key (OAEP, SHA-256) in `seal_keys/<id>.bin`. Only the
operator's private key, which never enters this folder, unwraps it (`unseal.py`). The secret reaches openssl through
a pipe, not through argv or a file.
"""
import base64
import json
import os
import pathlib
import secrets
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import accounts  # noqa: E402

PREFIX = "em"
PUBLIC_FIELDS = ("custom_id", "type", "status", "model", "stop", "provider_stop", "input_tokens", "output_tokens",
                 "reasoning_tokens", "provider_cost", "json_ok")
KEYS = "seal_keys"


def sealed(name):
    return name.startswith(PREFIX)


def public_key():
    """The operator's public key. accounts.EXPLORE is read at call time, so the tests can move it."""
    return accounts.EXPLORE / "main" / "seal_public.pem"


def json_ok(text):
    try:
        return isinstance(json.loads(text), dict)
    except (TypeError, ValueError):
        return False


def public(row):
    """The fields of a raw.jsonl row that a sealed run keeps in plain text."""
    out = {k: row[k] for k in PUBLIC_FIELDS if k in row}
    if "text" in row:
        out["json_ok"] = json_ok(row["text"])
    return out


def _openssl(args, data, secret=None):
    fds = ()
    if secret is not None:
        r, w = os.pipe()
        os.write(w, secret.encode())
        os.close(w)
        fds = (r,)
        args = [*args, "-pass", f"fd:{r}"]
    try:
        out = subprocess.run(["openssl", *args], input=data, capture_output=True, pass_fds=fds)
    finally:
        for fd in fds:
            os.close(fd)
    if out.returncode:
        raise RuntimeError(f"openssl {args[0]} failed: {out.stderr.decode(errors='replace')[:300]}")
    return out.stdout


CIPHER = ["enc", "-aes-256-cbc", "-pbkdf2", "-iter", "10000", "-salt"]


class Sealer:
    """One secret, wrapped once into `<folder>/seal_keys/<id>.bin`. seal() returns a JSON-safe dict."""

    def __init__(self, folder):
        key = public_key()
        if not key.exists():
            sys.exit(f"Not run. {key} is missing. The operator creates it with lib/make_seal_key.sh "
                     f"(REVISION-12.md section 7).")
        self.secret = secrets.token_hex(32)
        self.id = f"{time.strftime('%Y%m%dT%H%M%S')}-{secrets.token_hex(4)}"
        wrapped = _openssl(["pkeyutl", "-encrypt", "-pubin", "-inkey", str(key), "-pkeyopt", "rsa_padding_mode:oaep",
                            "-pkeyopt", "rsa_oaep_md:sha256"], self.secret.encode())
        (folder / KEYS).mkdir(parents=True, exist_ok=True)
        (folder / KEYS / f"{self.id}.bin").write_bytes(wrapped)

    def seal(self, data):
        return {"k": self.id, "c": base64.b64encode(_openssl(CIPHER, data, self.secret)).decode()}


def write_blob(path, data, sealer):
    """One sealed file: a JSON object with the key id and the ciphertext of `data`."""
    tmp = path.with_name(path.name + ".part")
    tmp.write_text(json.dumps(sealer.seal(data)))
    os.replace(tmp, path)


def open_blob(blob, secret):
    """Operator side (unseal.py): the plain bytes of one sealed object."""
    return _openssl([*CIPHER, "-d"], base64.b64decode(blob["c"]), secret)


def unwrap(path, private_key):
    """Operator side (unseal.py): the secret of one seal_keys file. openssl asks for the key's passphrase."""
    return _openssl(["pkeyutl", "-decrypt", "-inkey", str(private_key), "-pkeyopt", "rsa_padding_mode:oaep",
                     "-pkeyopt", "rsa_oaep_md:sha256", "-in", str(path)], None).decode()
