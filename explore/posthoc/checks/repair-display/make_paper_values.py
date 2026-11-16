"""Every new number of the final-plan revision of the paper, formatted as the paper prints it.

Reads only the outputs of this folder (out/n3_d3_check.json, out/n1_heldout_stored.json, out/n2_gated_soft.json).
Writes out/paper_values.json (also a source for the number check) and prints the Markdown rows.
Usage (from explore/): python3 -I posthoc/checks/repair-display/make_paper_values.py
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
NAME = {"sonnet": "Sonnet", "haiku": "Haiku", "sol": "Sol", "luna": "Luna", "opus": "Opus", "astra": "Astra",
        "deepseek": "DeepSeek", "qwen": "Qwen", "gemma": "Gemma"}


def g(x):
    """A dialogue count as Table 3 prints it: integer or one decimal (no negative zero)."""
    x = 0.0 if abs(x) < 1e-12 else x
    return f"{x:.0f}" if abs(x - round(x)) < 1e-9 else f"{x:.1f}"


def signed(x):
    s = g(x)
    return s if s.startswith("-") or s == "0" else "+" + s


def interval(p):
    """Table D7 prints a difference without a plus sign (positive: the gated policy avoided fewer failures)."""
    pt, lo, hi = p
    return f"{g(pt)} [{g(lo)}, {g(hi)}]"


def pct(k, n):
    return f"{100 * k / n:.1f}%"


def main():
    n3 = json.loads((OUT / "n3_d3_check.json").read_text())
    n1 = json.loads((OUT / "n1_heldout_stored.json").read_text())["models"]
    n2 = json.loads((OUT / "n2_gated_soft.json").read_text())["models"]
    vals = {}

    # N3: guesthouse rows of Table D3 (from the planned-gate rows; the counts are the same for both gates)
    gh_rows = {}
    for x in n3["rows"]:
        if x["gate"] != "planned":
            continue
        V, K = x["V"]["S3"], x["K"]["S3"]
        row = next(r for r in n3["rows"] if r["model"] == x["model"] and r["gate"] == "clear_no")
        yes = K
        unclear = row["K"]["S3"] - K
        no = V - yes - unclear
        label = "Guesthouse"
        gh_rows[x["model"]] = {"values": V, "yes": yes, "no": no, "unclear": unclear,
                               "share_yes": pct(yes, V), "share_no": pct(no, V),
                               "md": f"| | {label} | {V} | {yes} | {no} | {unclear} | {pct(yes, V)} | {pct(no, V)} |"}
    vals["n3_d3_guesthouse_rows"] = gh_rows
    son = next(r for r in n3["rows"] if r["model"] == "sonnet" and r["gate"] == "planned")
    vals["n3_sonnet_example"] = {"removed": son["decreases"][0], "lost": son["decreases"][1],
                                 "ratio": round(son["b_exact_bases"]["ratio"], 2),
                                 "variant_a_ratio": round(son["a_no_guesthouse"]["ratio"], 2)}
    luna = next(r for r in n3["rows"] if r["model"] == "luna" and r["gate"] == "clear_no")
    vals["n3_luna_bases"] = {"n0": luna["n0"], "n1": luna["n1"]}
    vals["n3_reproduces_all_12_rows"] = n3["variant_b_reproduces_all"]

    # N1: held-out stored counts (read 1)
    M7 = list(n1)
    P = lambda m, p, k: n1[m]["policies"][p][k]  # noqa: E731
    rng = lambda xs: f"{g(min(xs))} to {g(max(xs))}"  # noqa: E731
    vals["n1"] = {
        "original_failures_NT": rng([n1[m]["original_failures_NT"] for m in M7]),
        "avoided_planned": rng([P(m, "planned", "net_avoided_NT") for m in M7]),
        "avoided_relax": rng([P(m, "relax_any", "net_avoided_NT") for m in M7]),
        "avoided_soft": rng([P(m, "soft", "net_avoided_NT") for m in M7]),
        "planned_gross_losses_H": {NAME[m]: g(P(m, "planned", "gross_losses_H")) for m in M7},
        "planned_gross_losses_H_range": rng([P(m, "planned", "gross_losses_H") for m in M7]),
        "planned_gross_losses_H_total": g(sum(P(m, "planned", "gross_losses_H") for m in M7)),
        "gross_gains_H_all_policies": sorted({P(m, p, "gross_gains_H") for m in M7 for p in ("planned", "relax_any", "soft")}),
        "symbolic_gross_losses_H": sorted({P(m, p, "gross_losses_H") for m in M7 for p in ("relax_any", "soft")}),
        "H_dialogues": {NAME[m]: n1[m]["dialogues"]["H"] for m in M7},
        "NT_dialogues": {NAME[m]: n1[m]["dialogues"]["NT"] for m in M7},
        "relax_guesthouse_stated": {NAME[m]: n1[m]["guesthouse_newly_shown_stated_H"]["relax_any"] for m in M7},
    }

    # N2: Table D7 rows and ranges
    rows, gh, calls, second, below_v = [], [], [], [], []
    for m, r in n2.items():
        Pg = r["policies"]["G"]
        flip = lambda x: [-x[0], -x[2], -x[1]]  # noqa: E731  (comparator minus gated policy: positive = fewer avoided)
        rows.append(f"| {NAME[m]} | {g(Pg['net_avoided'])} | {interval(flip(r['G_minus_verify']))} | "
                    f"{interval(flip(r['G_minus_soft']))} | {g(Pg['guesthouse_newly_shown']['stated'])} |")
        gh.append(Pg["guesthouse_newly_shown"]["stated"])
        calls.append(r["conditional_calls_share"])
        second.append(r["second_search_share"])
        below_v.append(r["G_minus_verify"][2] < 0)
    vals["n2"] = {
        "table_rows": rows,
        "guesthouse_stated_range": rng(gh),
        "conditional_calls_range": f"{100 * min(calls):.1f}% to {100 * max(calls):.1f}%",
        "second_search_range": f"{100 * min(second):.1f}% to {100 * max(second):.1f}%",
        "fewer_than_soft_whole_interval": sum(r["G_minus_soft"][2] < 0 for r in n2.values()),
        "fewer_than_verifier_point": sum(r["G_minus_verify"][0] < 0 for r in n2.values()),
        "fewer_than_verifier_whole_interval": sum(below_v),
        "fewer_than_verifier_whole_interval_models": [NAME[m] for m, b in zip(n2, below_v) if b],
        "gross_losses_H": sorted({r["policies"]["G"]["gross_losses"] for r in n2.values()}),
        "gross_gains_H": sorted({r["policies"]["G"]["gross_gains"] for r in n2.values()}),
        "avoided_range": rng([r["policies"]["G"]["net_avoided"] for r in n2.values()]),
    }
    (OUT / "paper_values.json").write_text(json.dumps(vals, indent=1))
    print(json.dumps({k: v for k, v in vals.items() if k != "n2"}, indent=1))
    print("\n".join(rows))
    print(json.dumps({k: v for k, v in vals["n2"].items() if k != "table_rows"}, indent=1))


if __name__ == "__main__":
    main()
