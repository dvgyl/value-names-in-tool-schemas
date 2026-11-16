"""the paper, final 5: the Track I values for Appendix H (Table H1 with two decimals, Table H2 per word).

No model call, no network call. It reads only the stored output of the frozen registered analysis
(main/exp1/track_i.json). It opens no answer folder, no sealed file and no key file.

Status of the values:
- Table H1: the five registered contrasts, as the frozen analysis wrote them; only the rounding is new
  (two decimals, in points).
- Table H2: the rate of the registered secondary outcome "unsupported commitment" (a valid answer states a
  condition, organization and attribute, that the correct answer does not state), for the text with the word,
  under the original schema (a_legacy) and the renamed schema (b_renamed). The frozen analysis wrote these
  rates as description, with no test.

Usage (from explore/):
  python3 -I r10/analysis/loyal_tracki_tables.py
It writes r10/analysis/out/loyal_tracki_tables.json and .md.
This file is a copy of the project script loyal_final5_tracki.py with the paths of the study folder; the values are the same,
and only the source path in the outputs differs.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]  # explore/
SRC = ROOT / "main/exp1/track_i.json"
OUT = pathlib.Path(__file__).resolve().parent / "out"
WORDS = [("onsite", "on-site"), ("north", "north"), ("retail", "retail"), ("large", "large")]


def pts(x):
    return round(100 * x, 2)


def main():
    res = json.loads(SRC.read_text())["results"]
    h1 = []
    for t in res["part1_family"]["tests"]:
        lo, hi = t["ci95"]
        h1.append({"number": t["number"], "contrast": t["contrast"], "mean_points": pts(t["mean"]),
                   "ci95_points": [pts(lo), pts(hi)], "p_holm": round(t["p_holm"], 3),
                   "direction": t["direction"]})
    rates = res["part6_rates"]["words"]
    h2 = []
    for key, word in WORDS:
        row = {"word": word}
        for variant in ("a_legacy", "b_renamed"):
            c = rates[key][f"{variant} collision"]["unsupported_commitment"]
            row[variant] = {"k": c["k"], "n": c["n"], "share_pct": round(100 * c["k"] / c["n"], 1)}
        h2.append(row)
    out = {"source": str(SRC.relative_to(ROOT)), "table_h1": h1, "table_h2": h2}
    OUT.mkdir(exist_ok=True)
    (OUT / "loyal_tracki_tables.json").write_text(json.dumps(out, indent=1))

    def sgn(v):
        return f"{v:+.2f}".replace("+0.00", "0.00").replace("-0.00", "0.00")

    md = ["# the paper final 5: Track I values for Appendix H", "",
          f"Source: `{out['source']}` (stored output of the frozen registered analysis).", "",
          "## Table H1 (two decimals, points)", "",
          "| # | Contrast | Mean | 95% interval | Holm p | Direction |", "|---|---|---|---|---|---|"]
    for r in h1:
        lo, hi = r["ci95_points"]
        md.append(f"| {r['number']} | {r['contrast']} | {r['mean_points']:.2f} | [{sgn(lo)}, {sgn(hi)}] | "
                  f"{r['p_holm']:.3f} | {r['direction']} |")
    md += ["", "## Table H2 (unsupported commitment, text with the word; description, no test)", "",
           "| Word | Original schema (a_legacy) | Renamed schema (b_renamed) |", "|---|---|---|"]
    for r in h2:
        a, b = r["a_legacy"], r["b_renamed"]
        md.append(f"| {r['word']} | {a['k']} of {a['n']} ({a['share_pct']:.1f}%) | "
                  f"{b['k']} of {b['n']} ({b['share_pct']:.1f}%) |")
    (OUT / "loyal_tracki_tables.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
