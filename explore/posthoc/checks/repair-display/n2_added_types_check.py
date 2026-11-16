"""Check for the Table D7 caption (review fix, 2026-11-16): when the gated policy widens a display, are all added
venues guesthouses? Reason: the policy acts only on a hotel-only search with fewer than five results, which already
shows every matching hotel. Same data, loaders and policy code as n2_gated_soft.py (imported, not changed).
Usage (from explore/): python3 -I posthoc/checks/repair-display/n2_added_types_check.py
"""
import collections
import importlib.util
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("n2", HERE / "n2_gated_soft.py")
n2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n2)


def main():
    F5 = n2.load_f5()
    data, g = F5.runs.context()
    db = F5.gold.hotel_db()
    ids = {k: list(g[F5.B.GROUP_KEY[k]]) for k in F5.B.SIZES}
    group_of = {d: k for k, lst in ids.items() for d in lst}
    nt = [d for d in ids["S1t"] if F5.gold.brief_type(data[d]) is None and F5.gold.brief_type(data[d], "fail_info") is None]
    h = [d for d in ids["S2"] if F5.gold.brief_type(data[d]) == "hotel"]
    G = F5.V.gots(data, group_of)
    search = lambda f: F5.bs.search(db, f)  # noqa: E731
    out = {}
    for m in n2.MODELS9:
        got = G[m]
        c = collections.Counter()
        for d in nt + h:
            for rd in F5.base_reads(got, d):
                f0 = got[(d, "f0", rd)]
                shown, _, trig, wid = n2.gated_display(search, f0, got[(d, "verify", rd)]["answer"])
                if not wid:
                    continue
                d0 = search(f0)[:5]
                c["widened_answers"] += 1
                c["hotels_in_original_equal_all_matching_hotels"] += (
                    [v["name"] for v in d0] == [v["name"] for v in search({**f0, "type": None}) if v["type"] == "hotel"])
                for v in shown[len(d0):]:
                    c["added_" + v["type"]] += 1
        out[m] = dict(c)
        print(m, dict(c), flush=True)
    (HERE / "out" / "n2_added_types_check.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
