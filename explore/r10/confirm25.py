"""Amendment R10-25 (PROTOCOL.md): a held-out confirmation of the repair results of the paper. Exploratory,
fixed in the protocol before the run and before any computation of a new outcome on the held-out answers.

Data: the opened stage-1 answers of Registration A (main/exp0/open/em1_<model>/raw.jsonl), read only through the frozen
loader main/exp0/analysis.load (its main never runs, and it writes nothing). Form t_legacy (the original form; it equals
the development form F0), parts nat and hot. Sets (`sets`): NT, the 213 natural dialogues (the brief sets no type); H,
the 66 goal-hotel dialogues whose brief sets hotel; G, the 11 goal-hotel dialogues whose brief sets guesthouse; and the
label groups LN, LG and LH of the label reference.
Calls (`build`): one verifier call (forms10.FORMS["verify"], the user text is the full dialogue) for each valid t_legacy
answer of the parts nat and hot whose type holds hotel and not guesthouse. The custom_id holds the read number of that
answer. Runs ern_<model> (r10/runs.py, experiment code "V"). `assert_stage1` replaces groups.assert_unprotected for
these runs: only stage-1 dialogues can enter a request.
Usage (from explore/): .venv/bin/python -I r10/confirm25.py check | sets | counts | project
"""
import collections
import importlib.util
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
for sub in ("lib", "forms", "pmain", "trackc", "r9", "r9/natural", "r9/additions", "r9/free", "main"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(HERE))
import forms10  # noqa: E402

AMENDMENT = "### R10-25 "
OPEN = EXPLORE / "main" / "exp0" / "open"
FROZEN = EXPLORE / "main" / "exp0" / "analysis.py"
FROZEN_SHA256 = "c8841480ae3016d3ca71ab64daf265281f57b6dee800a9a4a73eaf2a8aa4d0d9"
PANEL = ("sonnet", "haiku", "sol", "luna", "deepseek", "qwen", "gemma")  # the interim panel of the registration
FORM, PARTS, CELL = "t_legacy", ("nat", "hot"), "verify"
MAX_BOUND = 1.50  # USD per step of R10-25
RESERVE = 0.00  # the caps of newmoney.py (group R25) hold the margin, as in R10-19 to R10-24
# name -> (model, account, pilot calls); the order of the calls while the money holds (Sonnet only if it fits)
PLAN = {
    "ern_deepseek": ("deepseek", "deepinfra_main", 4),
    "ern_qwen": ("qwen", "deepinfra_main", 4),
    "ern_gemma": ("gemma", "deepinfra_main", 4),
    "ern_luna": ("luna", "openai_r9", 4),
    "ern_sol": ("sol", "openai_r9", 3),
    "ern_haiku": ("haiku", "anthropic_r9a", 4),
    "ern_sonnet": ("sonnet", "anthropic_r9a", 2),
}
RUNS = tuple(PLAN)
MODEL_OF = {n: p[0] for n, p in PLAN.items()}
RUN_OF = {p[0]: n for n, p in PLAN.items()}
SIZES = {"NT": 213, "H": 66, "G": 11, "LN": 187, "LG": 19, "LH": 74}
REPEAT_SIZES = {"NT": 43, "H": 11, "G": 2}
STATED = {"NT": 3, "H": 18, "G": 2}
_cache = {}


def frozen():
    """main/exp0/analysis.py as a module under another name, with no cache file written next to it."""
    if "frozen" not in _cache:
        import hashlib
        if hashlib.sha256(FROZEN.read_bytes()).hexdigest() != FROZEN_SHA256:
            sys.exit(f"Not run. {FROZEN.relative_to(EXPLORE)} differs from its frozen SHA-256.")
        saved = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        try:
            spec = importlib.util.spec_from_file_location("exp0_frozen_analysis", FROZEN)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        finally:
            sys.dont_write_bytecode = saved
        _cache["frozen"] = mod
    return _cache["frozen"]


def hotel_only(t):
    return isinstance(t, tuple) and "hotel" in t and "guesthouse" not in t


