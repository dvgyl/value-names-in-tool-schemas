"""Rerun the analyses of the preprint offline, and compare each output with the stored file.

Put the public corpus in corpus/ first (README, section 3, step 2). Then, from the repository folder:

    python3 -I reproduce.py --smoke      the smoke test: one run, five values (do this first; about 10 seconds)
    python3 -I reproduce.py              unpack the answer rows, then run every analysis that can run here
    python3 -I reproduce.py a h i        run only the analyses with these names
    python3 -I reproduce.py --list       list the analyses and stop
    python3 -I reproduce.py --checks     also run the checks of the code (README, section 5)
    python3 -I reproduce.py --slow       also run the slow simulation steps (about 20 minutes)
    python3 -I reproduce.py --unpack     only unpack the answer rows

What the script does:
1. It unpacks each explore/<run>/raw.jsonl.gz (and conversations.jsonl.gz) next to itself, without ".gz".
   The analysis scripts read the unpacked files.
2. It runs the steps of each analysis of analyses.json with this Python interpreter, in isolated mode (-I).
   No analysis makes a model call or a network call.
3. It compares each output with the stored file, byte for byte. Some outputs hold a time, a duration or a checksum
   of a project file; analyses.json names these keys and lines, and the comparison leaves them out. When an output
   is the same, the stored file stays. When it differs, the new file stays in its place, so that `git diff` shows
   the difference. When a step fails, the stored files come back.
The last line tells how many analyses gave the stored results. The exit code is 0 when all of them did.
Option --json FILE writes the full report to FILE.
"""
import gzip
import json
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent
EXPLORE = ROOT / "explore"
CORPUS = ROOT / "corpus" / "MULTIWOZ2.4"
MANIFEST = json.loads((ROOT / "analyses.json").read_text())
ANALYSES = {a["name"]: a for a in MANIFEST["analyses"]}
SMOKE_RUN = "era1_haiku"
WHY = {"sealed": "needs the held-out answers, which stay encrypted (README, section 8)",
       "files": "reads files that are not in this repository (README, section 8)",
       "none": "no script (README, section 4)", "slow": "slow: run it with --slow",
       "private": "needs the private labels and the labelling key (README, section 8)"}


def unpack(only=None):
    """Unpack every answer file that is missing or has another size than its .gz copy."""
    n = 0
    for gz in sorted(x for x in EXPLORE.glob("*/*.jsonl.gz") if not x.name.startswith("._")):
        if only and gz.parent.name not in only:
            continue
        target = gz.with_suffix("")
        with open(gz, "rb") as fh:
            fh.seek(-4, 2)
            size = int.from_bytes(fh.read(4), "little")  # gzip stores the size of the data (modulo 2**32)
        if target.exists() and target.stat().st_size % 2 ** 32 == size:
            continue
        with gzip.open(gz, "rb") as fi, open(target, "wb") as fo:
            while chunk := fi.read(1 << 20):
                fo.write(chunk)
        n += 1
    return n


def run(argv, cwd):
    t = time.time()
    p = subprocess.run([sys.executable, "-I", *argv], cwd=cwd, capture_output=True, text=True)
    return p, round(time.time() - t, 1)


def without(x, keys):
    """x without the dictionary keys in keys, at any depth."""
    if isinstance(x, dict):
        return {k: without(v, keys) for k, v in x.items() if k not in keys}
    if isinstance(x, list):
        return [without(v, keys) for v in x]
    return x


def same_output(new, old, a, name):
    if new == old:
        return True
    if name.endswith(".json") and a.get("ignore_keys"):
        try:
            return without(json.loads(new), set(a["ignore_keys"])) == without(json.loads(old), set(a["ignore_keys"]))
        except ValueError:
            return False
    if a.get("ignore_lines"):
        pat = re.compile(a["ignore_lines"])
        keep = lambda b: [x for x in b.decode().splitlines() if not pat.match(x)]  # noqa: E731
        return keep(new) == keep(old)
    return False


def one(a, slow):
    row = {"name": a["name"], "part": a["part"], "topic": a["topic"], "compare": []}
    kind = a["kind"]
    if kind in ("sealed", "files", "none", "private") or (kind == "slow" and not slow):
        row.update(status="not run", why=a.get("why", WHY[kind]))
        return row
    compare = a.get("compare", a["outputs"])
    stored = {f: (ROOT / f).read_bytes() for f in a["outputs"]}
    row["seconds"] = 0.0
    p = None
    for step in a["steps"]:
        p, seconds = run(step["cmd"], ROOT if step["cwd"] == "." else EXPLORE)
        row["seconds"] = round(row["seconds"] + seconds, 1)
        if p.returncode:
            for f, old in stored.items():  # a failed step must not leave a half-written file
                (ROOT / f).write_bytes(old)
            row.update(status="failed", why=(p.stderr.strip().splitlines() or ["no message"])[-1][:300])
            return row
    for f in a.get("remove_after", []):  # a file that the script also writes, but that this repository does not store
        (ROOT / f).unlink(missing_ok=True)
    ok = True
    for f in a["outputs"]:
        path, old = ROOT / f, stored[f]
        new = path.read_bytes() if path.exists() else None
        if f not in compare:
            path.write_bytes(old)  # written again, but not compared (analyses.json, "compare")
            continue
        if new is not None and same_output(new, old, a, f):
            if new != old:
                path.write_bytes(old)  # only an ignored key or line differs: keep the stored file
            row["compare"].append(f"{pathlib.Path(f).name} same")
        else:
            ok = False
            row["compare"].append(f"{pathlib.Path(f).name} {'missing' if new is None else 'DIFFERENT'}")
    if a.get("printed"):
        same = p.stdout == (ROOT / a["printed"]).read_text()
        ok = ok and same
        row["compare"].append(f"printed text {'same as' if same else 'DIFFERENT from'} {pathlib.Path(a['printed']).name}")
    row["status"] = "same" if ok else "different"
    return row


