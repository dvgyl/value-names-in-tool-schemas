"""Tests of the X7 forms, groups, neutral words, requests, step guards, and analysis. No API call.

Usage: python3 -I r9/x7/test_x7.py
"""
import collections
import difflib
import json
import pathlib
import re
import sys
import tempfile
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import x7  # noqa: E402
import x7_analyze as xa  # noqa: E402
from test_natural import SIZE_OR_QUALITY  # noqa: E402

A0_TEXT = (
    "You read a conversation between a traveller and a tourist information assistant in Cambridge. Write down the "
    "traveller's requirements for the attraction as one JSON object. Use only what the traveller said or agreed to. "
    "Fields: name, area, type. Give name as the attraction name if the traveller asked for one attraction by name, else "
    "null. For each field give null if the traveller never stated a requirement, \"any\" if the traveller said it does "
    "not matter, or a list of acceptable values in the traveller's order of preference (first is most preferred). "
    "Allowed values: area: centre, north, south, east, west. type: architecture, boat, cinema, college, concerthall, "
    "entertainment, multiple sports, museum, nightclub, park, swimmingpool, theatre. If the traveller changed their "
    "mind, give the final requirement. An option that the traveller only accepted from the assistant's offers is not a "
    "requirement. Output only the JSON object.")
A1_EDITS = [(["entertainment"], ["amusement_venue"]), (["multiple", "sports"], ["athletics_venue"])]
EXPECTED = {"ex7_claude": {"claude-haiku-5-5": 734 * 2 * 3, "claude-sonnet-5-5": 734 * 2 * 2},
            "ex7_luna": {"gpt-6-luna": 734 * 2 * 3}, "ex7_sol": {"gpt-6.1-sol": 734 * 2},
            "ex7_di": {m: 734 * 2 for m in x7.natural.ds.MODELS}}


def words(s):
    return re.findall(r"\w+|[^\w\s]", s)


def edits(a, b):
    a, b = words(a), words(b)
    return [(a[i1:i2], b[j1:j2]) for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
            if op != "equal"]


def check_forms():
    a0, a1 = x7.FORMS["a0"], x7.FORMS["a1"]
    assert x7.TYPES == ["architecture", "boat", "cinema", "college", "concerthall", "entertainment", "multiple sports",
                        "museum", "nightclub", "park", "swimmingpool", "theatre"], x7.TYPES
    assert x7.system(a0) == A0_TEXT, x7.system(a0)
    assert edits(x7.system(a0), x7.system(a1)) == A1_EDITS, edits(x7.system(a0), x7.system(a1))
    assert edits(json.dumps(x7.schema(a0)), json.dumps(x7.schema(a1))) == A1_EDITS
    hotel, s0 = x7.e13.schema(False)["schema"], x7.schema(a0)["schema"]
    assert (s0["type"], s0["additionalProperties"], s0["required"]) == ("object", False, ["name", "area", "type"])
    assert s0["properties"]["name"] == hotel["properties"]["name"] and s0["properties"]["area"] == hotel["properties"]["area"]
    assert s0["properties"]["type"] == json.loads(json.dumps(hotel["properties"]["type"]).replace(
        json.dumps(["guesthouse", "hotel"]), json.dumps(x7.TYPES)))
    print("forms: A0 is p_main for attractions with the closed E13 schema; A1 changes only the two type values, in the "
          "prompt and in the schema")


def check_parse():
    a0, a1 = x7.FORMS["a0"], x7.FORMS["a1"]
    t = lambda **f: "noise {} " + json.dumps({"name": None, "area": None, "type": None, **f})  # noqa: E731
    assert x7.parse(t(type=["amusement_venue", "Athletics Venue"]), a1)["type"] == ("entertainment", "multiple sports")
    assert x7.parse(t(type=["athletics_venue", "museum"]), a1)["type"] == ("multiple sports", "museum")
    assert x7.parse(t(type=["amusement_venue"]), a0)["type"] == ("amusement_venue",), "A0 must not map back"
    assert x7.parse(t(type=["Entertainment"]), a1)["type"] == ("entertainment",)
    assert x7.parse(t(type=["mutliple sports", "multiple_sports"]), a0)["type"] == ("multiple sports",)
    assert x7.parse(t(type="any", area=["north", "centre"], name="Kettles Yard"), a0) == {
        "name": "Kettles Yard", "area": ("north", "centre"), "type": "any"}
    assert x7.parse(t(), a1) == {"name": None, "area": None, "type": None}
    assert x7.parse(t(type="theatre"), a1)["type"] == ("theatre",)
    print("parse: A1 neutral words map back to entertainment and multiple sports; A0 maps nothing back")