def stage1():
    """(units, repeat) of the frozen analysis: the stage-1 natural and goal-hotel ids (no ".json")."""
    A = frozen()
    return A.stage1_units(A.wave1.ids())


def sets(data):
    """{"NT", "H", "G", "LN", "LG", "LH": [dialogue ids with .json]} and {"NT", "H", "G": [ids with repeat reads]}.
    Corpus text, briefs and labels only (no answer)."""
    import common
    import gold
    import natural
    units, repeat = stage1()
    nat = [d + ".json" for d in units["natural"]]
    hot = [d + ".json" for d in units["goal_hotel"]]
    assert all(gold.brief_type(data[d]) is None and gold.brief_type(data[d], "fail_info") is None for d in nat)
    out = {"NT": nat, "H": [d for d in hot if gold.brief_type(data[d]) == "hotel"],
           "G": [d for d in hot if gold.brief_type(data[d]) == "guesthouse"]}
    assert len(out["H"]) + len(out["G"]) == len(hot)
    for d in nat + hot:
        t = common.gold_form(data[d])["type"]
        says = natural.says_hotel(data[d], True)
        if t == ("hotel",):
            out.setdefault("LH", []).append(d)
        elif t is None and says:
            out.setdefault("LN", []).append(d)
        elif t == ("guesthouse",) and says:
            out.setdefault("LG", []).append(d)
    rep = {k: [d for d in out[k] if d.removesuffix(".json") in repeat["natural" if k == "NT" else "goal_hotel"]]
           for k in ("NT", "H", "G")}
    sizes = {k: len(v) for k, v in out.items()}
    assert sizes == SIZES, sizes
    assert {k: len(v) for k, v in rep.items()} == REPEAT_SIZES
    return out, rep


def assert_stage1(ids):
    """Raise ValueError when a dialogue id (with .json) is not a stage-1 natural or goal-hotel dialogue, or when it is
    in the gate set or in the Track P sample (which holds the stage-2 dialogues)."""
    A = frozen()
    lists = A.wave1.ids()
    units, _ = A.stage1_units(lists)
    allowed = {d + ".json" for v in units.values() for d in v}
    blocked = set(lists["gate"]) | set(lists["sample"])
    bad = sorted(d for d in ids if d not in allowed or d in blocked)
    if bad:
        raise ValueError(f"R10-25: {len(bad)} dialogue(s) outside stage 1 (first {bad[0]})")


def originals(data=None):
    """cells[(model, part, form)][dialogue][read] of the frozen loader (parsed fields or None), for the 7 models."""
    if "cells" not in _cache:
        A = frozen()
        cells, missing, units, repeat, nrows, _ = A.load(OPEN, list(PANEL), data)
        _cache["cells"] = cells
        _cache["rows"] = nrows
    return _cache["cells"]


def original_reads(model, data=None):
    """{(dialogue with .json, read): fields or None} of t_legacy in the parts nat and hot, in the order of the stage-1
    lists (natural first) and of the reads."""
    cells = originals(data)
    units, _ = stage1()
    out = {}
    for part, key in (("nat", "natural"), ("hot", "goal_hotel")):
        got = cells.get((model, part, FORM), {})
        for d in units[key]:
            for r in sorted(got.get(d, {})):
                out[(d + ".json", r)] = got[d][r]
    return out


def call_keys(model, data=None):
    """[(dialogue with .json, read)] of the valid t_legacy answers with a hotel-only filter."""
    return [k for k, f in original_reads(model, data).items() if f is not None and hotel_only(f["type"])]


def request(name, model, d, read, data):
    """One verifier request: the call of the development verifier runs (verify3.build, runs.build_b) on dialogue d."""
    import common
    import models
    import runs
    form = forms10.FORMS[CELL]
    return models.request(model, runs.cid(name, d, CELL, read), common.dialogue_text(data[d]), form.system,
                          form.schema, cell=CELL)


def build(name, model, reads, data, g):
    """The verifier requests of one model: one per key of call_keys, user text the full dialogue."""
    assert reads == 1 and MODEL_OF[name] == model, (name, model, reads)
    return [request(name, model, d, r, data) for d, r in call_keys(model, data)]


