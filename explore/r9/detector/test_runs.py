"""Tests of the X3 and Z4 forms and request builders. It loads data.json (about one minute) and makes no API call.

1. The domain template, given the hotel fields, gives the E13 `p_main` prompt and schema.
2. For each selected pair, the neutral form changes only the pair value, in the prompt and in the schema.
3. The parser maps the neutral value back, and does not count an original value that the neutral form does not offer.
4. Each X3 run has the count per model of review/plan13/r9_counts.py --balance (Z4: 120 per new pair, amendment 1),
   the E13 Claude settings, the planned GPT and DeepInfra settings, and no validation, test, or Track P dialogue.
Usage: python3 -I r9/detector/test_runs.py
"""
import copy
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import runs  # noqa: E402
import forms  # noqa: E402
import common  # noqa: E402
from common import anth  # noqa: E402

sys.path.insert(0, str(runs.EXPLORE / "pmain"))
import e13  # noqa: E402

COUNTS = runs.EXPLORE.parents[1] / "review" / "plan13" / "r9_counts.py"
LONG = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5", "luna": "gpt-6-luna", "sol": "gpt-6.1-sol",
        "deepseek": "DeepSeek-V4.1-Flash", "qwen": "Qwen3.8-27B", "gemma": "gemma-4-31B-it"}


def test_template_is_p_main():
    hotel = forms.Domain("a hotel booking assistant", "hotel", True, e13.VALUES)
    assert forms.system_text(hotel, e13.VALUES) == common.FORMS["p_main"].system
    assert forms.schema(hotel, e13.VALUES) == e13.schema(False)["schema"]


def changed_span(a, b):
    """The words of a and of b between the first and the last word where they differ."""
    a, b = a.split(), b.split()
    i = next(k for k in range(min(len(a), len(b))) if a[k] != b[k])
    j = next(k for k in range(1, min(len(a), len(b))) if a[-k] != b[-k])
    return " ".join(a[i:len(a) - j + 1]), " ".join(b[i:len(b) - j + 1])


def test_neutral_form_changes_only_the_value():
    sel = runs.selection()
    for p in sel["pairs"]:
        o, n = runs.pair_form(p, "orig"), runs.pair_form(p, "neut")
        span = changed_span(o.system, n.system)
        assert span in ((p["value"] + ",", p["neutral"] + ","), (p["value"] + ".", p["neutral"] + ".")), (p["id"], span)
        assert o.system.count(f" {p['slot']}: ") == 1
        so, sn = copy.deepcopy(o.schema), copy.deepcopy(n.schema)
        items_o, items_n = (s["properties"][p["slot"]]["anyOf"][2]["items"]["enum"] for s in (so, sn))
        k = items_o.index(p["value"])
        assert items_n[k] == p["neutral"] and p["value"] not in items_n
        items_n[k] = p["value"]
        assert so == sn, f"{p['id']}: the schemas differ outside the pair value"
        assert o.token == p["value"] and n.token == p["neutral"]
    departure = next(p for p in sel["pairs"] if p["domain"] == "train" and p["slot"] == "departure")
    f = runs.pair_form(departure, "neut")
    assert f.schema["properties"]["destination"]["anyOf"][2]["items"]["enum"] == forms.STATIONS, \
        "the other station field keeps its values"


def test_parse_maps_back():
    o = forms.form("train", "departure", "london")
    n = forms.form("train", "departure", "london", "dax")
    text = json.dumps({"departure": ["dax"], "destination": None, "day": "any", "leaveat": ["10:15"], "arriveby": None})
    got = forms.parse("reasoning text {\"a\": 1} " + text, n)
    assert got == {"departure": ("london",), "destination": None, "day": "any", "leaveat": ("10:15",), "arriveby": None}
    assert forms.holds(got, n) and forms.holds(forms.parse(text.replace("dax", "london"), o), o)
    assert not forms.holds(forms.parse(text.replace("dax", "london"), n), n), "london is not offered by the neutral form"
    assert not forms.holds(forms.parse(text.replace('["dax"]', '"any"'), n), n)
    r = forms.form("restaurant", "pricerange", "expensive", "dax")
    got = forms.parse(json.dumps({"name": "", "food": ["Chinese"], "pricerange": ["DAX", "cheap"], "area": None}), r)
    assert got["name"] is None and got["food"] == ("chinese",) and got["pricerange"] == ("expensive", "cheap")


