"""Analysis test, with no API call.

1. The copied market and parser reproduce the saved P4 (`items.json`) and P5 (`summary.json`) numbers.
2. `analyze.py` runs end to end for e1, e5, and e6 on synthetic raw.jsonl files in a temporary folder.

Usage: python3 -I test_analyze.py
"""
import collections
import json
import pathlib
import subprocess
import sys
import tempfile

FORMS_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(FORMS_DIR))
import common  # noqa: E402
from common import anth  # noqa: E402

P5_DIR = common.P4_DIR.parent / "p5_unclear"


def replicate_prototypes(data, ids, market, ambiguous, undisputed):
    items = json.loads((common.P4_DIR / "items.json").read_text())
    assert sorted({x["id"] for x in items}) == ids and len(ids) == 123, "P4 dialogue set differs"
    for x in items:
        ext = {f: tuple(v) if isinstance(v, list) else v for f, v in x["ext"].items()}
        assert market.flips(x["id"], ext) == x["flip_markets"], (x["id"], x["model"])
    table = collections.defaultdict(collections.Counter)
    for line in (P5_DIR / "raw.jsonl").read_text().splitlines():
        r = json.loads(line)
        c = table[r["model"]]
        c["n"] += 1
        try:
            ext = common.parse(r.get("text") or "")
        except (ValueError, AttributeError):
            c["parse_fail"] += 1
            continue
        c["name_given"] += bool(ext["name"])
        for f in common.FIELDS:
            if (r["id"], f) in ambiguous:
                c["amb_fields"] += 1
                c["amb_unclear"] += ext[f] == "unclear"
                c["amb_commit"] += isinstance(ext[f], tuple)
            elif (r["id"], f) in undisputed:
                c["clear_fields"] += 1
                c["clear_unclear"] += ext[f] == "unclear"
        c["flip_markets"] += market.flips(r["id"], ext)
        c["markets"] += common.MARKETS
    saved = json.loads((P5_DIR / "summary.json").read_text())
    assert {m: dict(c) for m, c in table.items()} == saved, ({m: dict(c) for m, c in table.items()}, saved)
    print(f"replication passed: {len(items)} P4 items give their saved flip markets; P5 counts equal {saved}", flush=True)


def answer(ext):
    final = {f: list(v) if isinstance(v, tuple) else v for f, v in ext.items()}
    return 'Draft: {"area": ["north"], "stars": ["0"]}\nFinal:\n' + json.dumps(final)


def row(name, dialogue, form, read, model, text="", kind="succeeded", stop="end_turn", tin=1000, tout=100):
    r = {"custom_id": common.custom_id(name, dialogue, form, read, model), "type": kind}
    if kind == "succeeded":
        r.update(model=common.MODELS[model], stop=stop, input_tokens=tin, output_tokens=tout, text=text)
    return r


def reads(name, model, forms, dialogues, n, gold, unclear_fields, tout):
    out = []
    for form in forms:
        for i in dialogues:
            for read in range(1, n + 1):
                ext = dict(gold[i])
                if common.FORMS[form].name:
                    ext["name"] = "Synthetic Lodge"
                if common.FORMS[form].unclear:
                    ext.update({f: "unclear" for f in unclear_fields.get(i, [])})
                out.append(row(name, i, form, read, model, answer(ext), tout=tout))
    return out