def check_neutral(data):
    """The F4 rule, applied in the order of PROTOCOL.md X7: no part of the original value, no size or quality word, no
    use in a traveller turn of the training split (space, underscore, or hyphen; plural allowed)."""
    val, test = x7.anth.splits()
    turns = [t["text"] for k, d in data.items() if k not in val | test for i, t in enumerate(d["log"]) if i % 2 == 0]
    found = {}
    for value, candidates in x7.CANDIDATES.items():
        own = set(value.split()) | {w.removesuffix("s") for w in value.split()} | set(
            w for k, v in x7.DB_SPELLING.items() if v == value for w in k.split())
        for token in candidates:
            phrase = re.compile(r"\b" + token.replace("_", "[ _-]?") + r"s?\b", re.I)
            parts = token.split("_")
            found[token] = (sum(1 for s in turns if phrase.search(s)),
                            sorted(p for p in parts if any(p in w or w in p for w in own)),
                            sorted(set(parts) & SIZE_OR_QUALITY))
        first = next(tok for tok in candidates if found[tok] == (0, [], []))
        assert x7.NEUTRAL[value] == first, (value, first, found)
    print(f"neutral words: {x7.NEUTRAL}; {len(turns):,} traveller turns; (turns, parts of the value, size or quality "
          f"words) = {found}")


def check_ids(data):
    stored = x7.ids()
    assert x7.compute_ids(data) == stored, "ids.json differs from the rule"
    units = x7.dialogues(stored["groups"])
    val, test = x7.anth.splits()
    assert len(units) == x7.UNION and not set(units) & (val | test)
    x7.anth.assert_outside_trackp(units, data)
    assert set(stored["revealed"]) == {u.removesuffix(".json") for u in units}
    assert set(stored["revealed"].values()) <= set(x7.TYPES) | {"none", "unmatched"}
    print(f"ids: ids.json equals the rule ({', '.join(f'{g} {n}' for g, n in x7.COUNTS.items())}; union {x7.UNION}); "
          f"revealed types {dict(collections.Counter(stored['revealed'].values()).most_common())}")


def body(r):
    return r["params"] if "params" in r else r["body"]


def check_requests(data):
    stored = x7.ids()
    units = [u.removesuffix(".json") for u in x7.dialogues(stored["groups"])]
    pool, (val, test) = x7.anth.trackp_pool(data), x7.anth.splits()
    text = {f: (x7.system(form), x7.schema(form)) for f, form in x7.FORMS.items()}
    for name, exp in x7.EXPERIMENTS.items():
        reqs = x7.requests(name, data, stored)
        models = collections.Counter(body(r)["model"] for r in reqs)
        assert models == EXPECTED[name], (name, models)
        seen = collections.Counter()
        for r in reqs:
            exp_name, unit, form, read, short = r["custom_id"].split("-")
            m, b = x7.natural.MODELS[short], body(r)
            assert exp_name == name and int(read) in exp.reads[short] and len(r["custom_id"]) <= 64
            assert unit + ".json" not in pool and unit + ".json" not in val | test
            seen[(short, form, unit)] += 1
            prompt, fmt = text[form]
            user = x7.common.dialogue_text(data[unit + ".json"])
            msgs = b.get("messages") or b.get("input")
            if m.provider == "anthropic":
                assert (b["system"], msgs) == (prompt, [{"role": "user", "content": user}])
                assert b["output_config"] == {"effort": m.effort, "format": fmt}
                assert (b["thinking"], b["max_tokens"]) == (m.thinking, 4096)
                continue
            assert msgs == [{"role": "system", "content": prompt}, {"role": "user", "content": user}]
            if m.provider == "openai":
                assert b["text"]["format"]["schema"] == fmt["schema"] and b["text"]["format"]["strict"]
                assert (b["reasoning"], b["max_output_tokens"]) == ({"effort": m.effort}, 4000) and "temperature" not in b
            else:
                assert b == x7.natural.ds.request(x7.natural.ds.MODELS[m.id], r["custom_id"], user, prompt, fmt["schema"])["body"]
        assert set(seen.values()) <= {len(n) for n in exp.reads.values()}
        assert {(s, f, u) for s in exp.reads for f in x7.FORMS for u in units} == set(seen)
    settings = {s: (x7.natural.MODELS[s].id, x7.natural.MODELS[s].effort) for s in ("sol", "luna")}
    assert settings == {"sol": ("gpt-6.1-sol", "low"), "luna": ("gpt-6-luna", "none")}, settings
    assert {n: e.account for n, e in x7.EXPERIMENTS.items()} == {
        "ex7_claude": "anthropic_r9a", "ex7_luna": "openai_r9", "ex7_sol": "openai_r9", "ex7_di": "deepinfra"}
    print("requests: " + "; ".join(f"{n} " + ", ".join(f"{m} {k:,}" for m, k in c.items()) for n, c in EXPECTED.items())
          + "; each dialogue once per form and read; the panel settings; no Track P, validation, or test dialogue")


