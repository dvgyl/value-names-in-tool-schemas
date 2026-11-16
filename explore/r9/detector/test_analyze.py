"""Test of the X3 and Z4 analysis (analyze.py) on synthetic rows. No data file, no API call.
Usage: python3 -I r9/detector/test_analyze.py"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import analyze  # noqa: E402

D = [f"PMUL{k:04d}.json" for k in range(10)]
SEL = {"z4_selected": True, "pairs": [
    {"id": "q01", "domain": "train", "slot": "departure", "value": "london", "neutral": "dax",
     "roles": {"x3_high": 1, "z4": 1}, "rule_b": 1.0, "x3": D, "brief_match": []},
    {"id": "q02", "domain": "restaurant", "slot": "pricerange", "value": "expensive", "neutral": "dax",
     "roles": {"x3_control": 1}, "rule_b": 0.1, "x3": D, "brief_match": D[:5]},
    {"id": "q03", "domain": "restaurant", "slot": "area", "value": "north", "neutral": "dax", "roles": {"z4": 2},
     "rule_b": 0.5, "z4": D, "brief_match": []},
    {"id": "q04", "domain": "restaurant", "slot": "area", "value": "west", "neutral": "wug", "roles": {"z4": 3},
     "rule_b": 0.2, "z4": D, "brief_match": D[:2]},
]}


def row(d, pid, variant, read, value, slot, model="sonnet", stop="end_turn"):
    text = json.dumps({slot: [value] if value else None})
    return {"custom_id": f"ez4c-{d.removesuffix('.json')}-{pid}-{variant}-{read}-{model}", "type": "succeeded",
            "stop": stop, "text": text}


def rows():
    out = []
    for k, d in enumerate(D):
        for read in (1, 2):
            out.append(row(d, "q01", "orig", read, "london", "departure"))
            out.append(row(d, "q01", "neut", read, "dax" if k < 2 else "cambridge", "departure"))
            out.append(row(d, "q02", "orig", read, "expensive", "pricerange"))
            out.append(row(d, "q02", "neut", read, "dax", "pricerange"))
            out.append(row(d, "q03", "orig", read, "north" if k < 5 else None, "area"))
            out.append(row(d, "q03", "neut", read, None, "area"))
            out.append(row(d, "q04", "orig", read, "west" if k < 1 else None, "area"))
            out.append(row(d, "q04", "neut", read, None, "area"))
    out.append(row(D[0], "q01", "orig", 3, "london", "departure", stop="max_tokens"))
    out.append(dict(row(D[0], "q01", "neut", 3, "dax", "departure"), text="not json"))
    return out


def test_stats_and_report():
    h, left = analyze.load(rows(), SEL)
    assert left == {("sonnet", "orig", "max_tokens"): 1, ("sonnet", "neut", "unparsed"): 1}, left
    s = analyze.stats(h, "sonnet", "q01", D)
    assert (s["orig"], s["neut"], round(s["drop"], 6), s["more"], s["less"]) == (1.0, 0.2, 80.0, 8, 0), s
    assert s["p"] == 2 / 2 ** 8 and s["reads"] == (20, 20)
    s = analyze.stats(h, "sonnet", "q02", D)
    assert (s["drop"], s["more"], s["less"], s["p"]) == (0.0, 0, 0, 1.0), "the neutral value maps back"
    lines = []
    analyze.report(h, SEL, "X3", ("sonnet",), lines.append)
    assert sum("prediction" in x and "holds" in x for x in lines) == 2, lines
    assert any("over 2 pairs: -" in x for x in lines), "no correlation from 2 points"
    lines = []
    rho = analyze.report(h, SEL, "Z4", ("sonnet", "haiku"), lines.append)
    assert abs(rho["sonnet"] - 1.0) < 1e-12 and rho["haiku"] is None, rho
    assert any("q04" in x and "brief sets value (2) +50.0, other +0.0" in x for x in lines), lines


def test_spearman():
    assert analyze.spearman([1, 1, 0], [2, 1, 0]) == 1.5 / 3 ** 0.5
    assert analyze.spearman([3, 2, 1], [1, 2, 3]) == -1.0
    assert analyze.ranks([5, 1, 5, 3]) == [3.5, 1.0, 3.5, 2.0]
    assert analyze.spearman([1, 2], [1, 2]) is None and analyze.spearman([1, 1, 1], [1, 2, 3]) is None


if __name__ == "__main__":
    test_stats_and_report()
    test_spearman()
    print("test_analyze (X3, Z4): all 2 tests pass")