def write(root, name, rows):
    (root / name).mkdir()
    (root / name / "raw.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))


def analyze(root, name):
    subprocess.run([sys.executable, "-I", str(FORMS_DIR / "analyze.py"), name, "--root", str(root)], check=True)
    return json.loads((root / name / "summary.json").read_text())


def synthetic(data, ids, ambiguous, undisputed):
    a = sorted(ambiguous)[0][0]
    amb_a = [f for f in common.FIELDS if (a, f) in ambiguous]
    b, c = [i for i in ids if all((i, f) in undisputed for f in common.FIELDS)][:2]
    e5 = common.e5_ids(data)[:2]
    gold = {i: common.gold_form(data[i]) for i in [a, b, c, *e5]}
    e1 = reads("e1", "sonnet", common.FORMS, [a, b, c], 5, gold, {a: amb_a}, 100)
    e1[[r["custom_id"] for r in e1].index(common.custom_id("e1", c, "p4", 5, "sonnet"))] = row(
        "e1", c, "p4", 5, "sonnet", answer({**gold[c], "area": "unclear"}))
    e1 += [row("e1", a, "p4", 1, "haiku", kind="errored"),
           row("e1", a, "p4", 2, "haiku", stop="refusal", tout=10),
           row("e1", a, "p4", 3, "haiku", answer(gold[a]), stop="max_tokens", tout=20),
           row("e1", a, "p4", 4, "haiku", "I cannot write JSON here.", tout=30),
           row("e1", a, "p4", 5, "haiku", answer(gold[a]), tout=40)]
    e6 = reads("e6", "sonnet", ["p4", "p5"], [a, b], 3, gold, {a: amb_a}, 300)
    e5_rows = reads("e5", "opus", ["p4", "p5"], e5, 3, gold, {}, 50)

    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        for name, rows in (("e1", e1), ("e6", e6), ("e5", e5_rows)):
            write(root, name, rows)
        s1, s6, s5 = analyze(root, "e1"), analyze(root, "e6"), analyze(root, "e5")

    son = s1["cells"]["claude-sonnet-5-5"]
    n_amb = 5 * len(amb_a)
    assert son["p4_name"]["valid_reads"] == 15 and son["p4_name"]["flip_markets"] == 0, "echoed gold must not flip"
    assert son["p4_name"]["markets"] == 300 and son["p4_name"]["name_filled"] == 15 and son["p4"]["name_filled"] == 0
    assert son["p4"]["values"]["ambiguous"]["fields"] == n_amb and son["p4"]["values"]["ambiguous"]["unclear"] == 0
    assert son["p4_unclear"]["values"]["ambiguous"]["unclear"] == n_amb
    assert son["p4"]["values"]["undisputed"]["unclear"] == 1 and son["p4_unclear"]["values"]["undisputed"]["unclear"] == 0
    assert son["p4"]["values"]["undisputed"]["fields"] == 5 * (sum((a, f) in undisputed for f in common.FIELDS) + 12)
    assert son["p4"]["agreement"]["identical"] == 2 and son["p4"]["agreement"]["per_field"]["area"] == 2 / 3
    assert son["p4_name"]["agreement"]["identical"] == 3 and "name" in son["p4_name"]["agreement"]["per_field"]
    assert son["p4"]["missing_rows"] == 123 * 5 - 15 and "claude-opus-5-5" not in s1["cells"]
    assert "opus|p4" in s1["missing_cells"] and "haiku|p4_name" in s1["missing_cells"]
    k = s1["contrasts"]["claude-sonnet-5-5"]
    assert k["name_effect"]["name_rate"] == 1.0 and k["unclear_effect"]["ambiguous_unclear_rate"] == 1.0
    assert k["interaction"]["ambiguous_unclear_rate"] == 0.0 and k["interaction"]["name_rate"] == 0.0
    hk = s1["cells"]["claude-haiku-5-5"]["p4"]
    assert (hk["errors"], hk["refusals"], hk["truncations"], hk["parse_failures"], hk["valid_reads"]) == (1, 1, 1, 1, 1), hk
    assert hk["output_tokens_mean"] == 25 and hk["input_tokens_mean"] == 1000 and hk["flip_markets"] == 0
    assert hk["markets"] == 20 and hk["measures"]["identical_share"] is None
    assert set(s1["contrasts"]["claude-haiku-5-5"]) == set(), "contrasts need every form of the contrast"

    cmp6 = s6["e6_vs_e1"]["claude-sonnet-5-5"]
    assert cmp6["p4"]["output_tokens_mean"] == {"low": 100, "high": 300, "high_minus_low": 200}
    assert cmp6["p5"]["ambiguous_unclear_rate"] == {"low": 1.0, "high": 1.0, "high_minus_low": 0.0}
    assert s6["cells"]["claude-sonnet-5-5"]["p4"]["flip_markets"] == 0 and s6["e1_reads"].endswith("e1/raw.jsonl")
    assert set(s6["contrasts"]["claude-sonnet-5-5"]) == {"p5_minus_p4"}

    op = s5["cells"]["claude-opus-5-5"]
    assert op["p4"]["flip_markets"] == 0 and op["p4"]["markets"] == 120 and set(op["p4"]["values"]) == {"all_fields"}
    assert "ambiguous_list_rate" not in op["p4"]["measures"] and s5["dialogues"] == 500 and "2.1" in s5["gold"]
    assert s5["contrasts"]["claude-opus-5-5"]["p5_minus_p4"]["name_rate"] == 1.0
    print("synthetic analysis test passed for e1, e5, and e6")


def main():
    data = anth.multiwoz()
    ids = common.p4_ids(data)
    ambiguous, undisputed = common.p4_field_sets(ids)
    replicate_prototypes(data, ids, common.Market(data, ids), ambiguous, undisputed)
    e5 = common.e5_ids(data)
    val, test = anth.splits()
    assert len(e5) == 500 and not set(e5) & (val | test), "E5 set must be 500 training dialogues"
    synthetic(data, ids, ambiguous, undisputed)


if __name__ == "__main__":
    main()
