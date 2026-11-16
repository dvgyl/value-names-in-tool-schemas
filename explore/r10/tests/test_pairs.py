"""Test of r10/pairs.py (experiment H). No API call. Usage: explore/.venv/bin/python -I r10/tests/test_pairs.py

It checks the two mechanical checks, check 3 (RULE_D_EXCLUDED), the choice and pairs.json, the request count (1,920
per read with 12 pairs), the seeded draw, the meaning of each item kind, the forms, the unchanged calibration pair,
and the new-text assert.
"""
import collections
import json
import pathlib
import re
import subprocess
import sys
import tempfile

R10 = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R10))
sys.path.insert(0, str(R10.parent / "r9" / "natural"))
import groups  # noqa: E402
import pairs as P  # noqa: E402
import test_natural  # noqa: E402
import zforms  # noqa: E402

ALL = P.CANDIDATES + (P.HOTEL,)
PLAN_ORDER = ["table", "room", "restaurant", "car", "taxi", "doctor", "gym", "school", "bike", "apartment", "office",
              "movie", "boat", "truck", "letter", "call", "coffee", "camera", "box", "flowers"]
PLAN_OTHERS = {"table": ("booth", "bar seat"), "room": ("suite", "apartment"), "restaurant": ("cafe", "pub"),
               "car": ("van", "minibus"), "taxi": ("minibus", "limousine"), "doctor": ("nurse practitioner", "pharmacist"),
               "gym": ("pool", "yoga studio"), "school": ("college", "academy"), "bike": ("e-bike", "scooter"),
               "apartment": ("house", "studio"), "office": ("remote", "hybrid"), "movie": ("documentary", "series"),
               "boat": ("ferry", "kayak"), "truck": ("van", "trailer"), "letter": ("email", "fax"),
               "call": ("video call", "message"), "coffee": ("tea", "hot chocolate"), "camera": ("camcorder", "webcam"),
               "box": ("envelope", "tube"), "flowers": ("plant", "wreath"), "hotel": ("guesthouse", "hostel")}
EXCLUDED = {"gym", "apartment", "office", "movie", "truck", "call", "box", "flowers"}
KEPT = [k for k in PLAN_ORDER if k not in EXCLUDED]
# SHA-256 of the 160 calibration requests of version 1 (pairs.v1.json); the calibration pair does not change.
HOTEL_V1_SHA256 = "e1a155120f311994f1fa7f372e474a0a04a81fb9a94a5199ffa68bb99feacfed"


def has(text, phrase):
    """The phrase as whole words, with an optional plural (a test copy, separate from pairs.word_pattern)."""
    return re.search(r"(?<![\w-])" + re.escape(phrase) + r"(?:s|es)?(?![\w-])", text, re.I) is not None


def test_candidates():
    assert [p.collision for p in P.CANDIDATES] == PLAN_ORDER and P.HOTEL.collision == "hotel"
    assert P.VALUE_CHANGES == {"boat": ("ferry", "punt", P.VALUE_CHANGES["boat"][2])} and P.VALUE_CHANGES["boat"][2]
    changed = {k: tuple(P.VALUE_CHANGES[k][1] if k in P.VALUE_CHANGES and v == P.VALUE_CHANGES[k][0] else v
                        for v in vs) for k, vs in PLAN_OTHERS.items()}
    assert {p.collision: p.others for p in ALL} == changed, "a value differs from the plan outside VALUE_CHANGES"
    assert len({p.neutral for p in ALL}) == len(ALL)
    assert P.HOTEL.neutral == test_natural.n.NEUTRAL, "the calibration token is not the round-9 F4 token"
    assert set(P.RULE_D_EXCLUDED) == EXCLUDED and all(P.RULE_D_EXCLUDED.values())
    print("candidates: the 20 pairs of the plan in its order (boat: ferry becomes punt, as VALUE_CHANGES records), "
          "hotel with the F4 token, and 8 pairs in RULE_D_EXCLUDED")


def test_checks():
    assert P.SIZE_OR_QUALITY == test_natural.SIZE_OR_QUALITY, "the copy of the round-9 size and quality words differs"
    assert {p.collision: P.check_pair(p) for p in ALL} == {p.collision: [] for p in ALL}
    table = P.CANDIDATES[0]
    in_corpus = table._replace(neutral="guest_house")
    assert len(P.token_failures(in_corpus)) == 1 and "traveller turns" in P.token_failures(in_corpus)[0]
    value_and_size = table._replace(neutral="big_booth_spot")
    got = P.token_failures(value_and_size)
    assert len(got) == 2 and "'booth'" in got[0] and "'big'" in got[1], got
    bad_para = table._replace(para="a seat nearby")
    assert len(P.check_pair(bad_para)) == 1 and "'seat'" in P.check_pair(bad_para)[0]
    bad_constraint = table._replace(constraint="The bar should be {price} and in the {place}.")
    assert len(P.para_failures(bad_constraint)) == 1 and "'bar'" in P.para_failures(bad_constraint)[0]
    print("checks: every candidate passes checks 1 and 2; planted failures of each part are found")


