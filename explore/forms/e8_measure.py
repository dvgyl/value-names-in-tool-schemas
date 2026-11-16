"""The main E8 measure (PROTOCOL.md): `type = hotel` reads on dialogues that say "hotel" and whose gold sets no type.

Usage: python3 -I e8_measure.py [base experiment] [renamed experiment]   (default: e5 e8)
The rule that counts the word in the traveller's turns only was fixed at analysis time; the all-turns rule is the check.
"""
import collections
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import anth  # noqa: E402

WORD = re.compile(r"\bhotels?\b", re.I)


def subset(data, ids, traveller_only):
    def says_hotel(d):
        return any(WORD.search(t["text"]) for k, t in enumerate(d["log"]) if k % 2 == 0 or not traveller_only)
    return {i for i in ids if common.gold_form(data[i])["type"] is None and says_hotel(data[i])}


def hits(experiments, chosen):
    out = collections.defaultdict(lambda: collections.defaultdict(list))
    for e in experiments:
        for line in open(anth.EXPLORE / e / "raw.jsonl"):
            r = json.loads(line)
            _, d, form, _, model = common.split_custom_id(r["custom_id"])
            if d not in chosen or r["type"] != "succeeded" or r.get("stop") != "end_turn":
                continue
            try:
                v = common.parse(r["text"])["type"]
            except (ValueError, KeyError):
                continue
            out[(model, form)][d].append(isinstance(v, tuple) and "hotel" in v)
    return out


def sign_test(a, b):
    more = sum(1 for d in a if d in b and sum(a[d]) / len(a[d]) > sum(b[d]) / len(b[d]))
    less = sum(1 for d in a if d in b and sum(a[d]) / len(a[d]) < sum(b[d]) / len(b[d]))
    n = more + less
    p = min(1.0, 2 * sum(math.comb(n, k) for k in range(min(more, less) + 1)) / 2 ** n) if n else 1.0
    return more, less, p


def main(base="e5", renamed="e8"):
    data = anth.multiwoz()
    ids = common.dialogue_ids(base, data)
    for label, traveller_only in (("traveller turns", True), ("all turns", False)):
        chosen = subset(data, ids, traveller_only)
        h = hits((base, renamed), chosen)
        print(f"== {label}: {len(chosen)} of {len(ids)} dialogues")
        forms = sorted({f for _, f in h if not f.endswith("_renamed")})
        for model in ("haiku", "sonnet", "opus"):
            for f in forms:
                a, b = h[(model, f)], h[(model, f + "_renamed")]
                ra = sum(map(sum, a.values())), sum(map(len, a.values()))
                rb = sum(map(sum, b.values())), sum(map(len, b.values()))
                more, less, p = sign_test(a, b)
                print(f"{model:7} {f:4} {ra[0]:4d}/{ra[1]:4d} ({100 * ra[0] / ra[1]:5.1f}%)  renamed {rb[0]:4d}/{rb[1]:4d} "
                      f"({100 * rb[0] / rb[1]:5.1f}%)  dialogues {more} to {less}, exact p = {p:.2g}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