def check_step_guards():
    """The non-Claude folders refuse a pilot. The Claude pilot without --approve prints its bound and stops before
    any client exists."""
    for name in ("ex7_luna", "ex7_sol", "ex7_di"):
        with mock.patch.object(sys, "argv", [f"{name}.py", "pilot"]):
            try:
                x7.main(name)
            except SystemExit as e:
                assert "has no pilot of its own" in str(e), e
            else:
                raise AssertionError(f"{name} ran its pilot step")
    no_call = mock.Mock(side_effect=AssertionError("a paid client was made"))
    with mock.patch.object(sys, "argv", ["ex7_claude.py", "pilot"]), mock.patch.object(x7.anth, "client", no_call), \
            mock.patch.object(x7.accounts, "api_key", no_call):
        try:
            x7.main("ex7_claude")
        except SystemExit as e:
            assert str(e).startswith("Not run."), e
        else:
            raise AssertionError("ex7_claude ran its pilot without --approve")
    assert not no_call.called
    print("step guards: only ex7_claude has a pilot, and without --approve it stops before any client")


def row(cid, text=None, stop="end_turn", kind="succeeded"):
    return {"custom_id": cid, "type": kind, "stop": stop, "text": text}


def check_analysis():
    t = lambda v: json.dumps({"name": None, "area": None, "type": v})  # noqa: E731
    rows = {
        "ex7_claude": [row("ex7_claude-U1-a0-1-sonnet", t(["entertainment"])),
                       row("ex7_claude-U1-a0-2-sonnet", t(["entertainment", "museum"])),
                       row("ex7_claude-U1-a1-1-sonnet", t(["amusement_venue"])), row("ex7_claude-U1-a1-2-sonnet", t(["museum"])),
                       row("ex7_claude-U2-a0-1-sonnet", t(["museum"])), row("ex7_claude-U2-a0-2-sonnet", t(None)),
                       row("ex7_claude-U2-a1-1-sonnet", t("any")), row("ex7_claude-U2-a1-2-sonnet", t(["Amusement Venue"])),
                       row("ex7_claude-U3-a0-1-sonnet", t(["entertainment"])),
                       row("ex7_claude-U3-a0-2-sonnet", t(["entertainment"]), "max_tokens"),
                       row("ex7_claude-U3-a1-1-sonnet", "no json here"), row("ex7_claude-U3-a1-2-sonnet", None, None, "errored")]
        + [row(f"ex7_claude-U4-a0-{r}-haiku", t(["museum"])) for r in (1, 2, 3)]
        + [row("ex7_claude-U4-a1-1-haiku", t(["museum"])), row("ex7_claude-U4-a1-2-haiku", t(["museum"])),
           row("ex7_claude-U4-a1-3-haiku", t(None)),
           row("ex7_claude-U5-a0-1-haiku", t(["multiple sports"])), row("ex7_claude-U5-a1-1-haiku", t(["athletics_venue"]))],
        "ex7_di": [row("ex7_di-U1-a0-1-qwen", t(["entertainment"])), row("ex7_di-U1-a1-1-qwen", t(["amusement_venue"]))],
    }
    stored = {"groups": {"G_ent": ["U1.json", "U2.json"], "C_ent": ["U2.json", "U3.json"], "G_sport": ["U5.json"],
                         "C_sport": [], "M": ["U4.json"]},
              "revealed": {"U1": "entertainment", "U2": "museum", "U3": "none", "U4": "museum", "U5": "unmatched"}}
    with tempfile.TemporaryDirectory() as tmp:
        for name, rs in rows.items():
            (pathlib.Path(tmp) / name).mkdir()
            (pathlib.Path(tmp) / name / "raw.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rs))
        reads, invalid = xa.load(tmp)
    assert invalid == {("sonnet", "a0"): 1, ("sonnet", "a1"): 2}, invalid
    of_target = lambda g: xa.target(x7.GROUPS[g].value)  # noqa: E731
    of_revealed = lambda g: xa.excludes(stored["revealed"])  # noqa: E731
    shares = {(g, m, f): (u, k, n) for g, m, f, u, k, n in xa.shares(reads, xa.group_units(stored), of_target)}
    assert shares == {("G_ent", "sonnet", "a0"): (2, 2, 4), ("G_ent", "sonnet", "a1"): (2, 2, 4),
                      ("G_ent", "qwen", "a0"): (1, 1, 1), ("G_ent", "qwen", "a1"): (1, 1, 1),
                      ("C_ent", "sonnet", "a0"): (2, 1, 3), ("C_ent", "sonnet", "a1"): (1, 1, 2),
                      ("G_sport", "haiku", "a0"): (1, 1, 1), ("G_sport", "haiku", "a1"): (1, 1, 1),
                      ("M", "haiku", "a0"): (1, 3, 3), ("M", "haiku", "a1"): (1, 2, 3)}, shares
    signs = {(g, m): (round(d, 2), *rest) for g, m, d, *rest in xa.signs(reads, xa.group_units(stored), of_target)}
    assert signs == {("G_ent", "sonnet"): (0.0, 1, 1, 1.0), ("G_ent", "qwen"): (0.0, 0, 0, 1.0),
                     ("C_ent", "sonnet"): (-16.67, 0, 1, 1.0), ("G_sport", "haiku"): (0.0, 0, 0, 1.0),
                     ("M", "haiku"): (33.33, 1, 0, 1.0)}, signs
    units_of = xa.revealed_units(stored)
    assert units_of == {"G_ent": {"U1", "U2"}, "C_ent": {"U2"}, "G_sport": set(), "C_sport": set(), "M": {"U4"}}
    excl = {(g, m, f): (u, k, n) for g, m, f, u, k, n in xa.shares(reads, units_of, of_revealed)}
    assert excl == {("G_ent", "sonnet", "a0"): (2, 0, 4), ("G_ent", "sonnet", "a1"): (2, 2, 4),
                    ("G_ent", "qwen", "a0"): (1, 0, 1), ("G_ent", "qwen", "a1"): (1, 0, 1),
                    ("C_ent", "sonnet", "a0"): (1, 0, 2), ("C_ent", "sonnet", "a1"): (1, 1, 2),
                    ("M", "haiku", "a0"): (1, 0, 3), ("M", "haiku", "a1"): (1, 0, 3)}, excl
    signs = {(g, m): (round(d, 2), *rest) for g, m, d, *rest in xa.signs(reads, units_of, of_revealed)}
    assert signs == {("G_ent", "sonnet"): (-50.0, 0, 2, 0.5), ("G_ent", "qwen"): (0.0, 0, 0, 1.0),
                     ("C_ent", "sonnet"): (-50.0, 0, 1, 1.0), ("M", "haiku"): (0.0, 0, 0, 1.0)}, signs
    print("analysis on synthetic rows: target shares, the A1 against A0 sign tests and drops, the revealed-choice "
          "exclusion, a dialogue in two groups, and the invalid rows give the hand-computed values")


def main():
    check_forms()
    check_parse()
    check_analysis()
    data = x7.panel.multiwoz()
    check_neutral(data)
    check_ids(data)
    check_requests(data)
    check_step_guards()
    print("all r9/x7 tests passed")


if __name__ == "__main__":
    main()
