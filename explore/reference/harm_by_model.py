"""Offline re-analysis of the round-9 reads (review of 2026-11-12). Stored answers only: no API call.

1. `type = hotel` on subsets of S1t that need no gold label: the brief names a guesthouse (the value is wrong by the
   venue data), the brief names a hotel, the brief names no venue and sets no type.
2. Search failure: the share of reads whose `type` keeps hotel and not guesthouse while no hotel fits the brief.
3. The trade of F1 and F4 against F0 with a 95% cluster bootstrap interval (dialogues resampled inside each group,
   2,000 draws, seed 20261112). Wrong = share on S1t x 994 + share on S3 x 490; correct = share on S2 x 545.
Exploratory: the analysis was chosen after the round-9 results.
Usage (from explore/): python3 -I reference/harm_by_model.py
"""
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPLORE = HERE.parent
sys.path.insert(0, str(EXPLORE / "r9" / "natural"))
sys.path.insert(0, str(EXPLORE / "r9" / "free"))
sys.path.insert(0, str(HERE))
import natural  # noqa: E402
import natural_analyze as na  # noqa: E402
import gold  # noqa: E402
from feasible_harm import fits  # noqa: E402

MODELS = ("sonnet", "haiku", "sol", "luna", "deepseek", "qwen", "gemma")
SIZES = {"S1t": 994, "S3": 490, "S2": 545}


def rate(reads, cell, units, measure):
    h = na.hits(reads, cell, units, measure)
    k, n = sum(map(sum, h.values())), sum(map(len, h.values()))
    return k, n, len(h)


def show(k, n, u):
    return f"{k}/{n} ({100 * k / n:.1f}%, {u} dialogues)" if n else "-"


def main():
    print(gold.EXPLORATORY)
    reads, _ = na.load()
    groups = natural.ids()
    data = gold.anth.multiwoz()
    db = gold.hotel_db()
    types = gold.db_types(db)
    s1t = groups["S1t"]
    info = {i: data[i]["goal"]["hotel"].get("info", {}) for i in s1t}
    free = [i for i in s1t if gold.brief_type(data[i]) is None and gold.brief_type(data[i], "fail_info") is None]
    named = {i: types.get(gold.norm(info[i]["name"]), "unmatched") for i in free if info[i].get("name")}
    u = lambda ids: {i.removesuffix(".json") for i in ids}
    subsets = {
        "brief names a guesthouse": u(i for i in named if named[i] == "guesthouse"),
        "brief names a hotel": u(i for i in named if named[i] == "hotel"),
        "brief: no type, no name": u(i for i in free if i not in named),
        "brief: no type (all)": u(free),
    }
    no_hotel_fits = u(i for i in free if not any(v["type"] == "hotel" and fits(v, info[i]) for v in db))
    print("subset sizes:", {k: len(v) for k, v in subsets.items()}, "| no hotel fits the brief:", len(no_hotel_fits))

    print("\n== 1. reads with type = hotel, F0 and F1")
    for name, units in subsets.items():
        print(name)
        for m in MODELS:
            print(f"  {m:9s} F0 {show(*rate(reads, (m, 'f0'), units, na.hotel))} | F1 {show(*rate(reads, (m, 'f1'), units, na.hotel))}")

    print("\n== 2. search failure: reads whose type hides every guesthouse while no hotel fits the brief")
    print("   (share of all reads on the dialogues whose brief sets no type)")
    for m in MODELS:
        for f in ("f0", "f1"):
            h = na.hits(reads, (m, f), subsets["brief: no type (all)"], na.hides)
            n = sum(map(len, h.values()))
            k = sum(sum(v) for d, v in h.items() if d in no_hotel_fits)
            print(f"  {m:9s} {f} {k}/{n} ({100 * k / n:.1f}%)" if n else f"  {m:9s} {f} -")

    print("\n== 3. trade against F0, 95% cluster bootstrap interval")
    rng = random.Random(20261112)
    units_of = {g: sorted(d.removesuffix(".json") for d in groups[g]) for g in SIZES}
    for m in MODELS:
        for form in ("f1", "f4"):
            cells = {}
            for g in SIZES:
                a, b = na.hits(reads, (m, "f0"), set(units_of[g]), na.hotel), na.hits(reads, (m, form), set(units_of[g]), na.hotel)
                both = sorted(set(a) & set(b))
                cells[g] = [(sum(a[d]), len(a[d]), sum(b[d]), len(b[d])) for d in both]
            if not all(cells.values()):
                continue

            def trade(sample):
                sh = {g: (sum(r[0] for r in rows) / sum(r[1] for r in rows), sum(r[2] for r in rows) / sum(r[3] for r in rows))
                      for g, rows in sample.items()}
                removed = sum((sh[g][0] - sh[g][1]) * SIZES[g] for g in ("S1t", "S3"))
                lost = (sh["S2"][0] - sh["S2"][1]) * SIZES["S2"]
                return removed, lost, lost / removed if removed > 0 else float("inf")

            point = trade(cells)
            draws = sorted(trade({g: rng.choices(rows, k=len(rows)) for g, rows in cells.items()})[2] for _ in range(2000))
            n = {g: len(rows) for g, rows in cells.items()}
            print(f"  {m:9s} {form}: wrong removed {point[0]:.1f}, correct lost {point[1]:.1f}, ratio {point[2]:.2f} "
                  f"[{draws[49]:.2f}, {draws[1949]:.2f}]; paired dialogues {n}")


if __name__ == "__main__":
    main()