def test_choice(spec):
    content = json.loads(P.PAIRS_JSON.read_text())
    assert content == P.choice(), "pairs.json differs from the rule"
    assert content["chosen"] == KEPT and len(KEPT) == 12 >= P.MIN_PAIRS and content["seed"] == P.SEED
    assert [r["pair"] for r in content["checked"]] == PLAN_ORDER
    assert {r["pair"] for r in content["checked"] if r["excluded"]} == EXCLUDED
    assert content["value_changes"] == {k: list(v) for k, v in P.VALUE_CHANGES.items()}
    assert content["requests_sha256"] == P.sha256(spec), "the requests differ from the pinned SHA-256"
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "pairs.json"
        assert [p.collision for p in P.chosen(path)] == KEPT and path.exists()
        first = path.read_text()
        P.chosen(path)
        assert path.read_text() == first, "a rerun changed the file"
        path.write_text(first.replace('"table"', '"coffee"', 1))
        try:
            P.chosen(path)
        except ValueError:
            pass
        else:
            raise AssertionError("a changed pairs.json was accepted")
    saved = dict(P.RULE_D_EXCLUDED)
    try:
        P.RULE_D_EXCLUDED.update({k: "test" for k in KEPT[:1]})
        P.RULE_D_EXCLUDED.update({k: "test" for k in ("coffee", "camera")})
        try:
            P.choice()
        except RuntimeError as e:
            assert "stop rule: only 9" in str(e), e
        else:
            raise AssertionError("the stop rule did not stop a list of 9 pairs")
    finally:
        P.RULE_D_EXCLUDED.clear()
        P.RULE_D_EXCLUDED.update(saved)
    print("choice: pairs.json equals the rule (12 pairs); it is written one time; a changed file stops the choice; "
          "fewer than 12 pairs stop H")


def test_counts(spec):
    main = [r for r in spec if not r["cell"].startswith("cal_")]
    cal = [r for r in spec if r["cell"].startswith("cal_")]
    assert len(main) == 12 * 20 * 4 * 2 == 1920 and len(cal) == 20 * 4 * 2 == 160
    assert [*dict.fromkeys(r["pair"] for r in main)] == KEPT and {r["pair"] for r in cal} == {"hotel"}
    assert collections.Counter(r["cell"] for r in spec) == {"g0": 960, "g4": 960, "cal_g0": 80, "cal_g4": 80}
    assert collections.Counter(r["kind"] for r in main) == {k: 480 for k in P.KINDS}
    assert len({r["stem"] for r in spec}) == len(spec)
    for r in spec:
        assert re.fullmatch(r"[a-z]+_\d\d_[a-z_]+", r["unit"]) and r["stem"] == f"{r['unit']}-{r['form']}"
        assert len(f"erh_sonnet_r1-{r['stem']}-9-sonnet") <= 64, r["stem"]
    assert P.sha256(cal) == HOTEL_V1_SHA256, "the calibration requests differ from version 1"
    print(f"counts: {len(main):,} requests per read for 12 pairs, plus {len(cal)} for the calibration pair "
          "(unchanged from version 1)")


def test_determinism():
    for p in ALL:
        assert P.items(p) == P.items(p)
        draws = P.scenarios(p)
        assert len(set(draws)) == P.N_SCENARIOS
        assert P.scenarios(p, seed=P.SEED + 1) != draws, f"{p.collision}: the seed does not change the draw"
    code = "import sys; sys.path.insert(0, sys.argv[1]); import pairs; print(pairs.sha256(pairs.NEW_TEXTS))"
    # -I ignores PYTHONHASHSEED, so each process has its own random hash seed.
    got = {subprocess.run([sys.executable, "-I", "-c", code, str(R10)], capture_output=True, text=True,
                          check=True).stdout.strip() for _ in range(3)}
    assert got == {P.sha256(P.NEW_TEXTS)}, got
    print(f"determinism: seed {P.SEED}; a changed seed changes each draw; 3 new processes give the same texts")


