"""Tests of the round-9 natural forms, groups, requests, and analysis. No API call.

Usage: python3 -I r9/natural/test_natural.py
"""
import collections
import difflib
import json
import pathlib
import re
import subprocess
import sys
import tempfile
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import natural as n  # noqa: E402
import natural_analyze as na  # noqa: E402

COUNTS = n.EXPLORE.parents[1] / "review" / "plan13" / "r9_counts.py"
SHORT = {"claude-haiku-5-5": "haiku", "claude-sonnet-5-5": "sonnet", "gpt-6.1-sol": "sol", "gpt-6-luna": "luna",
         "DeepSeek-V4.1-Flash": "deepseek", "Qwen3.8-27B": "qwen", "gemma-4-31B-it": "gemma"}
# The only edits of each form against F0, as (old words, new words), in the prompt and in the schema.
TEXT_EDITS = {
    "f0": [],
    "f1": [("type", "property_kind"), ("type", "property_kind"), ("hotel", "large_property")],
    "f2": [("hotel", "large_property")],
    "f3": [("type", "property_kind"), ("type", "property_kind")],
    "f4": [("hotel", "serviced_property")],
    "f5": [("area", "district"), ("pricerange", "price_band"), ("area", "district"), ("pricerange", "price_band")],
    "f6": [("hotel", "category_A ( any venue type that is not a guesthouse )")],
}
SCHEMA_EDITS = {
    "f0": [],
    "f1": [(['"type": {'], ['"property_kind": {']), (['"hotel"'], ['"large_property"']), (['"type",'], ['"property_kind",'])],
    "f2": [(['"hotel"'], ['"large_property"'])],
    "f3": [(['"type": {'], ['"property_kind": {']), (['"type",'], ['"property_kind",'])],
    "f4": [(['"hotel"'], ['"serviced_property"'])],
    "f5": [(['"area": {'], ['"district": {']), (['"pricerange": {'], ['"price_band": {']),
           (['"area",', '"pricerange",'], ['"district",', '"price_band",'])],
    "f6": [(['"hotel"'], ['"category_A"'])],
}
SIZE_OR_QUALITY = {"large", "small", "big", "little", "tiny", "huge", "grand", "mini", "major", "minor", "luxury",
                   "luxurious", "premium", "budget", "cheap", "expensive", "deluxe", "superior", "basic", "fancy", "posh",
                   "upscale", "boutique", "quality", "standard", "economy", "elite", "best", "top", "fine", "high", "low"}


def edits(a, b, split):
    a, b = split(a), split(b)
    return [(a[i1:i2], b[j1:j2]) for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
            if op != "equal"]


def words(s):
    return re.findall(r"\w+|[^\w\s]", s)


def check_forms():
    for group in ("S1", n.TRACKC):
        prompt, fmt = n.base(group)
        assert n.system(prompt, n.FORMS["f0"]) == prompt and n.schema(fmt, n.FORMS["f0"]) == fmt
        for name, form in n.FORMS.items():
            got = [(" ".join(x), " ".join(y)) for x, y in edits(prompt, n.system(prompt, form), words)]
            assert got == TEXT_EDITS[name], (group, name, got)
            lines = lambda f: json.dumps(f["schema"], indent=0).splitlines()
            assert edits(fmt, n.schema(fmt, form), lines) == SCHEMA_EDITS[name], (group, name)
    natural_prompt, natural_fmt = n.base("S1")
    assert n.system(natural_prompt, n.FORMS["f1"]) == n.common.FORMS["p_main_renamed"].system, "F1 is not the E13 renamed form"
    assert json.dumps(n.schema(natural_fmt, n.FORMS["f1"])) == json.dumps(n.e13.schema(True)), "F1 schema is not E13's"
    assert json.dumps(n.base(n.TRACKC)[1]) == json.dumps(natural_fmt), "the E14 and E13 p_main schemas differ"
    print("forms: each form changes only its named tokens; F0 and F1 equal E13 p_main and p_main_renamed")