def smoke():
    unpack(only={SMOKE_RUN})
    p, seconds = run(["smoke_test.py"], EXPLORE)
    sys.stdout.write(p.stdout)
    sys.stderr.write(p.stderr)
    return p.returncode


def checks():
    rows = []

    def add(name, p, seconds, ok, note=""):
        rows.append({"name": name, "status": "same" if ok else "different", "seconds": seconds,
                     "compare": [note] if note else [],
                     "why": "" if ok else (p.stderr.strip().splitlines() or [""])[-1][:300]})

    p, s = run(["verify_requests.py"], EXPLORE)
    counts = json.loads(p.stdout.strip().splitlines()[-1]) if p.returncode == 0 else {}
    add("check: rebuild the requests", p, s, p.returncode == 0 and counts.get("different") == 0, json.dumps(counts))
    p, s = run(["main/exp0/test_analysis.py"], EXPLORE)
    add("check: frozen analysis on simulated answers", p, s, p.returncode == 0)
    stored = {f: f.read_bytes() for f in sorted((ROOT / "tables").glob("*.gz")) if not f.name.startswith("._")}
    p, s = run(["answer_tables.py"], EXPLORE)
    notes, ok = [], p.returncode == 0
    for f, old in stored.items():
        new = f.read_bytes() if f.exists() else b""
        same = bool(new) and gzip.decompress(new) == gzip.decompress(old)
        ok = ok and same
        if same:
            f.write_bytes(old)  # the same table; keep the stored file (the gzip header holds a time)
        notes.append(f"{f.name} {'same' if same else 'DIFFERENT'}")
    add("check: scored tables", p, s, ok, ", ".join(notes))
    p, s = run(["smoke_test.py"], EXPLORE)
    last = (p.stdout.strip().splitlines() or [""])[-1]
    add("check: smoke test", p, s, p.returncode == 0 and last.endswith("of 5 values as expected")
        and last.startswith("smoke test: 5 "), last)
    need_data = set(MANIFEST["unit_tests_need_data"])
    for t in sorted((EXPLORE / "r10" / "tests").glob("test_*.py")):
        if t.name.startswith("._"):
            continue
        p, s = run([f"r10/tests/{t.name}"], EXPLORE)
        expect_fail = t.name in need_data
        add(f"check: unit test {t.name}" + (" (needs withheld data, so it must fail)" if expect_fail else ""),
            p, s, (p.returncode != 0) if expect_fail else (p.returncode == 0))
    for t in MANIFEST["posthoc_tests"]:
        p, s = run([t], EXPLORE)
        add(f"check: unit test {t}", p, s, p.returncode == 0)
    return rows


def main():
    args = sys.argv[1:]
    if "--list" in args:
        for a in MANIFEST["analyses"]:
            print(f"{a['name']:28s} part {a['part']}  {a['kind']:7s} {a['topic']}")
        return 0
    if not (CORPUS / "data.json").exists():
        sys.exit(f"The corpus is missing: {CORPUS.relative_to(ROOT)}/data.json does not exist. "
                 "See README, section 3, step 2.")
    if "--smoke" in args:
        return smoke()
    n = unpack()
    print(f"answer files unpacked: {n}")
    if "--unpack" in args:
        return 0
    json_out = args[args.index("--json") + 1] if "--json" in args else None
    names = [a for a in args if not a.startswith("--") and a != json_out]
    unknown = [x for x in names if x not in ANALYSES]
    if unknown:
        sys.exit(f"unknown analysis: {', '.join(unknown)}. See: python3 -I reproduce.py --list")
    slow = "--slow" in args or bool(names)  # an analysis named on the command line runs, slow or not
    report = []
    for name in names or list(ANALYSES):
        row = one(ANALYSES[name], slow)
        report.append(row)
        print(f"{row['status']:9s} {name:28s} {row.get('seconds', '')!s:>7s}  "
              f"{'; '.join(row['compare']) or row.get('why', '')}", flush=True)
    if "--checks" in args:
        for row in checks():
            report.append(row)
            print(f"{row['status']:9s} {row['name']}  {'; '.join(row['compare']) or row.get('why', '')}", flush=True)
    if json_out:
        pathlib.Path(json_out).write_text(json.dumps(report, indent=1) + "\n")
    ran = [r for r in report if r["status"] != "not run"]
    bad = [r["name"] for r in ran if r["status"] != "same"]
    print(f"\n{len(ran) - len(bad)} of {len(ran)} runs gave the stored results; "
          f"{len(report) - len(ran)} not run (see above). Not as stored: {', '.join(bad) or 'none'}.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
