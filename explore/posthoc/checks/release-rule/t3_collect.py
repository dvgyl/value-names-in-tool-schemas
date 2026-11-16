"""T3 (SPEC-T3-bootstrap-precision.md), step 1: collect the paired per-request differences of every actual release
decision that the paper reports, with the rules and levels the paper uses, and reproduce each 2,000-draw decision.

Post hoc numerical sensitivity. Stored answers only, read through the loaders of the paper's analyses (unchanged):
posthoc/release-sim/stored.py (Tables 5, 9, 12, 13), r10/analysis/rtest_v.py (Table 14, broad
rewrite; as in rtest_final9.part_b), posthoc/release-fresh/analyze.py (Table 11) and
r10/analysis/release_test3.py (replication). Every loader refuses folders whose names start with
"em". No model call, no network call, no key file.

Each group runs in its own process (the loaders put different folders on sys.path):
    python3 -I posthoc/checks/release-rule/t3_collect.py stored
    python3 -I posthoc/checks/release-rule/t3_collect.py fresh
    python3 -I posthoc/checks/release-rule/t3_collect.py replication
    python3 -I posthoc/checks/release-rule/t3_collect.py merge      -> out/t3_diffs.json
"""
import importlib.util
import json
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]  # explore/ of the repository
W = ROOT / "posthoc"
EXPLORE = ROOT
OUT = HERE / "out"
SIM_DIR = W / "release-sim"
sys.path.insert(0, str(SIM_DIR))
import rules  # noqa: E402  (posthoc/release-sim/rules.py, unchanged)

SEED, DRAWS = 20261112, 2000
NAMES = {"sol": "Sol", "luna": "Luna", "deepseek": "DeepSeek", "qwen": "Qwen", "gemma": "Gemma", "haiku": "Haiku",
         "sonnet": "Sonnet"}
UPD = {"a": "repeat", "b": "paraphrase 1", "c": "full rename", "d": "field-order edit", "e": "paraphrase 2"}


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def boot_vals(diffs, seed=SEED, draws=DRAWS):
    """The frozen bootstrap (rtest_final9.boot, stored.boot_vals): sorted means of `draws` resamples of requests."""
    n = len(diffs)
    rng = random.Random(seed)
    return sorted(sum(rng.choices(diffs, k=n)) / n for _ in range(draws))


def view(diffs, seed=SEED, draws=DRAWS):
    return {"change": sum(diffs) / len(diffs), "up": sum(x > 0 for x in diffs), "down": sum(x < 0 for x in diffs),
            "vals": boot_vals(diffs, seed, draws)}


def decide(diffs_by_set, rule, level, seed=SEED, draws=DRAWS):
    views = [view(diffs_by_set[s], seed, draws) for s in ("open", "specific")]
    dec, classes, ivs = rules.decide_sets(views, level, rule)
    return dec, classes, ivs


def entry(key, group, table, label, diffs, rules_levels, expected):
    """rules_levels: {rule: level}; expected: {rule: decision} (the paper's 2,000-draw decisions)."""
    rep = {}
    for rule, lev in rules_levels.items():
        dec, classes, ivs = decide(diffs, rule, lev)
        rep[rule] = {"decision": dec, "classes": classes, "intervals": ivs}
        assert dec == expected[rule], (key, rule, dec, expected[rule])
    return {"key": key, "group": group, "table": table, "label": label, "sets": diffs,
            "pairs": {s: len(diffs[s]) for s in diffs}, "rules": {r: {"level": lv} for r, lv in rules_levels.items()},
            "reproduced_2000": rep}


# ------------------------------------------------------------------------------------------------ groups

