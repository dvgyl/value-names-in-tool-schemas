"""Operator only, after the codes and the test-retest are frozen (REVISION-12.md section 3): open the sealed files of
one run. Usage: python3 -I lib/unseal.py <private key> <run folder> <output folder>

It writes the plain files into the output folder: raw.jsonl (full rows), the batch files, and the synchronous answers.
openssl asks once per key file for the passphrase of the private key.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import seal  # noqa: E402


def main(private_key, folder, out):
    folder, out = pathlib.Path(folder), pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    secrets = {p.stem: seal.unwrap(p, private_key) for p in sorted((folder / seal.KEYS).glob("*.bin"))
               if not p.name.startswith("._")}
    opened = []
    for path in sorted(folder.glob("*.sealed")):
        if path.name.startswith("._"):
            continue
        blob = json.loads(path.read_text())
        target = out / ("raw.jsonl" if path.name == "raw.sealed" else path.name.removesuffix(".sealed"))
        target.write_bytes(seal.open_blob(blob, secrets[blob["k"]]))
        opened.append(target.name)
    for name in ("responses.jsonl", "pilot_responses.jsonl"):
        path = folder / name
        if not path.exists():
            continue
        with open(out / name, "w") as fh:
            for line in path.read_text().splitlines():
                rec = json.loads(line)
                if "sealed" in rec:
                    rec = json.loads(seal.open_blob(rec["sealed"], secrets[rec["sealed"]["k"]]))
                fh.write(json.dumps(rec) + "\n")
        opened.append(name)
    print(f"{folder.name}: opened {', '.join(opened) or 'nothing'} into {out}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
