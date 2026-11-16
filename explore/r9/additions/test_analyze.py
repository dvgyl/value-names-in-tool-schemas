"""Synthetic test of zanalyze (no API call, no MultiWOZ dialogue). Usage: python3 -I r9/additions/test_analyze.py

The rows are hand-made, and each expected value below was computed by hand.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import zanalyze  # noqa: E402
import zforms  # noqa: E402
import zruns  # noqa: E402

VENUE = {h["name"]: h for h in zforms.HOTELS}
GH, HO = VENUE["acorn guest house"], VENUE["gonville hotel"]
OTHER_AREA = next(a for a in ("north", "south", "east", "west", "centre") if a != HO["area"])
G = zruns.Groups(t994=["D1.json", "D2.json", "D3.json", "D4.json"], frame500=["D1.json", "D2.json"],
                 booked=["D1.json", "D2.json", "D3.json"],
                 s1=["D1.json", "D2.json", "D3.json", "D4.json", "D5.json"], rest=["D6.json", "D7.json"],
                 s2=["D6.json", "D7.json"], venue={"D1.json": GH, "D2.json": GH, "D3.json": HO, "D6.json": HO},
                 brief={"D1.json": None, "D2.json": None, "D3.json": None, "D4.json": None, "D5.json": None,
                        "D6.json": None, "D7.json": "hotel"})
EMPTY = {"name": None, "area": None, "pricerange": None, "stars": None, "type": None, "parking": None, "internet": None}


def row(exp, d, cell, read, model, stop="end_turn", text=None, **answer):
    return {"custom_id": f"{exp}-{d}-{cell}-{read}-{model}", "type": "succeeded", "stop": stop,
            "text": text if text is not None else json.dumps({**EMPTY, **answer})}


def cells(exp, model, cell, answers):
    """One row per (dialogue, answer) in `answers`, with read numbers from 1."""
    return [row(exp, d, cell, k, model, **a) for d, many in answers.items() for k, a in enumerate(many, 1)]


H, N = {"type": ["hotel"]}, {}


def z1_rows():
    rows = cells("e13", "sonnet", "p_main", {"D1": [H], "D2": [H], "D3": [H], "D4": [N]})  # the E13 name, aliased
    rows += cells("e13", "sonnet", "p_main_renamed", {d: [N] for d in ("D1", "D2", "D3", "D4")})
    rows += cells("ez1_claude", "sonnet", "edit_f0", {"D1": [H], "D2": [N], "D3": [N], "D4": [N]})
    rows += cells("ez1_claude", "sonnet", "edit_f1", {d: [N] for d in ("D1", "D2", "D3", "D4")})
    rows += cells("ez1_claude", "sonnet", "acc_orig_f0", {"D1": [N], "D2": [H]})
    rows.append(row("ez1_claude", "D2", "edit_f0", 2, "sonnet", stop="max_tokens", **H))  # a missing cell, not a hit
    rows.append(row("ez1_claude", "D3", "edit_f0", 2, "sonnet", text="no json here"))
    return rows


def test_z1():
    out = zanalyze.analyze(z1_rows(), G)
    s = out["z1_b2"]["sonnet"]
    assert [s["t994_type_hotel"][c]["share"] for c in ("orig_f0", "orig_f1", "edit_f0", "edit_f1")] == [0.75, 0, 0.25, 0]
    assert s["did_text_x_rename"]["mean"] == 0.5 and s["did_text_x_rename"]["dialogues"] == 4
    assert s["did_text_x_rename"]["sign_test"] == {"positive": 2, "negative": 0, "p_exact": 0.5}
    assert s["share_of_rename_gap_removed_by_edit"] == 0.6667
    assert s["edit_effect_under_f0"]["mean"] == 0.5 and s["edit_effect_under_f1"]["mean"] == 0
    assert s["frame_effect_under_f0_original_text"]["mean"] == 0.5
    assert out["missing"] == {"sonnet|edit_f0": {"max_tokens": 1, "parse_fail": 1}}


def test_z2():
    rows = cells("ez2_claude", "sonnet", "pre_f0", {"D1": [H], "D2": [{"type": ["guesthouse", "hotel"]}],
                                                    "D3": [{"type": ["hotel"], "area": [OTHER_AREA]}]})
    rows += cells("e13", "sonnet", "p_main", {"D1": [N], "D2": [N], "D3": [H]})
    rows += cells("ez2_claude", "sonnet", "pre_unclear", {"D1": [{"type": "unclear"}], "D2": [N], "D3": [N]})
    for d, answers in {"D1": ["does not fix", "does not fix", "fixes"], "D2": ["fixes", "cannot tell"],
                       "D3": ["fixes"]}.items():
        rows += [row("ez2_claude", d, "pre_probe", k, "sonnet", text=json.dumps({"answer": a}))
                 for k, a in enumerate(answers, 1)]
    s = zanalyze.analyze(rows, G)["z2_b3"]["sonnet"]
    pre = s["booked554"]["pre_f0"]
    assert pre["type_hotel"]["share"] == 1.0 and pre["precision_of_type_hotel"]["share"] == 0.3333
    assert {k: v["share"] for k, v in pre["excludes_booked_type"].items()} == {"all": 0.3333, "guesthouse": 0.5,
                                                                               "hotel": 0.0}
    assert pre["excludes_booked_venue_all_fields"]["hotel"]["share"] == 1.0, "the area excludes the booked hotel"
    assert s["booked554"]["pre_unclear"]["type_unclear"]["share"] == 0.3333
    assert s["prefix_minus_full_f0_type_hotel"]["mean"] == 0.6667
    rec = s["recognition_by_commitment"]
    assert {k: v["dialogues"] for k, v in rec.items()} == {"does not fix": 1, "fixes": 1, "split": 1}
    assert rec["does not fix"]["pre_f0_type_hotel"]["share"] == 1.0
    assert rec["does not fix"]["pre_unclear_type_unclear"]["share"] == 1.0


def test_z3():
    split = {"D1": [{"type_required": None, "type_preferred": ["hotel"]}], "D2": [{"type_required": ["hotel"]}],
             "D3": [{"type_required": ["hotel"]}], "D4": [N], "D5": [N],
             "D6": [{"type_required": None, "type_preferred": ["hotel"]}], "D7": [{"type_required": ["hotel"]}]}
    rows = [row("eb4_open", d, "p_split", 1, "deepseek", **{**{k: v for k, v in EMPTY.items() if k != "type"},
                                                            "type_required": None, "type_preferred": None, **a[0]})
            for d, a in split.items()]
    rows += cells("eb4_open", "deepseek", "p_unclear_nat", {"D1": [{"type": "unclear"}], "D2": [H], "D3": [N],
                                                            "D4": [N], "D5": [N]})
    rows += cells("eb4_open", "deepseek", "p_null_nat", {d: [N] for d in ("D1", "D2", "D3", "D4", "D5")})
    rows += cells("ex2", "deepseek", "F0", {"D1": [H], "D2": [H], "D3": [N], "D4": [H], "D5": [N], "D6": [H],
                                            "D7": [N]})
    out = zanalyze.analyze(rows, G, {**zanalyze.ALIASES, "F0": "orig_f0"})["z3_b4"]["deepseek"]
    s = out["forms"]
    p = s["p_split"]
    assert p["s1_type_hotel"]["share"] == 0.4 and p["s1_type_preferred_hotel"]["share"] == 0.2
    assert p["s1_booked_excludes_type"]["share"] == 0.3333, "only type_required filters"
    assert p["kept_gold_and_booked_hotel"]["share"] == 0.0
    assert p["kept_required_or_preferred_gold_and_booked_hotel"]["share"] == 1.0
    assert p["kept_gold_and_brief_hotel"]["share"] == 1.0
    assert p["dialogues_preferred_hotel_where_f0_hotel"] == {"dialogues": 3, "share": 0.3333}
    assert s["orig_f0"]["s2_type_hotel"]["share"] == 0.5 and p["s2_kept_share_of_f0"] == 2.0
    u = s["p_unclear_nat"]
    assert u["s1_type_unclear"]["share"] == 0.2 and u["s1_booked_excludes_type"]["share"] == 0.3333
    assert out["s1_type_hotel_unclear_minus_null"]["mean"] == 0.2
    assert out["s1_type_hotel_f0_minus_form"]["p_split"]["mean"] == 0.2  # per dialogue 1, 0, -1, 1, 0
    assert set(s) == {"orig_f0", "p_split", "p_null_nat", "p_unclear_nat"}


def test_sign_and_interval():
    assert zanalyze.sign_p(5, 0) == 0.0625 and zanalyze.sign_p(0, 0) == 1.0
    e = zanalyze.analyze(z1_rows(), G)["z1_b2"]["sonnet"]["did_text_x_rename"]
    assert e["ci95"][0] <= e["mean"] <= e["ci95"][1]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
    print("zanalyze test passed")
