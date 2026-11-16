"""Amendment R10-16: two control updates that are harmless by construction, under the release rule of R10-6.
Exploratory.

Inputs: erc_haiku/raw.jsonl (cells t0 and tord) and erc2_haiku/raw.jsonl (cell trep); 10 reads per arm on the specific
set and 1 on the open and guesthouse sets (control.READS); MultiWOZ 2.4 and hotel_db.json. With --pilot it reads the
pilot rows (a dry run of the code). Outputs: r10/analysis/out/control.md and control.json (--pilot: control_pilot.*).

Definitions (fixed in R10-16 before any call):
- Each update has a control arm and an update arm. Update (a), trep: erc2_haiku trep against erc_haiku t0. Update (b),
  tord: erc_haiku tord against erc_haiku t0. Every cell keeps the names and values of t0, so release_analyze.read_of
  with the arm "t0" reads every row.
- The control reads go into the arm "t0" and the update reads into the arm "tedit", and release_analyze.analyse runs
  on them without change: decide, release and interval_level of Appendix I; L = 5 points; one look; level 98.75%
  (release_analyze.LEVEL); percentile cluster bootstrap over prefixes (2,000 draws, seed 20261112).
- Description: the same rule on read 1 of each arm only (the R10-6 design, 1 read per arm).
Usage (from explore/): .venv/bin/python -I r10/analysis/control_analyze.py [--pilot]
"""
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
EXPLORE = R10.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(R10))
sys.path.insert(0, str(HERE))
import control  # noqa: E402
import gold  # noqa: E402
import release_analyze as ra  # noqa: E402
import runs  # noqa: E402

OUT = HERE / "out"
# update: (agent, (control folder, control cell), (update folder, update cell))
UPDATES = {"haiku trep (a)": ("haiku", ("erc_haiku", "t0"), ("erc2_haiku", "trep")),
           "haiku tord (b)": ("haiku", ("erc_haiku", "t0"), ("erc_haiku", "tord"))}


def load_cell(folder, cell, pilot, first_only=False):
    """{dialogue id + ".json": [(kind, fields or reason)]} of one cell, or None when the file does not exist."""
    path = EXPLORE / folder / ("pilot_raw.jsonl" if pilot else "raw.jsonl")
    if not path.exists():
        return None
    out = collections.defaultdict(list)
    for line in path.read_text().splitlines():
        r = json.loads(line)
        _, d, c, read = r["custom_id"].split("-")
        if c == cell and (not first_only or read == "1"):
            out[d + ".json"].append(ra.read_of(r, "t0"))
    return out


def reads_of(control_reads, update_reads):
    reads = collections.defaultdict(list)
    for d, lst in control_reads.items():
        reads[(d, "t0")] = lst
    for d, lst in update_reads.items():
        reads[(d, "tedit")] = lst
    return reads


def per_dialogue_reads(control_reads, update_reads, ids):
    n = collections.Counter()
    for d in ids:
        n[(len(control_reads.get(d, [])), len(update_reads.get(d, [])))] += 1
    return {f"{a} and {b}": k for (a, b), k in sorted(n.items())}


def pts(x):
    return "-" if x is None else f"{x:+.1f}"


def pct(x):
    return "-" if x is None else f"{100 * x:.1f}%"


def predictions(res):
    def model_decision(u):
        e = res.get(u)
        return None if e is None else e["all"]["release"]

    p = {}
    for k, u in (("C1", "haiku trep (a)"), ("C2", "haiku tord (b)")):
        d = model_decision(u)
        p[k] = {"words": f"Haiku, update {u.split()[1]} {u.split()[2]}: the rule gives \"pass\"", "value": d,
                "held": "n/a" if d is None else "held" if d == "pass" else "failed"}
    sets = {u: [e["all"]["sets"][s]["decision"] for s in ("open", "specific")] for u, e in res.items()}
    p["C3"] = {"words": "no set of a control update is \"flag-worthy\"", "value": sets,
               "held": "n/a" if not sets else "failed" if any("flag-worthy" in v for v in sets.values()) else "held"}
    p["C4"] = {"words": "Sonnet, update (a): the rule gives \"pass\"", "value": None,
               "held": "n/a (Sonnet did not run: its bound did not fit the shared limit)"}
    return p


