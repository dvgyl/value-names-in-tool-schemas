"""SPEC-N3-D3.md: does Table D3 reproduce the verifier rows of Table D1? Stored outputs only; no model call.

Usage (from explore/): python3 -I posthoc/checks/repair-display/n3_d3_check.py [master.md]
Reads r10/analysis/out/b_hotel_only.json and the printed Table D1 of the master.
Writes posthoc/checks/repair-display/out/n3_d3_check.json.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]  # explore/ of the repository
HERE = pathlib.Path(__file__).resolve().parent
STORED = ROOT / "r10/analysis/out/b_hotel_only.json"
MASTER = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "manuscript.md"  # repository copy: the manuscript is not in this repository, so this check cannot run here
SIZES = {"S1t": 994, "S3": 490, "S2": 545}
MODELS = ("sonnet", "haiku", "sol", "luna", "opus", "astra")
READS = {"haiku": 2, "luna": 2}
GATES = {"planned": ("verify", ("yes",)), "clear_no": ("verify_no_only (post hoc)", ("yes", "unclear"))}


def trade(counts, n0, n1, groups_unsupported=("S1t", "S3")):
    """counts[g] = (V, K); n0[g], n1[g] answer bases. Returns (R, L, share, ratio)."""
    R = sum((counts[g][0] / n0[g] - counts[g][1] / n1[g]) * SIZES[g] for g in groups_unsupported)
    L = (counts["S2"][0] / n0["S2"] - counts["S2"][1] / n1["S2"]) * SIZES["S2"]
    base = sum(counts[g][0] / n0[g] * SIZES[g] for g in groups_unsupported)
    return R, L, (R / base if base else None), (L / R if R > 0 else None)


def decreases(counts, r, groups_unsupported=("S1t", "S3")):
    return (sum(counts[g][0] - counts[g][1] for g in groups_unsupported) / r, (counts["S2"][0] - counts["S2"][1]) / r)


def printed_d1(md):
    """{(model, gate): (share %, (dec_unsupported, dec_supported), ratio, meets)} from the printed Table D1."""
    text = md.split("**Table D1.**", 1)[1].split("**The count fixed before the runs", 1)[0]
    out, model = {}, None
    for line in text.splitlines():
        if not line.startswith("|") or line.startswith("|---") or "Model (random" in line:
            continue
        cells = [c.strip().strip("*") for c in line.strip("|").split("|")]
        if cells[0]:
            model = cells[0].split(" (")[0].lower()
        repair = cells[1]
        if not repair.startswith("Verifier"):
            continue
        gate = "planned" if "planned" in repair else "clear_no"
        share = float(re.match(r"(-?[\d.]+)%", cells[2]).group(1))
        dec = re.findall(r"([\d.]+) − 0", cells[3])
        ratio = float(re.match(r"([\d.]+)", cells[4]).group(1))
        out[(model, gate)] = (share, (float(dec[0]), float(dec[1])), ratio, cells[5])
    return out


def run(stored, printed):
    rows, all_b, all_c, problem_a = [], True, True, False
    for m in MODELS:
        s = stored[m]
        vt = s["verify_table"]
        r = READS.get(m, 1)
        for gate, (arm, keep) in GATES.items():
            V = {g: sum(vt[f"{g}, baseline hotel only"].get(a, 0) for a in ("yes", "no", "unclear")) for g in SIZES}
            K = {g: sum(vt[f"{g}, baseline hotel only"].get(a, 0) for a in keep) for g in SIZES}
            n0 = {g: s["rates"]["f0"][g]["n"] for g in SIZES}
            n1 = {g: s["rates"][arm][g]["n"] for g in SIZES}
            identity = {g: (V[g] == s["rates"]["f0"][g]["k"], K[g] == s["rates"][arm][g]["k"]) for g in SIZES}
            counts = {g: (V[g], K[g]) for g in SIZES}
            a = trade(counts, n0, n1, ("S1t",))
            b = trade(counts, n0, n1)
            simple = {g: r * SIZES[g] for g in SIZES}
            c = trade(counts, simple, simple)
            dec = decreases(counts, r)
            st = s["trade"][arm]
            p_share, p_dec, p_ratio, p_meets = printed[(m, gate)]

            def match(x):
                return (round(100 * x[2], 1) == p_share and round(x[3], 2) == p_ratio)
            ok_dec = (round(dec[0], 1) == p_dec[0] and round(dec[1], 1) == p_dec[1])
            meets = x_meets = b[2] >= 0.5 and 0 <= b[3] <= 0.30
            ok_meets = (p_meets.startswith("yes") == x_meets)
            ok_b = match(b) and ok_dec and ok_meets
            ok_c = match(c) and ok_dec and ok_meets
            all_b &= ok_b
            all_c &= ok_c
            problem_a |= not match(a)
            rows.append({"model": m, "gate": gate, "V": V, "K": K, "n0": n0, "n1": n1, "identity": identity,
                         "a_no_guesthouse": {"R": a[0], "L": a[1], "share": a[2], "ratio": a[3]},
                         "b_exact_bases": {"R": b[0], "L": b[1], "share": b[2], "ratio": b[3]},
                         "c_simple_bases": {"R": c[0], "L": c[1], "share": c[2], "ratio": c[3]},
                         "decreases": dec, "stored": {k: st[k] for k in ("removed", "lost", "ratio", "removed_share")},
                         "printed": {"share": p_share, "decreases": p_dec, "ratio": p_ratio, "meets": p_meets},
                         "b_reproduces": ok_b, "c_reproduces": ok_c, "a_matches": match(a), "meets_point": meets})
    return {"spec": "SPEC-N3-D3.md", "problem_confirmed_variant_a": problem_a, "variant_b_reproduces_all": all_b,
            "variant_c_reproduces_all": all_c, "rows": rows}


def main():
    stored = json.loads(STORED.read_text())["models"]
    printed = printed_d1(MASTER.read_text())
    assert len(printed) == 12, printed
    res = run(stored, printed)
    out = HERE / "out" / "n3_d3_check.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(res, indent=1))
    for x in res["rows"]:
        a, b, c = x["a_no_guesthouse"], x["b_exact_bases"], x["c_simple_bases"]
        print(f"{x['model']:7} {x['gate']:9} printed {x['printed']['share']:5.1f}% {x['printed']['ratio']:.2f} | "
              f"a {100*a['share']:5.1f}% {a['ratio']:.2f} | b {100*b['share']:5.2f}% {b['ratio']:.4f} "
              f"| c {100*c['share']:5.2f}% {c['ratio']:.4f} | dec {x['decreases']} | b ok {x['b_reproduces']} "
              f"c ok {x['c_reproduces']} | id {all(all(v) for v in x['identity'].values())}")
    print("problem confirmed (a):", res["problem_confirmed_variant_a"], "| b reproduces all:",
          res["variant_b_reproduces_all"], "| c reproduces all:", res["variant_c_reproduces_all"])


if __name__ == "__main__":
    main()