def group_stored():
    ST = module("t3_stored", SIM_DIR / "stored.py")
    fid = {r["name"]: r for r in json.loads((SIM_DIR / "out" / "fidelity.json").read_text())["rows"]}
    out, checks = [], []
    for c in ST.comparisons():
        n = c["name"]
        f = fid[n]
        diffs = c["sets"]
        if n.startswith("R10-20"):
            key = f"five-model|{c['model']}|{c['update']}"
            group, table = "five-model test", "5, 13"
            label = f"{NAMES[c['model']]}, {UPD[c['update']]}"
            rl = {"original": c["level_run"], "revised": c["level_run"], "final": c["level_final"]}
        elif n.startswith("R10-22"):
            key = f"two-model|{c['model']}|{c['update']}"
            group, table = "two-model test", "5, 13"
            label = f"{NAMES[c['model']]}, {UPD[c['update']]}"
            rl = {"original": c["level_run"], "revised": c["level_run"], "final": c["level_final"]}
        elif n.startswith("R10-16"):
            first = c["answers"] == "first answer"
            key = f"haiku|{c['update']}|{'first' if first else 'all'}"
            group, table = "Haiku controls", "5, 12"
            label = f"Haiku, {UPD[c['update']]}" + (", first answer only" if first else "")
            rl = ({"original": c["level_run"]} if first else
                  {"original": c["level_run"], "revised": c["level_run"], "final": c["level_final"]})
        else:
            key = f"stored|{c['model']}|{c['a']}|{c['b']}"
            group, table = "stored comparisons", "9"
            label = f"{NAMES.get(c['model'], c['model'])}: {c['a']} v {c['b']}"
            rl = {"original": c["level_run"], "revised": c["level_run"], "final": c["level_final"]}
        exp = {r: f[r] for r in rl}
        e = entry(key, group, table, label, diffs, rl, exp)
        e["source_name"] = n
        out.append(e)
        checks.append({"key": key, "reproduced": True})
    # Table 14 (steered rewrites) and the broad rewrite, as in rtest_final9.part_b (first answer per prefix)
    V = ST.V
    sets = ST.sets_r10_6()
    f9 = json.loads((EXPLORE / "r10" / "analysis" / "out" / "rtest_final9.json").read_text())["B"]["edits"]

    def dof(a, b):
        return {s: ST.diffs_of(a, b, sets[s]) for s in ("open", "specific")}
    sc, hc = V.tool_reads(("erp_sonnet",), "t0", 1), V.tool_reads(("ers_haiku",), "t0", 1)
    edits = []
    for c, word in (("th", "hotel"), ("tg", "guesthouse")):
        edits.append((f"steered|sonnet|{c}", "steered rewrites", "14", f"Sonnet, {word} rewrite",
                      dof(sc, V.tool_reads(("ers_sonnet",), c, 1)), f"steered {c}, sonnet", ("original", "revised")))
        edits.append((f"steered|haiku|{c}", "steered rewrites", "14", f"Haiku, {word} rewrite",
                      dof(hc, V.tool_reads(("ers_haiku",), c, 1)), f"steered {c}, haiku", ("original", "revised")))
    for m in ("sonnet", "sol"):
        edits.append((f"broad|{m}", "broad rewrite", "Appendix J", f"{NAMES[m]}, broad rewrite",
                      dof(V.tool_reads((f"erp_{m}",), "t0", 1), V.tool_reads((f"erp_{m}",), "tedit", 1)),
                      f"broad rewrite, {m}", ("original",)))
    for key, group, table, label, diffs, f9key, rl_names in edits:
        st = f9[f9key]["98.75"]
        for s in ("open", "specific"):  # same per-request data as the stored analysis
            assert abs(sum(diffs[s]) / len(diffs[s]) - st[s]["change"]) < 1e-3, (key, s)
            assert len(diffs[s]) == st[s]["pairs"], (key, s)
        exp = {"original": st["first_as_run"], "revised": st["revised_as_run"]}
        rl = {r: 1 - 0.05 / 4 for r in rl_names}
        e = entry(key, group, table, label, diffs, rl, {r: exp[r] for r in rl})
        for r in rl:  # interval ends equal the stored ones (4 decimals)
            for s, iv in zip(("open", "specific"), e["reproduced_2000"][r]["intervals"]):
                assert [round(x, 4) for x in iv] == st[s]["as_run"], (key, r, s, iv, st[s]["as_run"])
        e["source_name"] = f9key
        out.append(e)
        checks.append({"key": key, "reproduced": True})
    return out, checks


