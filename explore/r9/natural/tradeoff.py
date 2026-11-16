"""Post-hoc (written 2026-11-04, after the X1 results): the trade of each form against F0 on Claude, from the shares
that natural_analyze.py prints. Expected wrong `type = hotel` values per read set = share on S1t x 994 + share on S3
x 490 (gold sets no type or `guesthouse`). Expected correct values = share on S2 x 545 (gold `hotel`).
Usage: python3 -I r9/natural/tradeoff.py logs/analysis/<natural log>
"""
import re
import sys

SIZES = {"S1t": 994, "S3": 490, "S2": 545}
share = {}
for line in open(sys.argv[1]):
    m = re.match(r"(S1t|S2|S3)\s+(\w+)\s+(f\d)\s+\d+ units\s+\d+/\s*\d+ \(\s*([\d.]+)%\)", line)
    if m:
        share[m[1], m[2], m[3]] = float(m[4]) / 100
for model in ("sonnet", "haiku", "sol", "luna"):
    if (("S2", model, "f0")) not in share:
        continue
    base = None
    print(f"{model}: form, wrong, correct, wrong removed, correct lost, correct lost per wrong removed")
    for form in ("f0", "f1", "f2", "f4", "f6"):
        if not all((g, model, form) in share for g in SIZES):
            continue
        wrong = share["S1t", model, form] * SIZES["S1t"] + share["S3", model, form] * SIZES["S3"]
        correct = share["S2", model, form] * SIZES["S2"]
        base = base or (wrong, correct)
        removed, lost = base[0] - wrong, base[1] - correct
        ratio = f"{lost / removed:.2f}" if removed > 0 else "-"
        print(f"  {form}  {wrong:6.1f}  {correct:6.1f}  {removed:6.1f}  {lost:6.1f}  {ratio}")