def markdown(out):
    L = ["## Harmless control updates under the release rule (amendment R10-16)" +
         (" - pilot rows only (dry run; no result)" if out["pilot"] else ""), "",
         f"Exploratory. Haiku answered the 554 first requests of experiment A with the original tool (t0, the control), "
         f"with the original tool again in a new batch (trep, update a), and with the same tool whose schema fields are "
         f"in alphabetical order (tord, update b). Reads per arm: {control.READS['specific']} on the specific set, "
         f"{control.READS['open']} on the open and guesthouse sets. Rule of R10-6 (Appendix I, unchanged): L = {ra.L} "
         f"points, one look, {100 * ra.LEVEL:.2f}% percentile cluster bootstrap intervals over prefixes "
         f"({ra.DRAWS} draws, seed {ra.SEED}).", ""]
    if out["missing"]:
        L += [f"Not fetched at this run: {', '.join(out['missing'])}.", ""]
    for label, key in (("All reads (the design of R10-16)", "all"),
                       ("Description: read 1 of each arm only (the design of R10-6)", "read1")):
        L += [f"### Decisions: {label}", "", f"| Update | Set | Pairs | Change, points | {100 * ra.LEVEL:.2f}% interval | "
              "Half-width | Set decision | Update decision |", "|---|---|---|---|---|---|---|---|"]
        for u, e in out["updates"].items():
            r = e[key]
            for s in ("open", "specific"):
                x = r["sets"][s]
                iv = x["interval"]
                hw = "-" if not iv else f"{(iv[1] - iv[0]) / 2:.1f}"
                L.append(f"| {u} | {s} | {x['pairs']} | {pts(x['change'])} | "
                         f"{'-' if not iv else f'[{pts(iv[0])}, {pts(iv[1])}]'} | {hw} | {x['decision']} | "
                         f"{r['release'] if s == 'open' else ''} |")
        L.append("")
    L += ["### Descriptions (all reads)", "", "Rate of `type` holding hotel (valid reads):", "",
          "| Update | Set | Control (t0) | Update | Reads per prefix (control and update: prefixes) |", "|---|---|---|---|---|"]
    for u, e in out["updates"].items():
        for s in ("open", "specific", "guesthouse"):
            a, b = e["all"]["rates"][s]["t0"], e["all"]["rates"][s]["tedit"]
            L.append(f"| {u} | {s} | {pct(a['share'])} ({a['k']}/{a['n']}) | {pct(b['share'])} ({b['k']}/{b['n']}) | "
                     f"{json.dumps(e['reads_per_prefix'][s])} |")
    L += ["", "| Update | Trade: wrong removed | correct lost | ratio | Blocking filters, open set: control | update |",
          "|---|---|---|---|---|---|"]
    for u, e in out["updates"].items():
        t, bo = e["all"]["trade"], e["all"]["blocking_open"]
        if t is None:
            tr = "- | - | not computed"
        elif not t["defined"]:
            tr = f"{t['wrong_removed']:.1f} | {t['correct_lost']:.1f} | not defined (no wrong value removed)"
        else:
            tr = f"{t['wrong_removed']:.1f} | {t['correct_lost']:.1f} | {t['ratio']:.2f}"
        L.append(f"| {u} | {tr} | " + " | ".join(f"{pct(bo[a]['share'])} ({bo[a]['k']}/{bo[a]['n']})"
                                                 for a in ra.ARMS) + " |")
    L += ["", "Read kinds and `type` values, per arm:", ""]
    for u, e in out["updates"].items():
        for arm, name in (("t0", "control"), ("tedit", "update")):
            L.append(f"- {u} {name}: kinds {json.dumps(e['all']['kinds'][arm])}; type "
                     f"{json.dumps(e['all']['type_values'][arm])}")
    L += ["", "### Predictions (R10-16)", "", "| # | Words | Value | Result |", "|---|---|---|---|"]
    for k, v in out["predictions"].items():
        L.append(f"| {k} | {v['words']} | {json.dumps(v['value'])} | {v['held']} |")
    return "\n".join(L) + "\n"


def main():
    pilot = "--pilot" in sys.argv
    control.check_amendment()
    data, g = runs.context()
    db = gold.hotel_db()
    sets = ra.request_sets(data, g)
    out = {"amendment": "R10-16", "exploratory": True, "pilot": pilot, "L": ra.L, "level": ra.LEVEL,
           "reads": control.READS, "missing": [], "updates": {}}
    for u, (agent, (cf, cc), (uf, uc)) in UPDATES.items():
        c_all, u_all = load_cell(cf, cc, pilot), load_cell(uf, uc, pilot)
        if c_all is None or u_all is None:
            out["missing"] += [f for f, x in ((cf, c_all), (uf, u_all)) if x is None]
            continue
        c_1, u_1 = load_cell(cf, cc, pilot, True), load_cell(uf, uc, pilot, True)
        out["updates"][u] = {"agent": agent, "control": f"{cf} {cc}", "update": f"{uf} {uc}",
                             "all": ra.analyse(reads_of(c_all, u_all), sets, data, db),
                             "read1": ra.analyse(reads_of(c_1, u_1), sets, data, db),
                             "reads_per_prefix": {s: per_dialogue_reads(c_all, u_all, ids) for s, ids in sets.items()}}
    out["missing"] = sorted(set(out["missing"]))
    out["predictions"] = predictions(out["updates"])
    OUT.mkdir(exist_ok=True)
    stem = "control_pilot" if pilot else "control"
    (OUT / f"{stem}.json").write_text(json.dumps(out, indent=1, default=float))
    (OUT / f"{stem}.md").write_text(markdown(out))
    print((OUT / f"{stem}.md").read_text())


if __name__ == "__main__":
    main()
