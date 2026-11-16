"""Test of main/exp0/analysis.py on simulated answers only (main/exp0/simulate.py). No model call, no sealed file, no
real answer. The fake unseal folders go into a new temporary folder.

1. effect: with a known effect, both family tests reject at 0.025 after Holm, with `t_renamed` lower.
2. null: over 200 simulated data sets with no effect, the share of family tests with p <= 0.025 stays near 0.025.
   Tolerance: each test rejects in at most 12 of 200 sets (binomial 200 x 0.025: P(13 or more) = 0.0017); the two
   tests together reject 2 to 20 times in 400 (P outside = 0.0018); the family (Holm) rejects in at most 12 of 200
   sets. This test uses the full 10,000 permutation draws of the analysis (it takes about 3 to 4 minutes).
3. missing: planted missing cells (an errored row, an absent row, a cut reply, a V0 failure, a reply that is not JSON)
   are counted with their reasons and leave the primary test; the worst case scores each one against the sign of the
   primary panel mean.
4. parts: the output has every part of ACTION-PLAN section 2.10 in order, and the three SHA-256 values are those of
   the files.
5. refusal: a row of part tp, of a Track P sample dialogue, of a gate-set dialogue, of another model, with an id of
   the wrong form, or with an id that no stage-1 request has stops the script with an error, and it writes nothing.
   So do a directory of the input that is not a panel folder and a panel that is not the A1 panel. A `._*` file in
   the input is ignored (every full run has one).
6. no answer text: MARKER (in every simulated answer) is in no byte of the outputs or of the printed output.
7. no overwrite: a second run into the same folder stops and changes no byte.
Usage (from explore/): .venv/bin/python -I main/exp0/test_analysis.py
"""
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parents[1]
sys.path.insert(0, str(HERE))
import analysis as an  # noqa: E402
import simulate as sim  # noqa: E402

PANEL = list(an.PANEL)
DATA = an.wave1.anth.multiwoz()
LISTS = an.wave1.ids()
UNITS, REPEAT = an.stage1_units(LISTS)
TMP = pathlib.Path(tempfile.mkdtemp(prefix="exp0_test_"))
HEADINGS = ("## Frozen files", "## 1. The H4 natural family", "## 2. Missing cells and the worst case",
            "## 3. Each model's paired effect", "### 3b. Repeat reads", "## 4. Registered secondary outcomes",
            "### 4.1 `f4`", "### 4.2 `t_described`", "### 4.3 The placebo", "### 4.4 The prefix",
            "### 4.5 The trade ratio", "### 4.6 Any `type` commitment", "## 5. New outcomes of amendment A1",
            "### (a) Contrasts on the dialogues whose goal names no venue", "### (b) Search failure",
            "### (c) The trade ratio with its 95% interval", "### (d) The mixed model", "## Choices (CHOICES)")
KEYS = {"part1_family": {"tests", "claim1_transfers", "anchoring_reading"},
        "part2_missing": {"rule", "cells", "worst_case", "same_decisions"},
        "part3_models": {"read1", "repeat_dialogues", "repeat_means_family", "repeat_means_models"},
        "part4_secondary": {"f4", "t_described", "placebo", "prefix", "trade_points", "commitment"},
        "part5_a1": {"a_no_venue", "b_search_failure", "c_trade", "d_mixed_model"}}


def run_cli(folder, out, *extra):
    p = subprocess.run([sys.executable, "-I", str(HERE / "analysis.py"), str(folder), "--out", str(out), *extra],
                       capture_output=True, text=True, cwd=EXPLORE)
    assert sim.MARKER not in p.stdout + p.stderr, "answer text in the printed output"
    return p


def outputs(out):
    return [out / name for name in an.OUTPUTS if (out / name).exists()]


def no_marker(out):
    for path in outputs(out):
        assert sim.MARKER.encode() not in path.read_bytes(), f"answer text in {path.name}"


def full_run(name, effect, missing=None, seed=1):
    folder, out = TMP / f"{name}_in", TMP / f"{name}_out"
    sim.write(folder, effect, seed, PANEL, missing, DATA, LISTS)
    (folder / "._AppleDouble").write_bytes(b"\x00\x05\x16\x07")  # an exFAT side file: the analysis ignores it
    p = run_cli(folder, out)
    assert p.returncode == 0, p.stderr[-2000:]
    no_marker(out)
    return folder, out, json.loads((out / "stage1.json").read_text()), (out / "RESULT-STAGE1.md").read_text()