def check_projection(name, bound):
    """A step goes only when the free money of its account (limit minus committed, no reserve) holds its bound and the
    money that R10-23 (projected rounds without a batch) and R10-24 (runs without a batch or a run step) still need."""
    import accounts
    import budget_gate
    import harmless3
    import runs
    import steer3
    acc = runs.RUNS[name].account
    data, g = runs.context()
    r23 = 0.0
    for m in steer3.MODELS:
        if steer3.PLAN[m].account != acc:
            continue
        x = steer3.future(m, data, g)
        if x is None:
            sys.exit(f"Not run. {name}: R10-23 model {m} has no conversation pilot, so its money cannot be projected.")
        r23 += x
    r24 = harmless3.pending_bounds(acc)
    free = budget_gate.free(acc, 0.0)
    print(f"R10-25 projection on {acc}: free {free:.2f} USD (limit {budget_gate.limit(acc):.2f} - committed "
          f"{accounts.committed(accounts.ACCOUNTS[acc]):.2f}); this step {bound:.2f} + R10-23 later rounds {r23:.2f} + "
          f"R10-24 not run {r24:.2f} = {bound + r23 + r24:.2f} USD")
    if bound + r23 + r24 > free + 1e-9:
        sys.exit(f"Not run. {name}: the step and the money that R10-23 and R10-24 still need ({bound + r23 + r24:.2f} "
                 f"USD) pass the free money of {acc} ({free:.2f} USD). Apply the cut order of R10-25 first.")


def amendment_text():
    import steer2
    return steer2.amendment_text(AMENDMENT)


def check_amendment():
    """R10-25 is in PROTOCOL.md under the round-10 amendments and holds the verifier text, the fixed values, the hashes,
    the predictions and the run names."""
    text = amendment_text()
    if text is None:
        sys.exit(f"Not run. PROTOCOL.md has no amendment {AMENDMENT.strip()!r}.")
    flat = " ".join(text.split())
    need = [forms10.VERIFY_SYSTEM, "Status: exploratory, fixed in the protocol before the run.",
            "W_hotel = 545 and W_notype = 994", "δ = 2.0 points", "deepinfra_main 2.00 USD, openai_r9 1.60 USD, "
            "anthropic_r9a 0.45 USD", "The step limit is 1.50 USD", FROZEN_SHA256,
            "e8cd2490a137a888a3463420f7da4349f29b645fb780a72288400cbaa7291794",
            "2615e6ac412c49ee507c6b2a5d76441df1e2d404ec789a33b9b6963d9fe09dce", "- V1 (main):", "- V1w:", "- V2:",
            "- V3:", "- V4:", "- D1:", "- D2:", "The word rule (PRIMARY, fixed now)", *RUNS,
            "DeepSeek, Qwen, Gemma, Luna and Haiku 4, Sol 3, Sonnet 2"]
    for words in need:
        if words not in flat:
            sys.exit(f"Not run. R10-25 does not hold {words!r}.")


def counts(data):
    """Requests per model, by set (offline; after the amendment)."""
    s, _ = sets(data)
    where = {d: k for k in ("NT", "H", "G") for d in s[k]}
    out = {}
    for m in PANEL:
        keys = call_keys(m, data)
        c = collections.Counter((where[d], "read 1" if r == 1 else "reads 2-3") for d, r in keys)
        out[m] = {"requests": len(keys), **{f"{a} {b}": n for (a, b), n in sorted(c.items())}}
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "check":
        check_amendment()
        print("R10-25 holds the verifier text, the fixed values, the hashes, the predictions and the run names")
    elif cmd == "sets":
        import runs
        data, _g = runs.context()
        s, rep = sets(data)
        print({k: len(v) for k, v in s.items()}, {k: len(v) for k, v in rep.items()})
    elif cmd == "counts":
        import runs
        data, _g = runs.context()
        for m, c in counts(data).items():
            print(m, c)
    elif cmd == "project":
        import runs
        for n in RUNS:
            check_projection(n, 0.0)
    else:
        sys.exit(__doc__)