def group_fresh():
    AN = module("t3_fresh", W / "release-fresh" / "analyze.py")
    import runs  # noqa: E402  (put on sys.path by analyze.py)
    res = json.loads((W / "release-fresh" / "out" / "result.json").read_text())
    data, g = runs.context()
    sel = AN.f27.select(data, g)
    sets = {s: sel[s] for s in AN.SETS}
    run_of = {m: r for r, m in AN.f27.MODEL_OF.items()}
    out, checks = [], []
    for u, e in res["updates"].items():
        lev, cell = e["level"], e["cell"]
        for m, v in e["models"].items():
            reads = AN.load(run_of[m], False)
            diffs = {s: AN.diffs(reads, sets[s], AN.f27.CONTROL, cell) for s in AN.SETS}
            rl = {"final": lev, "revised": lev, "original": lev}
            ent = entry(f"fresh|{m}|{u}", "fresh test", "11", f"{NAMES[m]}, {u}", diffs, rl, v["decisions"])
            for s, iv in zip(AN.SETS, ent["reproduced_2000"]["final"]["intervals"]):
                assert [round(x, 4) for x in iv] == v["sets"][s]["symmetric"], (u, m, s)
            for s, iv in zip(AN.SETS, ent["reproduced_2000"]["original"]["intervals"]):
                assert [round(x, 4) for x in iv] == v["sets"][s]["as_run"], (u, m, s)
            ent["source_name"] = f"R10-27 {u} {m}"
            out.append(ent)
            checks.append({"key": ent["key"], "reproduced": True})
    return out, checks


def group_replication():
    R3 = module("t3_rep", EXPLORE / "r10" / "analysis" / "release_test3.py")
    import runs  # noqa: E402
    stored = json.loads((EXPLORE / "r10" / "analysis" / "out" / "release_test3.json").read_text())["runs"]
    data, g = runs.context()
    sets = R3.ra.request_sets(data, g)
    out, checks = [], []
    for run_name, cells in R3.h3.PLAN.items():
        assert not run_name.startswith("em")
        reads = R3.load(run_name, False, set(cells))
        control, (u, upd) = R3.h3.CONTROL_OF[run_name], R3.h3.UPDATE_OF[run_name]
        lev = R3.h3.LEVEL[run_name]
        diffs = {}
        for s in ("open", "specific"):
            dd = []
            for d in sets[s]:
                a, b = R3.a20.valid_scores(reads, d, control), R3.a20.valid_scores(reads, d, upd)
                if a and b:
                    dd.append(100 * (R3.a20.mean(b) - R3.a20.mean(a)))
            diffs[s] = dd
        st = stored[run_name]["replication"]
        exp = {"original": st["first"]["release"], "revised": st["revised"]["release"]}
        m = R3.h3.MODEL_OF[run_name]
        ent = entry(f"replication|{m}|{u}", "replication", "Appendix I", f"{NAMES[m]}, {UPD[u]} (replication)", diffs,
                    {"original": lev, "revised": lev}, exp)
        for s, iv in zip(("open", "specific"), ent["reproduced_2000"]["original"]["intervals"]):
            assert all(abs(x - y) < 1e-9 for x, y in zip(iv, st["sets"][s]["interval"])), (run_name, s)
        ent["source_name"] = run_name
        out.append(ent)
        checks.append({"key": ent["key"], "reproduced": True})
    return out, checks


def main():
    cmd = sys.argv[1]
    OUT.mkdir(exist_ok=True)
    if cmd == "merge":
        allr, allc = [], []
        for gname in ("stored", "fresh", "replication"):
            x = json.loads((OUT / f"t3_diffs_{gname}.json").read_text())
            allr += x["comparisons"]
            allc += x["checks"]
        (OUT / "t3_diffs.json").write_text(json.dumps({"what": "T3 inputs: paired per-request differences (points)",
                                                        "comparisons": allr, "checks": allc}, indent=0))
        print(f"merged {len(allr)} comparisons, {sum(len(c['rules']) for c in allr)} rule-decisions")
        return
    fn = {"stored": group_stored, "fresh": group_fresh, "replication": group_replication}[cmd]
    out, checks = fn()
    for e in out:
        del e["reproduced_2000"]  # recomputed in t3_boot.py; the asserts above passed
    (OUT / f"t3_diffs_{cmd}.json").write_text(json.dumps({"comparisons": out, "checks": checks}, indent=0))
    print(f"{cmd}: {len(out)} comparisons; every 2,000-draw decision reproduced")


if __name__ == "__main__":
    main()