def test_kinds():
    for p in ALL:
        values = (p.collision,) + p.others
        by = collections.defaultdict(dict)
        for it in P.items(p):
            by[it.scenario][it.kind] = it
            assert it.user == f"{p.role.capitalize()}: " + it.text
        assert len(by) == 20 and all(set(k) == set(P.KINDS) for k in by.values())
        for s, k in by.items():
            word, para = k["unclear_word"].text, k["unclear_para"].text
            spec_, gen = k["clear_specific"].text, k["clear_general"].text
            assert has(word, p.collision) and not any(has(word, v) for v in p.others), word
            assert not any(has(para, w) for v in values for w in v.split()), para
            assert para == word.replace(p.word, p.para, 1) and word.count(p.word) == 1
            assert spec_.startswith(word + " ") and gen.startswith(word + " ")
            tail = spec_[len(word) + 1:]
            assert all(has(tail, v) for v in values) and f"not {p.nouns[1]} or {p.nouns[2]}." in tail, spec_
            tail = gen[len(word) + 1:]
            assert all(has(tail, v) for v in values) and "would all be fine" in tail and "not" not in tail, gen
            for it in k.values():
                assert not any(has(it.text, w) for w in p.neutral.split("_")), (p.neutral, it.text)
    print("item kinds: unclear_word holds the collision word only; no paraphrase holds a value word; each "
          "clear_specific item excludes both other values; each clear_general item accepts all three")


def test_scenarios():
    for p in ALL:
        dims = P.dims(p)
        for it, draw in zip(P.items(p)[::4], P.scenarios(p)):
            assert it.values == {d.field: d.values[i] for d, i in zip(dims, draw)}
            assert all(d.phrases[i] in it.text for d, i in zip(dims, draw)), it.text
    for key in KEPT:
        texts = [it.text for it in P.items(key)]
        assert not any(re.search(r"should be (?:high|low|moderate)\b", t) for t in texts), key
    assert all("a meeting of" in it.text for it in P.items("coffee"))
    for key in ("doctor", "school", "letter"):
        assert P.dims(key)[3] == P.WEEKDAYS
        assert not any(has(it.text, d) for it in P.items(key) for d in ("Saturday", "Sunday")), key
    print("scenarios: each item states the drawn place, price, size and day; no \"should be high\"; doctor, school "
          "and letter use Monday to Friday only")


def words(s):
    return re.findall(r"\w+|[^\w\s]", s)


def test_forms():
    f0 = P.FRAME.format(a_assistant=P.F0_ASSISTANT, role="traveller", service="hotel",
                        fields=P.F0_FIELDS[len("Fields: "):-1] + ". " + P.F0_NAME[:-1],
                        allowed=P.F0_ALLOWED[len("Allowed values: "):])
    assert f0 == zforms.F0, "the frame differs from F0 outside its changed parts"
    assert "hotel" not in P.FRAME.lower() and "traveller" not in P.FRAME
    assert P.system(P.HOTEL).startswith(f"You read a conversation between a traveller and {P.F0_ASSISTANT} in")
    for p in ALL:
        g0, g4 = P.form(p, False), P.form(p, True)
        assert isinstance(g0, zforms.Form) and g0.system.count(f" {p.service} ") == 2
        assert g0.system.count(p.role) == P.F0_ROLE_COUNT
        assert p is P.HOTEL or "hotel" not in g0.system.lower()
        diff = [(" ".join(a), " ".join(b)) for a, b in test_natural.edits(g0.system, g4.system, words)]
        assert diff == [(p.collision, p.neutral)], (p.collision, diff)
        enum = lambda f: f.schema["properties"]["type"]["anyOf"][2]["items"]["enum"]
        assert enum(g0) == list(p.others) + [p.collision] and enum(g4) == list(p.others) + [p.neutral]
        assert json.dumps(g0.schema).replace(json.dumps(p.collision), json.dumps(p.neutral)) == json.dumps(g4.schema)
        ref = zforms.schema()
        assert all(g0.schema["properties"][f]["anyOf"][:2] == ref["properties"]["area"]["anyOf"][:2]
                   for f in g0.schema["properties"])
        assert (g0.schema["required"], g0.schema["additionalProperties"]) == (list(g0.schema["properties"]), False)
        for f, prop in g0.schema["properties"].items():
            assert f"{f}: {', '.join(prop['anyOf'][2]['items']['enum'])}." in g0.system
    assert P.system("letter").startswith("You read a conversation between a customer and a letter sending assistant")
    assert " and a camera hire assistant in " in P.system("camera")
    print("forms: one frame (F0 with the assistant phrase, role word, service noun, field list and allowed values "
          "changed); G4 changes only the collision value; the schema is closed as zforms.schema")


def test_new_text(spec):
    assert {r["system"] for r in spec} | {r["user"] for r in spec} <= set(P.NEW_TEXTS)
    groups.assert_new_text(P.NEW_TEXTS)
    print(f"new text: NEW_TEXTS ({len(P.NEW_TEXTS):,} texts) covers every request; no sentence of 4 or more words "
          "is in a Track C or Track I item")


def main():
    assert P.PAIRS_JSON.exists(), "run `python3 -I r10/pairs.py choose` first; the test does not write pairs.json"
    spec = P.requests_spec()
    test_candidates()
    test_checks()
    test_choice(spec)
    test_counts(spec)
    test_determinism()
    test_kinds()
    test_scenarios()
    test_forms()
    test_new_text(spec)
    print("all r10/pairs tests passed")


if __name__ == "__main__":
    main()