def check_parts(result, md):
    pos = [md.find(h) for h in HEADINGS]
    assert all(i >= 0 for i in pos), [h for h, i in zip(HEADINGS, pos) if i < 0]
    assert pos == sorted(pos), "the parts are not in the order of ACTION-PLAN section 2.10"
    for part, keys in KEYS.items():
        assert keys <= set(result["results"][part]), (part, keys - set(result["results"][part]))
    tests = result["results"]["part1_family"]["tests"]
    assert [(t["test"], t["sample"], t["dialogues"]) for t in tests] == [
        ("wrong_values", "natural", 213), ("correct_values_kept", "goal_hotel", 77)], tests
    assert result["meta"]["counts"] == {"natural": 213, "goal_hotel": 77, "natural_repeat": 43,
                                        "goal_hotel_repeat": 13}
    assert result["results"]["part3_models"]["repeat_dialogues"] == {"natural": 43, "goal_hotel": 13}
    files = {"main/exp0/analysis.py": HERE / "analysis.py", "r10/briefsearch.py": EXPLORE / "r10" / "briefsearch.py",
             "r10/analysis/stats.py": EXPLORE / "r10" / "analysis" / "stats.py"}
    for key, path in files.items():
        h = hashlib.sha256(path.read_bytes()).hexdigest()
        assert result["meta"]["frozen_sha256"][key] == h and h in md, key
    assert "outcome (d) removed: no package" in md and an.MIXED_MODEL is False
    assert result["results"]["part5_a1"]["d_mixed_model"] == {"status": "removed",
                                                              "text": "outcome (d) removed: no package"}
    for key in ("pmain/e13.py", "r9/free/gold.py", "r9/additions/zforms.py", "lib/anth.py", "main/wave1_manifest.json"):
        assert result["meta"]["input_sha256"][key] == hashlib.sha256((EXPLORE / key).read_bytes()).hexdigest(), key
    assert an.form_hashes() == json.loads((EXPLORE / "main" / "wave1_manifest.json").read_text())["forms_sha256"]
    assert set(result["meta"]["choices"]) == {k for k, _ in an.CHOICES}
    a5 = result["results"]["part5_a1"]
    assert len(a5["a_no_venue"]["contrasts"]) == len(an.REGISTERED)
    assert set(a5["b_search_failure"]["models"]) == set(PANEL) and set(a5["c_trade"]) == {"t_renamed", "f4"}


def test_effect_parts_overwrite():
    folder, out, result, md = full_run("effect", sim.EFFECT)
    p1 = result["results"]["part1_family"]
    for t in p1["tests"]:
        assert t["reject"] and t["p_holm"] <= an.ALPHA and t["mean"] < 0, t
    assert p1["claim1_transfers"] and p1["anchoring_reading"]
    check_parts(result, md)
    before = {p.name: p.read_bytes() for p in outputs(out)}
    again = run_cli(folder, out)
    assert again.returncode != 0 and "Nothing is overwritten" in again.stderr, again.stderr
    assert {p.name: p.read_bytes() for p in outputs(out)} == before
    print("ok test_effect_parts_overwrite (both tests reject; every part present; no overwrite)")


def test_null_full_run():
    _, _, result, md = full_run("null", sim.NULL, seed=2)
    check_parts(result, md)
    print("ok test_null_full_run (every part present under no effect)")


def planted():
    """Six read-1 cells of the family, each missing for a different reason."""
    nat, hot = UNITS["natural"], UNITS["goal_hotel"]
    cid = lambda m, part, d, form: f"em1_{m}-{part}-{d}-{form}-1"
    return {cid("sonnet", "nat", nat[0], "t_renamed"): "errored",
            cid("haiku", "nat", nat[1], "t_legacy"): "cut",
            cid("sol", "hot", hot[0], "t_renamed"): "schema",
            cid("luna", "hot", hot[1], "t_legacy"): "not_json",
            cid("deepseek", "nat", nat[2], "t_renamed"): "absent",
            cid("deepseek", "nat", nat[2], "t_legacy"): "absent"}


def test_missing_cells():
    plan = planted()
    reasons = {"errored": "row errored", "cut": "stop max_tokens", "schema": "schema (V0)", "not_json": "parse",
               "absent": "row absent"}
    for c, kind in plan.items():  # each planted kind is a missing cell with its reason
        short, form = c.split("-")[0].removeprefix("em1_"), c.split("-")[3]
        assert an.judge(sim.missing_row(short, c, kind), form) == (None, reasons[kind]), kind
    folder, out, result, _ = full_run("missing", sim.EFFECT, plan)
    p2 = result["results"]["part2_missing"]
    assert p2["family_read1_missing"] == len(plan), p2["family_read1_missing"]
    want = {}
    for c, kind in plan.items():
        m, part, _, form, _ = an.ID.match(c).groups()
        want.setdefault(f"{m} {part} {form}", {}).setdefault(reasons[kind], 0)
        want[f"{m} {part} {form}"][reasons[kind]] += 1
    assert {k: v["read1_reasons"] for k, v in p2["cells"].items()} == want, p2["cells"]

    cells, missing, units, _, _, _ = an.load(folder, PANEL, DATA, LISTS)
    primary = result["results"]["part1_family"]["tests"]
    assert all(t["mean"] < 0 for t in primary)  # so the worst case scores t_renamed 1 and t_legacy 0
    fill = an.worst_fill(-1)
    assert fill == (1, 0)
    for c in plan:
        m, part, d, form, _ = an.ID.match(c).groups()
        test = an.FAMILY[0] if part == "nat" else an.FAMILY[1]
        assert an.model_diff(cells, m, test, d) is None, c  # it leaves the primary test
        new = an.value(cells, m, test.form, d)
        base = an.value(cells, m, test.base, d)
        want_diff = (1 if new is None else new) - (0 if base is None else base)
        assert an.model_diff(cells, m, test, d, fill=fill) == want_diff, c
    for test, t, w in zip(an.FAMILY, primary, p2["worst_case"]):
        assert t["dialogues"] == w["dialogues"] == {"natural": 213, "goal_hotel": 77}[t["sample"]]
        assert "missing t_renamed scores 1, missing t_legacy scores 0" == w["fill_direction"]
        vals = an.panel_values(cells, test, units[test.sample], PANEL, fill=fill)
        assert abs(round(sum(vals) / len(vals), 6) - w["mean"]) < 1e-9, (test.name, w["mean"])
        assert w["p"] == an.stats.permutation_test(vals, an.PERMUTATION_DRAWS, an.PERMUTATION_SEED) or \
            abs(w["p"] - an.stats.permutation_test(vals, an.PERMUTATION_DRAWS, an.PERMUTATION_SEED)) < 1e-6
    print("ok test_missing_cells (6 planted cells: counted with reasons, out of the primary test, worst case applied)")


