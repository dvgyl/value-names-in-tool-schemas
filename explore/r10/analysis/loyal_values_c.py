"""Final 8, part 3 (the paper): check the R10-23 numbers of the paper against the stored result and its independent check.

This file is a copy of the project script (an internal file) with the paths of
the study folder; it reads files that are not in the supplementary package (README.md, section 10).
Usage (from explore/):
  python3 -I r10/analysis/loyal_values_c.py compute     (writes out/loyal_values_c.json and .md)
  python3 -I r10/analysis/loyal_values_c.py check <the paper>
No model call and no network call. Reads only workshops/steer-search/out/result.md and result.json, and
workshops/steer-search/VERIFIED-STEER3.md.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
EXPLORE = HERE.parents[1]
ROOT = EXPLORE.parents[1]  # the project folder: the files under workshops/ are not in the supplementary package
RES = ROOT / "workshops/steer-search/out/result.md"
RESJ = ROOT / "workshops/steer-search/out/result.json"
VER = ROOT / "workshops/steer-search/VERIFIED-STEER3.md"
OUT = HERE / "out"
MODELS = ("haiku", "sol", "luna")


def fmt(x):
    return x.replace("-", "−")


def main_rows():
    t = RES.read_text(encoding="utf-8")
    rows = {}
    for line in t.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 10 and cells[0] in MODELS and cells[1] == "open":
            m, _, kind, cell, first_rate, first_ch, last_rate, last_ch, cat, _drop = cells
            rows[(m, kind, cell)] = {"first_rate": first_rate, "first": first_ch, "last_rate": last_rate,
                                     "last": re.sub(r" \(up.*", "", last_ch), "category": cat}
    panel = {(k, c, s): ch for k, c, s, ch in
             re.findall(r"^\| ([\w-]+) \| (\w+) \| (first|last) \| 448 \| ([^|]+) \|$", t, re.M)}
    preds = dict(re.findall(r"^\| (Q\d) \| (\{[^|]+\}) \|$", t, re.M))
    q5 = re.search(r"^\| haiku \| open \| hotel-only \| h1 \|[^\n]*\| persists \| ([^|]+) \|$", t, re.M).group(1).strip()
    again = {}
    for m in MODELS:
        block = t[t.index(f"- {m}: conversation status"):]
        for cell in ("t0", "h1", "g1"):
            line = re.search(rf"  - {cell}: [^\n]*", block).group(0)
            a = re.search(r"searched again (\d+)/(\d+)", line)
            e = re.search(r"first-search exclusion \(either\) \{\"n\": (\d+), \"searched_again\": (\d+)", line)
            again[f"{m} {cell}"] = {"again": [int(a.group(1)), int(a.group(2))], "excl_n": int(e.group(1)),
                                    "excl_again": int(e.group(2))}
    status = dict(re.findall(r"- (\w+): conversation status (\{[^}]+\})", t))
    return {"rows": {" ".join(k): v for k, v in rows.items()}, "panel": {" ".join(k): v.strip() for k, v in panel.items()},
            "predictions": {k: json.loads(v) for k, v in preds.items()}, "q5": q5, "searched_again": again,
            "status": {k: json.loads(v) for k, v in status.items()}}


def verified():
    v = VER.read_text(encoding="utf-8")
    costs = re.findall(r"^\| (Haiku|Sol|Luna|All three) [^|]*\| [^|]+\| [^|]+\| ([\d.]+) \|$", v, re.M)
    return {"costs": {k: float(x) for k, x in costs},
            "max_points_failed": re.search(r"Sol `h1`, 4 conversations, ([\d.]+) points", v).group(1),
            "quote_rule_calls": re.search(r"the rule changes (\d+) of ([\d,]+) calls", v).groups(),
            "control_between_runs": "about 3 points" if "moved by about 3 points between runs" in v else None,
            "all_confirmed": all(x in v for x in ("| 1. Conversation counts and statuses; the cancelled rows | "
                                                  "Confirmed |", "| 3. Q1 to Q5 against the text of the amendment | "
                                                  "Confirmed"))}


def compute():
    res = {"exploratory": True, "result": main_rows(), "verified": verified()}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "loyal_values_c.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    r = res["result"]["rows"]
    lines = ["## the paper, final 8 part 3: R10-23 numbers (from result.md; confirmed in VERIFIED-STEER3.md)", ""]
    for m in MODELS:
        lines.append(f"- {m}: H1 hotel-only first {r[f'{m} hotel-only h1']['first']}, last {r[f'{m} hotel-only h1']['last']}; "
                     f"G1 either first {r[f'{m} either g1']['first']}, last {r[f'{m} either g1']['last']}; t0 "
                     f"{r[f'{m} hotel-only t0']['first_rate']} / {r[f'{m} hotel-only t0']['last_rate']}")
    lines.append(f"- panel {res['result']['panel']}; Q5 {res['result']['q5']}; predictions {res['result']['predictions']}")
    lines.append(f"- searched again {res['result']['searched_again']}")
    lines.append(f"- verified {res['verified']}")
    (OUT / "loyal_values_c.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def check(md_path):
    res = json.loads((OUT / "loyal_values_c.json").read_text())
    flat = re.sub(r"\s+", " ", open(md_path, encoding="utf-8").read())
    r, a = res["result"]["rows"], res["result"]["searched_again"]
    fails = 0

    def ok(name, cond):
        nonlocal fails
        print(("ok   " if cond else "FAIL ") + name)
        fails += 0 if cond else 1

    def has(*ps):
        return all(p in flat for p in ps)

    # Table F5 rows
    for m, name in zip(MODELS, ("Haiku", "Sol", "Luna")):
        t0 = r[f"{m} hotel-only t0"]
        base = f"{t0['first_rate'].split(' ')[0]} / {t0['last_rate'].split(' ')[0]}"
        h, g = r[f"{m} hotel-only h1"], r[f"{m} either g1"]
        ah, ag = a[f"{m} h1"]["again"], a[f"{m} g1"]["again"]
        row_h = (f"| {name} | H1 | {base} | {fmt(h['first'])} | {fmt(h['last'])} | {ah[0]:,}/{ah[1]:,} "
                 f"({100 * ah[0] / ah[1]:.1f}%) |")
        row_g = (f"| {name} | G1 | {base} | {fmt(g['first'])} | {fmt(g['last'])} | {ag[0]:,}/{ag[1]:,} "
                 f"({100 * ag[0] / ag[1]:.1f}%) |")
        ok(f"Table F5 rows of {name}", has(row_h, row_g) and h["category"] == "persists" and g["category"] == "persists")
        ok(f"either = hotel-only at t0 for {name}", r[f"{m} either t0"]["first_rate"] == t0["first_rate"]
           and r[f"{m} either t0"]["last_rate"] == t0["last_rate"])
    p = res["result"]["panel"]
    ok("panel rows", has(f"| Panel | H1 | | {fmt(p['hotel-only h1 first'])} | {fmt(p['hotel-only h1 last'])} | |",
                         f"| Panel | G1 | | {fmt(p['either g1 first'])} | {fmt(p['either g1 last'])} | |",
                         f"+16.8 [+14.4, +19.2] with H1 (hotel-only) and +21.0 [+18.7, +23.4] with G1"))
    ok("Q1 to Q5 hold for every model", all(v == "holds" for q in res["result"]["predictions"].values()
                                             for v in q.values()) and len(res["result"]["predictions"]) == 5
       and has("All five predictions held"))
    ok("Q5 −6.3 [−8.9, −3.8]", res["result"]["q5"] == "-6.3 [-8.9, -3.8]" and has("−6.3 points [−8.9, −3.8]"))
    ok("F.10 results text", has("by +17.2 (Haiku), +25.5 (Sol) and +26.7 points (Luna)",
                                "+11.2 [+8.3, +14.3], +16.9 [+13.3, +20.5] and +22.5 [+19.0, +26.3]",
                                "+16.5 [+13.2, +20.3], +29.4 [+25.4, +33.9] and +17.2 [+14.0, +20.6]"))
    pct = {c: [100 * a[f"{m} {c}"]["again"][0] / a[f"{m} {c}"]["again"][1] for m in MODELS] for c in ("t0", "h1", "g1")}
    rng = {c: f"{min(v):.1f}% to {max(v):.1f}%" for c, v in pct.items()}
    ok(f"searched again: t0 {rng['t0']}, h1 {rng['h1']}, g1 {rng['g1']}",
       rng == {"t0": "0.3% to 1.3%", "h1": "8.0% to 10.9%", "g1": "5.8% to 16.6%"}
       and has("8.0% to 10.9% with H1 and 5.8% to 16.6% with G1, against 0.3% to 1.3% with the original tool",
               "was 0.3% to 1.3% with the original tool, 8.0% to 10.9% with H1 and 5.8% to 16.6% with G1"))
    ex = [(a[f"{m} h1"]["excl_again"], a[f"{m} h1"]["excl_n"]) for m in MODELS]
    ok("H1 first-search exclusions that searched again: 34 of 87, 40 of 190, 46 of 314",
       ex == [(34, 87), (40, 190), (46, 314)] and has("34 of 87 (Haiku), 40 of 190 (Sol) and 46 of 314 (Luna)"))
    last_either = [float(r[f"{m} either {c}"]["last"].split(" ")[0]) for m in MODELS for c in ("h1", "g1")]
    ok("abstract and Table 2 range 11 to 29 (last search, either type, H1 and G1)",
       (min(last_either), max(last_either)) == (11.2, 29.4)
       and has("+11.2 to +29.4 (Haiku, Sol, Luna)"))
    ok("Section 5 ranges", has("+11.2 (Haiku) to +22.5 points (Luna) with H1", "+16.5 (Haiku) to +29.4 (Sol) with G1"))
    st = res["result"]["status"]
    ok("failed conversations: Sol 8, Luna 2; at most 0.89 points",
       st["sol"].get("failed") == 8 and st["luna"].get("failed") == 2 and "failed" not in st["haiku"]
       and res["verified"]["max_points_failed"] == "0.89"
       and has("Eight Sol and two Luna conversations failed", "at most 0.89 points"))
    ok("quote rule: 118 of 1,298 calls", tuple(res["verified"]["quote_rule_calls"]) == ("118", "1,298")
       and has("118 of its 1,298 calls and one first-search score"))
    c = res["verified"]["costs"]
    ok("costs 0.39, 3.71, 0.37, 4.47 USD",
       [round(c[k], 2) for k in ("Haiku", "Sol", "Luna", "All three")] == [0.39, 3.71, 0.37, 4.47]
       and has("The search-again run cost 4.47 USD"))
    ok("control between runs: about 3 points", res["verified"]["control_between_runs"] == "about 3 points"
       and has("an unchanged control differed by about 3 points between runs"))
    ok("independent check confirms counts and predictions", res["verified"]["all_confirmed"])
    ok("old sentence removed", "We did not measure exclusion when the agent can search again" not in flat)
    print(f"{fails} failures")
    return fails


if __name__ == "__main__":
    if sys.argv[1] == "compute":
        compute()
    else:
        sys.exit(1 if check(sys.argv[2]) else 0)