def check_parse():
    def text(**fields):
        return "noise {" + json.dumps({"name": None, **fields})[1:]
    cases = {"f0": text(type=["hotel"]), "f1": text(property_kind=["large_property"]),
             "f2": text(type=["Large Property"]), "f3": text(property_kind=["hotel"]),
             "f4": text(type=["serviced_property", "guesthouse"]), "f6": text(type="category_a"),
             "f5": text(district=["north"], price_band=["cheap"], type=["hotel"])}
    for name, t in cases.items():
        got = n.parse(t, n.FORMS[name])
        assert got["type"] and "hotel" in got["type"], (name, got)
    assert n.parse(cases["f5"], n.FORMS["f5"])["area"] == ("north",)
    assert n.parse(cases["f5"], n.FORMS["f5"])["pricerange"] == ("cheap",)
    assert n.parse(cases["f4"], n.FORMS["f4"])["type"] == ("hotel", "guesthouse")
    assert n.parse(text(type="any"), n.FORMS["f2"])["type"] == "any"
    assert n.parse(text(type=["large_property"]), n.FORMS["f0"])["type"] == ("large_property",), "F0 must not map back"
    for line in list(open(n.EXPLORE / "e13" / "raw.jsonl"))[:400]:
        r = json.loads(line)
        form = "f1" if "renamed" in r["custom_id"] else "f0"
        assert n.parse(r["text"], n.FORMS[form]) == n.common.parse(r["text"]), r["custom_id"]
    print("parse: every form maps back to the original fields and values; F0 and F1 equal common.parse on E13 rows")


def check_ids(data):
    assert n.compute_ids(data) == n.ids(), "ids.json differs from the rule"
    assert json.loads(n.IDS.read_text())["seed"] == n.SEED
    print("ids: ids.json equals the rule (S1 1,136, S1t 994, S2 545, S3 490, S4 423, S5 280; certified 293 and 233)")


def check_neutral(data):
    val, test = n.anth.splits()
    turns = [t["text"] for k, d in data.items() if k not in val | test for i, t in enumerate(d["log"]) if i % 2 == 0]
    found = {}
    for token in ("serviced_property", "full_service"):
        phrase = re.compile(r"\b" + token.replace("_", "[ _-]?") + r"s?\b", re.I)
        parts = token.split("_")
        found[token] = (sum(1 for t in turns if phrase.search(t)),
                        "hotel" in token.lower(), sorted(set(parts) & SIZE_OR_QUALITY))
    passes = lambda tok: found[tok][0] == 0 and not found[tok][1] and not found[tok][2]
    assert n.NEUTRAL == ("serviced_property" if passes("serviced_property") else "full_service") and passes(n.NEUTRAL)
    print(f"neutral token: {n.NEUTRAL}; (traveller turns, has hotel, size or quality words) = {found}")


def r9_counts():
    out = subprocess.run([sys.executable, "-I", str(COUNTS), "--balance"], capture_output=True, text=True, check=True).stdout
    lines = [l for l in out.splitlines() if l.startswith("| `")]
    runs = [c.strip() for c in out.splitlines()[0].split("|")[2:-2]]
    table = {}
    for l in lines:
        cells = [c.strip() for c in l.split("|")[1:-1]]
        table[SHORT.get(cells[0].strip("`"))] = {r: int(c.replace(",", "") or 0) for r, c in zip(runs, cells[1:])}
    return table


def check_requests(data):
    groups, built = n.ids(), {}
    for name in n.EXPERIMENTS:
        built[name] = n.requests(name, data, groups)
    calls = collections.defaultdict(collections.Counter)
    for name, reqs in built.items():
        exp = n.EXPERIMENTS[name]
        cells = [n.anth.cell(r) if "params" in r else n.oc.cell(r) for r in reqs]
        models = collections.Counter(c[0] for c in cells)
        for model_id, k in models.items():
            short = next(s for s, m in n.MODELS.items() if m.id == model_id)
            calls[exp.run][short] += k + (min(n.anth.PILOT_PER_CELL, k) if exp.pilot else 0)
    table = r9_counts()
    for short in ("haiku", "sonnet"):
        assert calls["X1"][short] == table[short]["X1"], (short, calls["X1"][short], table[short]["X1"])
    for short in ("sol", "luna", "deepseek", "qwen", "gemma"):
        assert calls["B1"][short] == table[short]["B1"], (short, calls["B1"][short], table[short]["B1"])
    # X2 also holds other builders' parts, so the natural terms of r9_counts.py are written out here.
    s1, rest, spec = 1136, 1738, 600
    natural_x2 = {"sol": s1 * 3 + spec * 3, "luna": (s1 + rest) * 3 * 3, "deepseek": s1 * 2, "qwen": s1 * 2, "gemma": s1 * 2}
    assert dict(calls["X2"]) == natural_x2, dict(calls["X2"])
    assert all(natural_x2[m] <= table[m]["X2"] for m in natural_x2)
    print("counts per run and model: " + "; ".join(f"{run} " + ", ".join(f"{m} {k:,}" for m, k in sorted(c.items()))
                                                    for run, c in sorted(calls.items())))
    return built