def test_refusal():
    base = TMP / "refuse_base"
    sim.write(base, sim.NULL, 3, PANEL, None, DATA, LISTS)
    sample, gate = set(LISTS["sample"]), LISTS["gate"]
    sonnet = [r["custom_id"] for r in an.wave1.requests("sonnet", DATA, LISTS)]
    tp = next(c for c in sonnet if "-tp-" in c)
    in_sample = next(c for c in sonnet if "-nat-" in c and an.ID.match(c).group(3) + ".json" in sample)
    cases = {
        "part tp": tp,
        "Track P sample dialogue": in_sample,
        "gate-set dialogue": f"em1_sonnet-nat-{gate[0].removesuffix('.json')}-t_legacy-1",
        "does not have the wave-1 form": f"em1_sonnet-nat-{UNITS['natural'][0].lower()}-t_legacy-1",
        "no stage-1 request has the id": f"em1_sonnet-nat-{UNITS['natural'][0]}-p_main-1",
        "is of another model": f"em1_haiku-nat-{UNITS['natural'][0]}-t_legacy-1",
    }
    for phrase, cid in cases.items():
        folder, out = TMP / f"refuse_{len(list(TMP.iterdir()))}", TMP / f"refuse_out_{phrase[:4]}"
        shutil.copytree(base, folder)
        with open(folder / "em1_sonnet" / "raw.jsonl", "a") as fh:
            fh.write(json.dumps({"custom_id": cid, "type": "succeeded", "model": "claude-sonnet-5-5",
                                 "stop": "end_turn", "input_tokens": 1, "output_tokens": 1,
                                 "text": sim.answer("t_legacy", ["hotel"])}) + "\n")
        sim.write_manifest(folder, PANEL)  # the manifest matches, so only the id can stop the script
        p = run_cli(folder, out)
        assert p.returncode != 0 and phrase in p.stderr and "Stopped before any write" in p.stderr, (phrase, p.stderr)
        assert not outputs(out), f"{phrase}: an output file was written"
    folder, out = TMP / "refuse_dir", TMP / "refuse_dir_out"
    shutil.copytree(base, folder)
    (folder / "notes").mkdir()
    p = run_cli(folder, out)
    assert p.returncode != 0 and "folders that are not in the panel: notes" in p.stderr, p.stderr
    assert not outputs(out), "extra folder: an output file was written"
    out = TMP / "refuse_panel_out"
    p = run_cli(base, out, "--panel", "sonnet,haiku")
    assert p.returncode != 0 and "must be the interim panel of A1" in p.stderr, p.stderr
    assert not outputs(out), "panel: an output file was written"
    print(f"ok test_refusal ({len(cases)} kinds of forbidden id, an extra folder and a wrong panel stop the script, "
          f"nothing written)")


def test_null_rate(sets=200):
    ids = {m: [c for c in sim.stage1_ids(m, DATA, LISTS)
               if an.ID.match(c).group(2) in ("nat", "hot") and an.ID.match(c).group(4) in ("t_legacy", "t_renamed")]
           for m in PANEL}
    reject, family, start = [0, 0], 0, time.time()
    for k in range(sets):
        rows = {m: {r["custom_id"]: r for r in sim.rows(m, ids[m], sim.NULL, seed=1000 + k)} for m in PANEL}
        cells, _ = an.score(rows, ids)
        tests = an.family(cells, UNITS, PANEL, with_interval=False)
        for i, t in enumerate(tests):
            reject[i] += t["p"] <= an.ALPHA
        family += any(t["reject"] for t in tests)
    print(f"   null: p <= 0.025 in {reject[0]}/{sets} (wrong values) and {reject[1]}/{sets} (correct values kept); "
          f"family rejects in {family}/{sets}; {time.time() - start:.0f} s")
    assert max(reject) <= 12 and 2 <= sum(reject) <= 20 and family <= 12, (reject, family)
    print("ok test_null_rate")


def main():
    try:
        test_effect_parts_overwrite()
        test_missing_cells()
        test_refusal()
        test_null_full_run()
        test_null_rate()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("analysis test passed")


if __name__ == "__main__":
    main()