def r9_counts():
    out = subprocess.run([sys.executable, "-I", str(COUNTS), "--balance"], capture_output=True, text=True, check=True)
    lines = [ln for ln in out.stdout.splitlines() if ln.startswith("|")]
    head = [c.strip() for c in lines[0].strip("|").split("|")]
    table = {}
    for ln in lines[2:]:
        cells = [c.strip() for c in ln.strip("|").split("|")]
        table[cells[0].strip("`")] = {h: int(c.replace(",", "") or 0) for h, c in zip(head[1:], cells[1:])}
    return table


def test_runs(data):
    sel, counts = runs.selection(), r9_counts()
    val, test = anth.splits()
    for exp, run in runs.RUNS.items():
        reqs = runs.build(exp, data, sel)
        new_z4 = sum(len(p.get("z4", [])) for p in sel["pairs"])
        for short, reads in run.reads.items():
            mine = sum(r["custom_id"].endswith(f"-{short}") for r in reqs)
            want = counts[LONG[short]]["X3"] if exp.startswith("ex3") else new_z4 * 2 * reads  # Z4: amendment 1
            assert mine == want, (exp, short, mine, want)
        ids = [r["custom_id"] for r in reqs]
        assert len(ids) == len(set(ids)) and all(len(i) <= 64 and re.fullmatch(r"[A-Za-z0-9_-]+", i) for i in ids)
        fs = {(p["id"], v): runs.pair_form(p, v) for p in sel["pairs"] for v in runs.VARIANTS}
        for r in reqs:
            _, d, pid, variant, read, short = runs.split_custom_id(r["custom_id"])
            assert d not in val | test
            f, m = fs[pid, variant], runs.MODELS[short]
            body = r.get("params") or r["body"]
            user = body["messages"][-1]["content"] if "messages" in body else body["input"][-1]["content"]
            assert user == common.dialogue_text(data[d])
            if m.provider == "anthropic":
                thinking, effort = e13.SETTINGS[short]
                assert body["system"] == f.system and body["output_config"] == {
                    "effort": effort, "format": {"type": "json_schema", "schema": f.schema}}
                assert body["thinking"] == thinking and body["max_tokens"] == e13.MAX_TOKENS and "temperature" not in body
            elif m.provider == "openai":
                assert body["input"][0] == {"role": "system", "content": f.system} and "temperature" not in body
                assert body["reasoning"] == {"effort": {"luna": "none", "sol": "low"}[short]}
                assert body["text"]["format"]["schema"] == f.schema and body["max_output_tokens"] == 4000
            else:
                assert body["messages"][0] == {"role": "system", "content": f.system}
                assert body["response_format"]["json_schema"]["schema"] == f.schema
                assert body == runs.ds.request(runs.ds.MODELS[m.model], r["custom_id"], user, f.system, f.schema)["body"]
        di = {p["id"]: p for p in sel["pairs"]}
        if exp == "ex3d":
            assert all(set(di[i]["x3_deepinfra"]) <= set(di[i]["x3"]) for i in di if "x3" in di[i])
    bad = copy.deepcopy(sel)
    bad["pairs"][0]["x3"][0] = sorted(val)[0]
    try:
        runs.build("ex3c", data, bad)
    except AssertionError as e:
        assert "validation or test" in str(e)
    else:
        raise AssertionError("a validation dialogue passed the builder")


def test_selection_file():
    sel = runs.selection()
    x3 = [p for p in sel["pairs"] if "x3" in p]
    assert sum(len(p["x3"]) for p in x3) == 1200 and sum(len(p["x3_deepinfra"]) for p in x3) == 600
    z4 = [p for p in sel["pairs"] if "z4" in p["roles"]]
    assert len(z4) == 16 and all(len(p["z4"] if "z4" in p else p["x3"][:120]) == 120 for p in z4), "120 instances per Z4 pair"
    assert all(("z4" in p) != ("x3" in p) for p in z4), "a Z4 pair that X3 reads gets no new instances"
    assert all(p["x3_deepinfra"] == p["x3"][:len(p["x3_deepinfra"])] for p in x3), "the DeepInfra instances are a prefix"


if __name__ == "__main__":
    test_template_is_p_main()
    test_neutral_form_changes_only_the_value()
    test_parse_maps_back()
    test_selection_file()
    test_runs(anth.multiwoz())
    print("test_runs: all 5 tests pass")