def body(r):
    return r["params"] if "params" in r else r["body"]


def check_request_content(data, built):
    pool, (val, test) = n.anth.trackp_pool(data), n.anth.splits()
    item_text = {it.id.replace("-", "_"): it.text for it in n.templates.items() if it.condition == "a"}
    expect = {(g, f): (n.system(n.base(g)[0], form), n.schema(n.base(g)[1], form))
              for g in ("S1", n.TRACKC) for f, form in n.FORMS.items()}
    for name, reqs in built.items():
        for r in reqs:
            exp, unit, form, read, short = r["custom_id"].split("-")
            assert exp == name and form in n.FORMS
            b, m = body(r), n.MODELS[short]
            group = n.TRACKC if unit.startswith("xa_") else "S1"
            prompt, fmt = expect[(group, form)]
            user = item_text[unit] if group == n.TRACKC else n.common.dialogue_text(data[unit + ".json"])
            assert group == n.TRACKC or (unit + ".json" not in pool and unit + ".json" not in val | test)
            msgs = b.get("messages") or b.get("input")
            if m.provider == "anthropic":
                assert (b["system"], msgs[-1]["content"]) == (prompt, user)
                assert b["output_config"] == {"effort": m.effort, "format": fmt}
                assert (b["thinking"], b["max_tokens"]) == (m.thinking, 4096)
                continue
            assert msgs == [{"role": "system", "content": prompt}, {"role": "user", "content": user}]
            if m.provider == "openai":
                assert b["text"]["format"]["schema"] == fmt["schema"] and b["text"]["format"]["strict"]
                assert (b["reasoning"], b["max_output_tokens"]) == ({"effort": m.effort}, 4000) and "temperature" not in b
            else:
                assert b["response_format"]["json_schema"]["schema"] == fmt["schema"]
                assert b == n.ds.request(n.ds.MODELS[m.id], r["custom_id"], user, prompt, fmt["schema"])["body"]
    print("request content: every request holds its form's prompt and schema, the panel settings, and no Track P, "
          "validation, or test dialogue")


def check_reuse(built):
    """The F0 drift reads repeat E13 p_main, and the Sonnet Track C F0 reads repeat E14 p_main, byte for byte."""
    e13 = {(c.split("-")[1], c.split("-")[4], c.split("-")[3]): r["params"] for r in n.e13.build()
           for c in [r["custom_id"]] if c.split("-")[2] == "p_main"}
    drift = [r for r in built["ex1_s1"] if r["custom_id"].split("-")[2] == "f0"]
    assert len(drift) == 228 * 3 * 2
    for r in drift:
        _, unit, _, read, short = r["custom_id"].split("-")
        assert json.dumps(r["params"]) == json.dumps(e13[(unit, short, read)]), r["custom_id"]
    e14 = {r["custom_id"].removeprefix("e14-").rsplit("-", 2)[0]: r["params"] for r in n.e14.build()
           if r["custom_id"].endswith("-r1-sonnet")}
    tc = [r for r in built["ex1_tc"] if r["custom_id"].split("-")[2] == "f0"]
    assert len(tc) == 80 * 4 and {r["custom_id"].split("-")[3] for r in tc} == {"3", "4", "5", "6"}
    for r in tc:
        unit = r["custom_id"].split("-")[1]
        assert json.dumps(r["params"]) == json.dumps(e14[unit.replace("_", "-") + "-p_main"]), r["custom_id"]
    print("reuse: the drift requests equal E13 p_main, and the Track C F0 requests equal E14 p_main")


def check_pilot_guard():
    for name, exp in n.EXPERIMENTS.items():
        if exp.pilot:
            continue
        with mock.patch.object(sys, "argv", [f"{name}.py", "pilot"]):
            try:
                n.main(name)
            except SystemExit as e:
                assert "counts no pilot calls" in str(e)
            else:
                raise AssertionError(f"{name} ran its pilot step")
    print("pilot guard: only the X1 folders accept the pilot step")


def row(cid, text=None, stop="end_turn", kind="succeeded"):
    return {"custom_id": cid, "type": kind, "stop": stop, "text": text}


def t(value, key="type"):
    return json.dumps({"name": None, "area": None, key: value})


def check_analysis():
    rows = {
        "e13": [row(f"e13-U1-p_main-{r}-sonnet", t(["hotel"])) for r in (1, 2, 3)]
        + [row("e13-U2-p_main-1-sonnet", t(["hotel"])), row("e13-U2-p_main-2-sonnet", t(None)),
           row("e13-U2-p_main-3-sonnet", t(None))]
        + [row(f"e13-U3-p_main-{r}-sonnet", t(["guesthouse", "hotel"])) for r in (1, 2, 3)]
        + [row("e13-U1-p_main_renamed-1-sonnet", t(["large_property"], "property_kind"))]
        + [row(f"e13-U1-p_main_renamed-{r}-sonnet", t(None, "property_kind")) for r in (2, 3)]
        + [row(f"e13-U2-p_main_renamed-{r}-sonnet", t(None, "property_kind")) for r in (1, 2, 3)]
        + [row(f"e13-U3-p_main_renamed-{r}-sonnet", t(["guesthouse", "large_property"], "property_kind")) for r in (1, 2, 3)],
        "ex1_s1": [row(f"ex1_s1-U1-f2-{r}-sonnet", t(["large_property"])) for r in (1, 2, 3)]
        + [row("ex1_s1-U2-f2-1-sonnet", t(["Large Property"])), row("ex1_s1-U2-f2-2-sonnet", t(["hotel"]), "max_tokens"),
           row("ex1_s1-U2-f2-3-sonnet", None, None, "errored")]
        + [row(f"ex1_s1-U3-f2-{r}-sonnet", t(["guesthouse"])) for r in (1, 2, 3)]
        + [row(f"ex1_s1-U1-f0-{r}-sonnet", t(None)) for r in (1, 2, 3)],
        "ex1_grp": [row(f"ex1_grp-V1-f0-{r}-haiku", t(["hotel"])) for r in (1, 2, 3)]
        + [row("ex1_grp-V2-f0-1-haiku", t(["hotel"])), row("ex1_grp-V2-f0-2-haiku", t(["hotel"])),
           row("ex1_grp-V2-f0-3-haiku", t(["guesthouse"]))]
        + [row(f"ex1_grp-V1-f4-{r}-haiku", t(["serviced_property"])) for r in (1, 2, 3)]
        + [row(f"ex1_grp-V2-f4-{r}-haiku", t(None)) for r in (1, 2)] + [row("ex1_grp-V2-f4-3-haiku", "no json here")],
        "eb1_luna": [row("eb1_luna-V1-f5-1-luna", json.dumps({"district": ["north"], "price_band": None, "type": ["hotel"]})),
                     row("eb1_luna-V1-f6-1-luna", t(["category_A"]))],
        "e14": [row("e14-xa-g00-amb-p_main-r1-sonnet", t(["hotel"])), row("e14-xa-g00-amb-p_null-r1-sonnet", t(["hotel"])),
                row("e14-xb-g00-amb-p_main-r1-sonnet", t(["hotel"]))],
    }
    groups = {"S1t": ["U1.json", "U2.json", "U3.json"], "S2": ["V1.json", "V2.json"], "drift": ["U1.json"],
              "S1t_booked_guesthouse": ["U1.json", "U2.json"], "S1t_booked_hotel": ["U3.json"],
              "S1t_booked_none": [], "S1t_booked_unmatched": []}
    with tempfile.TemporaryDirectory() as tmp:
        for name, rs in rows.items():
            (pathlib.Path(tmp) / name).mkdir()
            (pathlib.Path(tmp) / name / "raw.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rs))
        reads, invalid = na.load(tmp)
    units_of = na.group_units(groups)
    shares = {(g, m, f): (k, total) for g, m, f, _, k, total in na.shares(reads, units_of)}
    assert shares == {("S1t", "sonnet", "f0"): (7, 9), ("S1t", "sonnet", "f1"): (4, 9), ("S1t", "sonnet", "f2"): (4, 7),
                      ("S1t", "sonnet", "f0_drift"): (0, 3), ("S2", "haiku", "f0"): (5, 6), ("S2", "haiku", "f4"): (3, 5),
                      ("S2", "luna", "f5"): (1, 1), ("S2", "luna", "f6"): (1, 1), ("drift", "sonnet", "f0"): (3, 3),
                      ("drift", "sonnet", "f0_drift"): (0, 3), ("tc_amb", "sonnet", "f0"): (1, 1)}, shares
    assert invalid == {("sonnet", "f2"): 2, ("haiku", "f4"): 1}, invalid
    signs = {(g, m, f): rest for g, m, f, *rest in na.signs(reads, units_of)}
    assert signs == {("S1t", "sonnet", "f1"): [2, 0, 0.5], ("S1t", "sonnet", "f2"): [1, 1, 1.0],
                     ("S2", "haiku", "f4"): [1, 0, 1.0], ("drift", "sonnet", "f0_drift"): [1, 0, 1.0]}, signs
    excl = {(m, f): (cells, hit, test) for m, f, cells, hit, test in na.exclusion(reads, groups)}
    assert excl[("sonnet", "f0")] == ([("guesthouse", 4, 6), ("hotel", 0, 3), ("none", 0, 0), ("unmatched", 0, 0)], 2, None)
    assert excl[("sonnet", "f1")][0][0] == ("guesthouse", 1, 6) and excl[("sonnet", "f1")][2] == (2, 0, 0.5)
    print("analysis on synthetic rows: shares, F0 sign tests, the drift label, the Track C rows, invalid rows, and the "
          "booked-venue exclusion give the hand-computed values")


def check_revealed():
    """On the real E13 rows the analysis gives the numbers of review/plan13/revealed_r9b.out and RESULTS.md section 10."""
    reads, _ = na.load(names=("e13",))
    groups = n.ids()
    excl = {(m, f): (cells, hit, test) for m, f, cells, hit, test in na.exclusion(reads, groups)}
    cells, hit, _ = excl[("sonnet", "f0")]
    assert [round(100 * k / total, 1) for _, k, total in cells[:3]] == [13.2, 25.3, 18.5] and hit == 53
    cells, _, (more, less, p) = excl[("sonnet", "f1")]
    assert [round(100 * k / total, 1) for _, k, total in cells[:3]] == [2.1, 8.9, 5.1] and (more, less) == (46, 1)
    assert f"{p:.2g}" == "6.8e-13"
    shares = {(g, m, f): (k, total) for g, m, f, _, k, total in na.shares(reads, na.group_units(groups))}
    assert [round(100 * k / total, 1) for k, total in (shares[("S1t", "haiku", "f0")], shares[("S1t", "haiku", "f1")],
                                                       shares[("S1t", "sonnet", "f0")], shares[("S1t", "sonnet", "f1")])] == [5.1, 1.3, 18.4, 5.2]
    print("real E13 rows: the analysis repeats revealed_r9b.out (Sonnet 13.2% to 2.1%, 46 to 1) and the E13 table")


def main():
    check_forms()
    check_parse()
    check_analysis()
    check_revealed()
    check_pilot_guard()
    data = n.anth.multiwoz()
    check_ids(data)
    check_neutral(data)
    built = check_requests(data)
    check_request_content(data, built)
    check_reuse(built)
    print("all r9/natural tests passed")


if __name__ == "__main__":
    main()
