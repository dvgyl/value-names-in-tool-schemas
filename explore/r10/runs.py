"""The registry of the round-10 runs and their only entry point (review/plan15/ACTION-PLAN.md sections 2.1 and 2.9).

Runs, reads and accounts follow WAVE1 of review/plan14/r10_costs.py. One folder holds one model. Run folders start
with "er", so lib/seal.py seals none of them, main/caps.py counts none of them, and lib/watch.py fetches them.

Before a paid step, main(name) checks, in this order:
1. Predictions first: explore/PROTOCOL.md holds "## Round 10 runs", and the SHA-256 of that section equals
   r10/protocol.lock.json ("## Round 10 amendments" is outside the hashed part).
2. No protected dialogue: groups.assert_unprotected for MultiWOZ runs; groups.assert_new_text for constructed text.
3. Requests unchanged (submit): the request hash equals r10/manifest.json.
4. Bounds within free money: budget_gate.fits(name, approved bound), with the 2 USD reserve per account (R10-18:
   labeltest.RESERVE; R10-19 and R10-20: labeltest2.RESERVE and the caps of newmoney.py; R10-21 and R10-22:
   labeltest3.RESERVE and their own cap in newmoney.py; R10-23 and R10-24: steer3.RESERVE and the cap group R23 of
   newmoney.py, and for round 1 of R10-23 the projection of all rounds, steer3.check_projection; R10-25:
   confirm25.RESERVE, the cap group R25 of newmoney.py and confirm25.check_projection, which keeps the money of the
   later R10-23 rounds free).
Experiment V (R10-25) reads held-out stage-1 dialogues: confirm25.assert_stage1 replaces groups.assert_unprotected.
Usage: python3 -I r10/runs.py manifest | list | verify       (offline)
       python3 -I r10/<name>.py estimate | pilot | submit | fetch   (the client steps; one thin script per run)
"""
import hashlib
import json
import pathlib
import sys
from typing import Callable, NamedTuple

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(HERE))
import accounts  # noqa: E402
import anth  # noqa: E402
import common  # noqa: E402
import forms10  # noqa: E402
import groups as grp  # noqa: E402
import models  # noqa: E402
import openai_compat as oc  # noqa: E402
import textedit  # noqa: E402
import tools  # noqa: E402
import zforms  # noqa: E402

PROTOCOL = EXPLORE / "PROTOCOL.md"
LOCK = HERE / "protocol.lock.json"
MANIFEST = HERE / "manifest.json"
SECTION, AMEND = "## Round 10 runs", "## Round 10 amendments"
PLANNING_OUT = {"anthropic": 80, "openai": 80, "deepinfra": 120}  # used only before a pilot measures the sizes


class Run(NamedTuple):
    exp: str
    model: str  # a key of models.MODELS
    account: str
    reads: int
    build: Callable  # (name, model, reads, data, g) -> list of requests
    multiwoz: bool = True
    pilot: int = None  # pilot calls per cell (amendments R10-13 and R10-14); None: anth.PILOT_PER_CELL (10)


def did(d):
    return d.removesuffix(".json")


def cid(name, d, cell, read):
    return f"{name}-{did(d)}-{cell}-{read}"


def text_full(data, d):
    return common.dialogue_text(data[d])


# A: the 554 prefixes, the form arm p0 and the tool arms t0, t1, t0ask.
def build_a(name, model, reads, data, g):
    out = []
    for d in g["booked"]:
        user = zforms.prefix_text(data[d])
        for read in range(1, reads + 1):
            f0 = zforms.FORMS["f0"]
            out.append(models.request(model, cid(name, d, "p0", read), user, f0.system, f0.schema, cell="p0"))
            for arm in ("t0", "t1", "t0ask"):
                out.append(models.request(model, cid(name, d, arm, read), user, tools.tool_system(arm), None,
                                          tools=tools.TOOLS[arm], cell=arm))
    return out


FULL = ("s1t", "s3", "s2")


def build_b(name, model, reads, data, g):
    out = []
    arms = ("f0", "b_list", "b_shot", "b_evidence", "verify")
    for grp_name in FULL:
        for d in g[grp_name]:
            user = text_full(data, d)
            for read in range(1, reads + 1):
                for arm in arms:
                    form = forms10.FORMS[arm]
                    out.append(models.request(model, cid(name, d, arm, read), user, form.system, form.schema, cell=arm))
                if model in ("sol", "luna") and grp_name in ("s2", "s3"):
                    form = forms10.FORMS["b_define"]
                    out.append(models.request(model, cid(name, d, "b_define", read), user, form.system, form.schema,
                                              cell="b_define"))
    return out


def build_i(name, model, reads, data, g):
    out = []
    for d in g["ins"]:
        texts = {"orig": text_full(data, d), "ins": textedit.inserted_text(data[d])}
        for read in range(1, reads + 1):
            for t, user in texts.items():
                for f in ("f0", "f1"):
                    form = zforms.FORMS[f]
                    out.append(models.request(model, cid(name, d, f"{t}_{f}", read), user, form.system, form.schema,
                                              cell=f"{t}_{f}"))
    return out


def build_panel(groups_used):
    def build(name, model, reads, data, g):
        out = []
        for grp_name in groups_used:
            for d in g[grp_name]:
                user = text_full(data, d)
                for read in range(1, reads + 1):
                    for f in ("f0", "f1"):
                        form = zforms.FORMS[f]
                        out.append(models.request(model, cid(name, d, f, read), user, form.system, form.schema, cell=f))
        return out
    return build


def build_s2(name, model, reads, data, g):
    """Step 2 of A. Before the stage-1 fetch, the requests come from the stage-1 pilot answers (the step-2 replay test
    is the pilot of this run); after the fetch, from the stage-1 answers."""
    import stage2
    source = "raw" if (EXPLORE / f"era1_{model}" / "raw.jsonl").exists() else "pilot"
    return stage2.requests(model, source)


def build_h(name, model, reads, data, g):
    import pairs
    out = []
    for item in pairs.requests_spec():
        for read in range(1, reads + 1):
            out.append(models.request(model, f"{name}-{item['stem']}-{read}", item["user"], item["system"],
                                      item["schema"], cell=item["cell"]))
    return out


def build_r(name, model, reads, data, g):
    """Amendment R10-6: arms t0 (as build_a) and tedit (the frozen edit of r10/release/edit.json)."""
    import release
    return release.build(name, model, reads, data, g)


def build_w(name, model, reads, data, g):
    """Amendment R10-7: the returned flag (r10/flag.py), arms plain and flag."""
    import flag
    return flag.build(name, model, reads, data, g)


def build_t(arm):
    """Amendment R10-8: later turns (r10/turns.py). The fixed part is the first agent request of each conversation."""
    def build(name, model, reads, data, g):
        import gold
        import turns
        return turns.first_requests(name, arm, data, list(g["booked"]), gold.hotel_db())
    build.arm = arm
    return build


def build_u(name, model, reads, data, g):
    """Amendment R10-13: the returned flag with travellers who require a hotel (Claude) and the GPT models (flag2.py)."""
    import flag2
    return flag2.build(name, model, reads, data, g)


def build_s(name, model, reads, data, g):
    """Amendment R10-14: the tools that a service with its own interest rewrote (steer.py)."""
    import steer
    return steer.build(name, model, reads, data, g)


def build_m(name, model, reads, data, g):
    """Amendment R10-15: more service rewrites, with and without a business interest (steer2.py)."""
    import steer2
    return steer2.build(name, model, reads, data, g)


def build_c(part):
    """Amendment R10-16: harmless control updates for the release rule (control.py). part: "control" (cells t0 and
    tord) or "repeat" (cell trep, the original tool again in a new batch)."""
    def build(name, model, reads, data, g):
        import control
        return control.build(name, model, reads, data, g, part)
    build.part = part
    return build


def build_y(name, model, reads, data, g):
    """Amendment R10-17: the planned verifier of experiment B on the open models (verify3.py)."""
    import verify3
    return verify3.build(name, model, reads, data, g)


def build_l(sets_used):
    """Amendment R10-18: the label test with one fixed definition (labeltest.py), cells l_hotel and l_code."""
    import labeltest
    return labeltest.build(sets_used)


def build_l2(name, model, reads, data, g):
    """Amendment R10-19: the label test, third arm l_neutral (labeltest2.py; the cells and reads of labeltest2.PLAN)."""
    import labeltest2
    return labeltest2.build(name, model, reads, data, g)


def build_k(name, model, reads, data, g):
    """Amendment R10-20: release tests of harmless updates (harmless.py; control, repeat, paraphrase, rename)."""
    import harmless
    return harmless.build(name, model, reads, data, g)


def build_l3(name, model, reads, data, g):
    """Amendment R10-21: the label test in the tool channel (labeltest3.py; cells tl_hotel, tl_code, tl_neutral)."""
    import labeltest3
    return labeltest3.build(name, model, reads, data, g)


def build_k2(name, model, reads, data, g):
    """Amendment R10-22: two more release tests on the tool channel (harmless2.py; control, field order, paraphrase)."""
    import harmless2
    return harmless2.build(name, model, reads, data, g)


def build_q(k):
    """Amendment R10-23: the steering runs when the agent can search again (steer3.py). Round k of the conversations;
    a round k > 1 is built from the fetched answers of rounds 1 to k - 1."""
    import steer3
    return steer3.build(k)


def build_k3(name, model, reads, data, g):
    """Amendment R10-24: the replication of the two paraphrase flags with a fresh control (harmless3.py)."""
    import harmless3
    return harmless3.build(name, model, reads, data, g)


def build_v(name, model, reads, data, g):
    """Amendment R10-25: one verifier call per held-out t_legacy answer with a hotel-only filter (confirm25.py)."""
    import confirm25
    return confirm25.build(name, model, reads, data, g)


def subset(build, key_fn):
    """A build restricted by a filter on (group name or None, dialogue id or stem, cell, read)."""
    def built(name, model, reads, data, g):
        return [r for r in build(name, model, reads, data, g) if key_fn(r)]
    return built


def reads_from(first, build):
    """A build whose read numbers start at `first` (a later read of the same design, so custom_ids stay unique)."""
    def built(name, model, reads, data, g):
        out = []
        for r in build(name, model, first + reads - 1, data, g):
            if int(r["custom_id"].rsplit("-", 1)[1]) >= first:
                out.append(r)
        return out
    return built


def build_cells(groups_used, cells):
    """B-type arms (forms10.FORMS) on the named groups."""
    def build(name, model, reads, data, g):
        out = []
        for grp_name in groups_used:
            for d in g[grp_name]:
                user = text_full(data, d)
                for read in range(1, reads + 1):
                    for arm in cells:
                        form = forms10.FORMS[arm]
                        out.append(models.request(model, cid(name, d, arm, read), user, form.system, form.schema,
                                                  cell=arm))
        return out
    return build


def half(which):
    """The first or second half of the units, by a sorted list of dialogue ids or H stems (a stable split)."""
    def key(r):
        unit = r["custom_id"].split("-")[1]
        return (hash_unit(unit) % 2) == which
    return key


def hash_unit(unit):
    return int(hashlib.sha256(unit.encode()).hexdigest()[:8], 16)


RUNS = {
    # A, stage 1 (stage 2 is built from the fetched rows by stage2.py)
    "era1_sonnet": Run("A", "sonnet", "anthropic_r9a", 2, build_a),
    "era1_opus": Run("A", "opus", "anthropic_r9a", 1, build_a),
    "era1_haiku": Run("A", "haiku", "anthropic_r9b", 2, build_a),
    "era1_sol": Run("A", "sol", "openai_r9", 2, build_a),
    "era1_luna": Run("A", "luna", "openai_r9", 2, build_a),
    # A, step 2
    "era2_sonnet": Run("A2", "sonnet", "anthropic_r9a", 1, build_s2),
    "era2_opus": Run("A2", "opus", "anthropic_r9a", 1, build_s2),
    "era2_haiku": Run("A2", "haiku", "anthropic_r9b", 1, build_s2),
    "era2_sol": Run("A2", "sol", "openai_r9", 1, build_s2),
    "era2_luna": Run("A2", "luna", "openai_r9", 1, build_s2),
    # B
    "erb_sonnet": Run("B", "sonnet", "anthropic_r9a", 1, build_b),
    "erb_haiku": Run("B", "haiku", "anthropic_r9b", 2, build_b),
    "erb_sol": Run("B", "sol", "openai_r9", 1, build_b),
    "erb_luna": Run("B", "luna", "openai_r9", 2, build_b),
    # I
    "eri_sonnet": Run("I", "sonnet", "anthropic_r9b", 2, build_i),
    "eri_haiku": Run("I", "haiku", "anthropic_r9b", 2, build_i),
    "eri_sol": Run("I", "sol", "openai_r9", 2, build_i),
    "eri_luna": Run("I", "luna", "openai_r9", 2, build_i),
    # F: effort high, S1t and S2 only
    "erf_sonnet": Run("F", "sonnet_high", "anthropic_r9b", 1, build_panel(("s1t", "s2"))),
    "erf_haiku": Run("F", "haiku_high", "anthropic_r9b", 1, build_panel(("s1t", "s2"))),
    "erf_sol": Run("F", "sol_high", "openai_r9", 1, build_panel(("s1t", "s2"))),
    "erf_luna": Run("F", "luna_high", "openai_r9", 1, build_panel(("s1t", "s2"))),
    # E and G: the strongest models as panel models
    "ere_opus": Run("E", "opus", "anthropic_r9b", 1, build_panel(FULL)),
    "erg_astra": Run("G", "astra", "openai_r9", 1, build_panel(FULL)),
    # H: constructed word and schema pairs (pairs.py)
    "erh_sonnet": Run("H", "sonnet", "anthropic_r9a", 2, build_h, multiwoz=False),
    "erh_haiku": Run("H", "haiku", "anthropic_r9b", 2, build_h, multiwoz=False),
    "erh_opus": Run("H", "opus", "anthropic_r9b", 1, build_h, multiwoz=False),
    "erh_sol": Run("H", "sol", "openai_r9", 2, build_h, multiwoz=False),
    "erh_luna": Run("H", "luna", "openai_r9", 2, build_h, multiwoz=False),
    # The fill (review/plan14/r10_costs.py FILL, in its order). Accounts: the free money after wave 1.
    "erx_f0h_opus": Run("F", "opus_high", "anthropic_r9b", 1,
                        subset(build_panel(("s1t", "s2")), lambda r: r["cell"] == "f0")),
    "erx_f1h_opus": Run("F", "opus_high", "anthropic_r9b", 1,
                        subset(build_panel(("s1t", "s2")), lambda r: r["cell"] == "f1")),
    "erx_b1_opus": Run("B", "opus", "anthropic_r9a", 1, build_cells(("s1t",), ("b_list", "verify"))),
    "erx_b2_opus": Run("B", "opus", "anthropic_r9a", 1, build_cells(("s2",), ("b_list", "verify"))),
    "erx_a1_sonnet": Run("A", "sonnet", "anthropic_r9a", 1, subset(reads_from(3, build_a), half(0))),
    "erx_a2_sonnet": Run("A", "sonnet", "anthropic_r9b", 1, subset(reads_from(3, build_a), half(1))),
    "era1_astra": Run("A", "astra", "openai_r9", 1, build_a),
    "erx_h1_astra": Run("H", "astra", "openai_r9", 1, subset(build_h, half(0)), multiwoz=False),
    "erx_h2_astra": Run("H", "astra", "openai_r9", 1, subset(build_h, half(1)), multiwoz=False),
    "erx_b1_astra": Run("B", "astra", "openai_r9", 1, build_cells(("s1t",), ("b_list", "verify"))),
    "erx_b2_astra": Run("B", "astra", "openai_r9", 1, build_cells(("s2",), ("b_list", "verify"))),
    "erx_a3_sol": Run("A", "sol", "openai_r9", 1, reads_from(3, build_a)),
    "erx_f2_haiku": Run("F", "haiku_high", "anthropic_r9b", 1, reads_from(2, build_panel(("s1t", "s2")))),
    "erx_f2_luna": Run("F", "luna_high", "openai_r9", 1, reads_from(2, build_panel(("s1t", "s2")))),
    "erx_i3_sonnet": Run("I", "sonnet", "anthropic_r9b", 1, reads_from(3, build_i)),
    "erx_i3_sol": Run("I", "sol", "openai_r9", 1, reads_from(3, build_i)),
    "erx_a2_opus": Run("A", "opus", "anthropic_r9b", 1, reads_from(2, build_a)),
    "erx_h34_haiku": Run("H", "haiku", "anthropic_r9b", 2, reads_from(3, build_h), multiwoz=False),
    "erx_h34_luna": Run("H", "luna", "openai_r9", 2, reads_from(3, build_h), multiwoz=False),
    # Amendment R10-5 (PROTOCOL.md): items 1 and 2 of the credit decision of 2026-11-12.
    "era2_astra": Run("A2", "astra", "openai_r9", 1, build_s2),
    "erx_b3_opus": Run("B", "opus", "anthropic_r9a", 1, build_cells(("s3",), ("b_list", "verify"))),
    "erx_b3_astra": Run("B", "astra", "openai_r9", 1, build_cells(("s3",), ("b_list", "verify"))),
    # Amendment R10-6 (PROTOCOL.md): the forward release test of a tool edit written by Claude Opus 5.5.
    "erp_sonnet": Run("R", "sonnet", "anthropic_r9a", 1, build_r),
    "erp_sol": Run("R", "sol", "openai_r9", 1, build_r),
    # Amendment R10-7 (PROTOCOL.md): the returned flag, step 2 of A without the one-call limit.
    "erw_sonnet": Run("W", "sonnet", "anthropic_r9b", 1, build_w),
    "erw_haiku": Run("W", "haiku", "anthropic_r9b", 1, build_w),
    "erw_opus": Run("W", "opus", "anthropic_r9b", 1, build_w),
    # Amendment R10-12 (PROTOCOL.md): planned repeats of R10-7 (the same requests; only the run name in the custom_id).
    "erw2_haiku": Run("W", "haiku", "anthropic_r9b", 1, build_w),
    "erw3_haiku": Run("W", "haiku", "anthropic_r9b", 1, build_w),
    "erw2_sonnet": Run("W", "sonnet", "anthropic_r9b", 1, build_w),
    "erw2_opus": Run("W", "opus", "anthropic_r9b", 1, build_w),
    # Amendment R10-8 (PROTOCOL.md): later turns with a simulated traveller (synchronous; r10/turns.py).
    "ert_sonnet": Run("T", "sonnet", "anthropic_r9a", 1, build_t("t0")),
    "ert1_sonnet": Run("T", "sonnet", "anthropic_r9a", 1, build_t("t1")),
    # Amendment R10-13 (PROTOCOL.md): arm (a), travellers who require a hotel (Claude); arm (b), the GPT models.
    "eru_sonnet": Run("U", "sonnet", "anthropic_r9b", 1, build_u, pilot=2),
    "eru_haiku": Run("U", "haiku", "anthropic_r9b", 1, build_u, pilot=3),
    "eru_opus": Run("U", "opus", "anthropic_r9b", 1, build_u, pilot=1),
    "eru_sol": Run("U", "sol", "openai_r9", 1, build_u, pilot=3),
    "eru_astra": Run("U", "astra", "openai_r9", 1, build_u, pilot=1),
    # Amendment R10-14 (PROTOCOL.md): a service model rewrote the tool to steer the agents (cells th, tg; Haiku t0).
    "ers_sonnet": Run("S", "sonnet", "anthropic_r9b", 1, build_s, pilot=3),
    "ers_haiku": Run("S", "haiku", "anthropic_r9b", 1, build_s, pilot=5),
    # Amendment R10-15 (PROTOCOL.md): three rewrites each for H, G and no interest (N), Haiku, control in the batch.
    "erm_haiku": Run("M", "haiku", "anthropic_r9b", 1, build_m, pilot=3),
    # Amendment R10-16 (PROTOCOL.md): harmless control updates for the release rule (Haiku; batch 2 after batch 1).
    "erc_haiku": Run("C", "haiku", "anthropic_r9b", 1, build_c("control"), pilot=5),
    "erc2_haiku": Run("C", "haiku", "anthropic_r9b", 1, build_c("repeat")),
    # Amendment R10-17 (PROTOCOL.md): the planned verifier on the open models (DeepInfra, synchronous step run).
    "ery_deepseek": Run("Y", "deepseek", "deepinfra_main", 2, build_y, pilot=5),
    "ery_qwen": Run("Y", "qwen", "deepinfra_main", 2, build_y, pilot=5),
    "ery_gemma": Run("Y", "gemma", "deepinfra_main", 2, build_y, pilot=5),
    # Amendment R10-18 (PROTOCOL.md): the label test with one fixed definition (labeltest.py). Sonnet is in two runs,
    # because its bound does not fit one account: the no-type set on anthropic_r9b, the hotel-brief set on anthropic_r9a.
    "erl_sonnet": Run("L", "sonnet", "anthropic_r9b", 1, build_l(("no_type",)), pilot=5),
    "erl_sonnet_hb": Run("L", "sonnet", "anthropic_r9a", 1, build_l(("hotel",)), pilot=3),
    "erl_haiku": Run("L", "haiku", "anthropic_r9b", 2, build_l(("no_type", "hotel")), pilot=5),
    "erl_sol": Run("L", "sol", "openai_r9", 1, build_l(("no_type", "hotel")), pilot=5),
    "erl_luna": Run("L", "luna", "openai_r9", 2, build_l(("no_type", "hotel")), pilot=5),
    # Amendment R10-19 (PROTOCOL.md): the label test, third arm l_neutral (labeltest2.py). Sonnet: the no-type set only,
    # split over two accounts (labeltest2.SONNET_A); erl2_sonnet_b gets no pilot (labeltest2.py pilot-copy).
    "erl2_sol": Run("L2", "sol", "openai_r9", 1, build_l2, pilot=3),
    "erl2_luna": Run("L2", "luna", "openai_r9", 1, build_l2, pilot=3),
    "erl2_sonnet_a": Run("L2", "sonnet", "anthropic_r9b", 1, build_l2, pilot=3),
    "erl2_sonnet_b": Run("L2", "sonnet", "anthropic_r9a", 1, build_l2, pilot=1),
    "erl2_haiku": Run("L2", "haiku", "anthropic_r9a", 1, build_l2, pilot=3),
    "erl2_deepseek": Run("L2", "deepseek", "deepinfra_main", 1, build_l2, pilot=2),
    "erl2_qwen": Run("L2", "qwen", "deepinfra_main", 1, build_l2, pilot=2),
    "erl2_gemma": Run("L2", "gemma", "deepinfra_main", 1, build_l2, pilot=2),
    # Amendment R10-20 (PROTOCOL.md): release tests of harmless updates (harmless.py). Tool calls on OpenAI, form
    # answers on DeepInfra.
    "erk_sol": Run("K", "sol", "openai_r9", 1, build_k, pilot=2),
    "erk_luna": Run("K", "luna", "openai_r9", 1, build_k, pilot=2),
    "erk_deepseek": Run("K", "deepseek", "deepinfra_main", 1, build_k, pilot=2),
    "erk_qwen": Run("K", "qwen", "deepinfra_main", 1, build_k, pilot=2),
    "erk_gemma": Run("K", "gemma", "deepinfra_main", 1, build_k, pilot=2),
    # Amendment R10-21 (PROTOCOL.md): the label test in the tool channel (labeltest3.py; Sol 3, Luna 4 answers).
    "erl3_sol": Run("L3", "sol", "openai_r9", 1, build_l3, pilot=3),
    "erl3_luna": Run("L3", "luna", "openai_r9", 1, build_l3, pilot=3),
    # Amendment R10-22 (PROTOCOL.md): release tests of a field-order change and a second paraphrase (harmless2.py).
    "erk2_sol": Run("K2", "sol", "openai_r9", 1, build_k2, pilot=2),
    "erk2_luna": Run("K2", "luna", "openai_r9", 1, build_k2, pilot=2),
    # Amendment R10-23 (PROTOCOL.md): the steering runs when the agent can search again (steer3.py). One batch run per
    # round k of the conversations (erq<k>_<model>); the conversation pilot of erq1_<model> covers every round.
    **{f"erq{k}_{m}": Run("Q", m, a, reads, build_q(k))
       for m, a, reads in (("haiku", "anthropic_r9b", 1), ("sol", "openai_r9", 1), ("luna", "openai_r9", 2))
       for k in (1, 2, 3, 4)},
    # Amendment R10-24 (PROTOCOL.md): the replication of the two paraphrase flags with a fresh control (harmless3.py).
    "erk3_deepseek": Run("K3", "deepseek", "deepinfra_main", 1, build_k3, pilot=2),
    "erk3_luna": Run("K3", "luna", "openai_r9", 1, build_k3, pilot=2),
    # Amendment R10-25 (PROTOCOL.md): the held-out confirmation of the the paper repair results (confirm25.py), in the
    # order of the calls while the money holds. Sonnet only if it fits.
    "ern_deepseek": Run("V", "deepseek", "deepinfra_main", 1, build_v, pilot=4),
    "ern_qwen": Run("V", "qwen", "deepinfra_main", 1, build_v, pilot=4),
    "ern_gemma": Run("V", "gemma", "deepinfra_main", 1, build_v, pilot=4),
    "ern_luna": Run("V", "luna", "openai_r9", 1, build_v, pilot=4),
    "ern_sol": Run("V", "sol", "openai_r9", 1, build_v, pilot=3),
    "ern_haiku": Run("V", "haiku", "anthropic_r9a", 1, build_v, pilot=4),
    "ern_sonnet": Run("V", "sonnet", "anthropic_r9a", 1, build_v, pilot=2),
}
FILL = [n for n in RUNS if n.startswith("erx_") or n == "era1_astra"]

_cache = {}


def context():
    if "data" not in _cache:
        _cache["data"] = anth.multiwoz()
        _cache["g"] = grp.groups(_cache["data"], verbose=False)
    return _cache["data"], _cache["g"]


def requests(name):
    run = RUNS[name]
    data, g = context()
    reqs = run.build(name, run.model, run.reads, data, g)
    if run.exp == "V":  # amendment R10-25: held-out stage-1 dialogues only, in place of groups.assert_unprotected
        import confirm25
        confirm25.assert_stage1({r["custom_id"].split("-")[1] + ".json" for r in reqs})
        if "new_text_V" not in _cache:  # the verifier text of experiment B
            grp.assert_new_text(tools.NEW_TEXTS + forms10.NEW_TEXTS)
            _cache["new_text_V"] = True
    elif run.multiwoz:
        grp.assert_unprotected({r["custom_id"].split("-")[1] + ".json" for r in reqs}, data)
        if run.exp in ("A", "A2", "B", "Y") and "new_text_ok" not in _cache:  # the constructed tool and B texts
            grp.assert_new_text(tools.NEW_TEXTS + forms10.NEW_TEXTS)
            _cache["new_text_ok"] = True
        if run.exp == "R":  # amendment R10-6: the texts of the edited tool
            import release
            grp.assert_new_text(tools.NEW_TEXTS + release.new_texts())
        if run.exp in ("W", "T") and f"new_text_{run.exp}" not in _cache:  # amendments R10-7 and R10-8
            import flag
            import turns
            grp.assert_new_text(tools.NEW_TEXTS + flag.NEW_TEXTS + (turns.NEW_TEXTS if run.exp == "T" else ()))
            _cache[f"new_text_{run.exp}"] = True
        if run.exp == "U" and "new_text_U" not in _cache:  # amendment R10-13
            import flag
            import flag2
            grp.assert_new_text(tools.NEW_TEXTS + flag.NEW_TEXTS + flag2.NEW_TEXTS)
            _cache["new_text_U"] = True
        if run.exp == "S":  # amendment R10-14: the texts of the steered tools
            import steer
            grp.assert_new_text(tools.NEW_TEXTS + steer.new_texts())
        if run.exp == "M":  # amendment R10-15: the texts of the rewritten tools
            import steer2
            grp.assert_new_text(tools.NEW_TEXTS + steer2.new_texts())
        if run.exp == "C":  # amendment R10-16: the control updates keep every text of the original tool
            grp.assert_new_text(tools.NEW_TEXTS)
        if run.exp == "K" and "new_text_K" not in _cache:  # amendment R10-20: the paraphrase texts
            import harmless
            grp.assert_new_text(tools.NEW_TEXTS + harmless.NEW_TEXTS)
            _cache["new_text_K"] = True
        if run.exp in ("L3", "K2") and f"new_text_{run.exp}" not in _cache:  # R10-21 and R10-22: the tool texts
            import harmless2
            grp.assert_new_text(tools.NEW_TEXTS + (harmless2.NEW_TEXTS if run.exp == "K2" else ()))
            _cache[f"new_text_{run.exp}"] = True
        if run.exp in ("Q", "K3") and f"new_text_{run.exp}" not in _cache:  # R10-23 and R10-24: the new texts
            import flag
            import harmless3
            import steer
            import steer3
            grp.assert_new_text(tools.NEW_TEXTS + (flag.NEW_TEXTS + steer.new_texts() + steer3.NEW_TEXTS
                                                   if run.exp == "Q" else harmless3.NEW_TEXTS))
            _cache[f"new_text_{run.exp}"] = True
    else:  # constructed text: no sentence of 4 or more words from a main-study item
        import pairs
        grp.assert_new_text(pairs.NEW_TEXTS)
    ids = [r["custom_id"] for r in reqs]
    assert len(ids) == len(set(ids)), f"{name}: duplicate custom_id"
    assert all(len(i) <= 64 for i in ids), f"{name}: a custom_id is longer than 64 characters"
    provider = accounts.ACCOUNTS[run.account].provider
    assert provider == models.PROVIDER[run.model], f"{name}: {run.account} cannot serve {run.model}"
    return reqs


def digest(reqs):
    return hashlib.sha256("".join(json.dumps(r, sort_keys=True) + "\n" for r in reqs).encode()).hexdigest()


def section_hash(text=None):
    text = PROTOCOL.read_text() if text is None else text
    if SECTION not in text:
        return None
    body = text.split(SECTION, 1)[1]
    end = min([i for i in (body.find("\n## "),) if i >= 0] or [len(body)])
    return hashlib.sha256((SECTION + body[:end]).encode()).hexdigest()


def check_lock():
    h = section_hash()
    if h is None:
        sys.exit(f"Not run. {PROTOCOL.name} has no section {SECTION!r}. The predictions come first.")
    if not LOCK.exists() or json.loads(LOCK.read_text()).get("sha256") != h:
        sys.exit(f"Not run. The section {SECTION!r} of {PROTOCOL.name} differs from {LOCK.name}. A change after the lock "
                 f"goes under {AMEND!r}.")


def write_manifest(names=None):
    names = names or [n for n in RUNS if n.startswith(("era1", "erb", "eri", "erf", "ere", "erg"))]
    old = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    for n in names:
        reqs = requests(n)
        entry = {"requests": len(reqs), "sha256": digest(reqs)}
        if n in old and old[n] != entry:
            sys.exit(f"Not written. {n} differs from {MANIFEST.name}; a change after the manifest is an amendment.")
        old[n] = entry
        print(n, entry["requests"], entry["sha256"][:12])
    MANIFEST.write_text(json.dumps(old, indent=1, sort_keys=True))


def amend_manifest(amendment, names):
    """Replace the manifest entries of `names` after a recorded amendment of PROTOCOL.md ("### <amendment>" under
    "## Round 10 amendments"). The old entries stay in the manifest under "amendments"."""
    if f"### {amendment} " not in PROTOCOL.read_text().split(AMEND, 1)[-1]:
        sys.exit(f"Not written. {PROTOCOL.name} has no amendment {amendment!r} under {AMEND!r}.")
    man = json.loads(MANIFEST.read_text())
    log = man.setdefault("amendments", [])
    for n in names:
        reqs = requests(n)
        entry = {"requests": len(reqs), "sha256": digest(reqs)}
        log.append({"amendment": amendment, "run": n, "old": man.get(n), "new": entry})
        man[n] = entry
        print(n, entry["requests"], entry["sha256"][:12], "(was", (log[-1]["old"] or {}).get("sha256", "")[:12] + ")")
    MANIFEST.write_text(json.dumps(man, indent=1, sort_keys=True))


def verify():
    """Rebuild every run of the manifest and compare it with its entry. Offline."""
    man = json.loads(MANIFEST.read_text())
    bad = [n for n, e in sorted(man.items()) if n != "amendments"
           and {"requests": len(r := requests(n)), "sha256": digest(r)} != e]
    print(f"{len(man) - ('amendments' in man)} manifest entries rebuilt; differ: {bad or 'none'}")
    return not bad


def main(name):
    import budget_gate
    run = RUNS[name]
    if run.exp == "T":  # amendment R10-8: synchronous conversations, its own client and checks
        import turns
        return turns.main(name, run.build.arm)
    step = sys.argv[1] if len(sys.argv) > 1 else ""
    if step in ("pilot", "submit", "run"):  # "run": the synchronous step of a DeepInfra run (R10-17)
        check_lock()
        if run.exp == "H":  # experiment H has its own locked section (r10/protocol_h.py)
            import protocol_h
            protocol_h.check()
        if run.exp == "R":  # amendment R10-6 holds the rewrite text and the SHA-256 of release/edit.json
            import release
            release.check_amendment()
            if "--approve" in sys.argv and float(sys.argv[sys.argv.index("--approve") + 1]) > release.MAX_BOUND:
                sys.exit(f"Not run. {name}: R10-6 allows at most {release.MAX_BOUND:.2f} USD per run.")
        if run.exp == "W":  # amendment R10-7 holds the new texts
            import flag
            flag.check_amendment()
            if not name.startswith("erw_") and "### R10-12 " not in PROTOCOL.read_text().split(AMEND, 1)[-1]:
                sys.exit(f"Not run. {name}: {PROTOCOL.name} has no amendment R10-12.")
            if "--approve" in sys.argv and float(sys.argv[sys.argv.index("--approve") + 1]) > flag.MAX_BOUND:
                sys.exit(f"Not run. {name}: R10-7 allows at most {flag.MAX_BOUND:.2f} USD per run.")
        if run.exp in ("U", "S"):  # amendments R10-13 and R10-14 hold their texts (R10-14 also the edit SHA-256)
            mod = __import__("flag2" if run.exp == "U" else "steer")
            mod.check_amendment()
            if "--approve" in sys.argv and float(sys.argv[sys.argv.index("--approve") + 1]) > mod.MAX_BOUND:
                sys.exit(f"Not run. {name}: {mod.AMENDMENT.strip('# ')} allows at most {mod.MAX_BOUND:.2f} USD per run.")
        if run.exp == "Y":  # amendment R10-17: its texts and its own money limit on deepinfra_main
            import verify3
            verify3.check_amendment()
            if "--approve" in sys.argv:
                bound = float(sys.argv[sys.argv.index("--approve") + 1])
                if bound > verify3.MAX_BOUND:
                    sys.exit(f"Not run. {name}: R10-17 allows at most {verify3.MAX_BOUND:.2f} USD per step.")
                verify3.check_shared(bound)
        if run.exp in ("M", "C"):  # amendments R10-15 and R10-16: their checks and the shared money limit
            import steer2
            mod = __import__("steer2" if run.exp == "M" else "control")
            mod.check_amendment()
            if "--approve" in sys.argv:
                bound = float(sys.argv[sys.argv.index("--approve") + 1])
                if bound > steer2.MAX_BOUND:
                    sys.exit(f"Not run. {name}: R10-15 and R10-16 allow at most {steer2.MAX_BOUND:.2f} USD per step.")
                steer2.check_shared(bound)
        reserve = budget_gate.RESERVE
        if run.exp == "L":  # amendment R10-18: its texts, its step limit, and its reserve (labeltest.RESERVE)
            import labeltest
            labeltest.check_amendment()
            reserve = labeltest.RESERVE
            if "--approve" in sys.argv and float(sys.argv[sys.argv.index("--approve") + 1]) > labeltest.MAX_BOUND:
                sys.exit(f"Not run. {name}: R10-18 allows at most {labeltest.MAX_BOUND:.2f} USD per step.")
        if run.exp in ("L2", "K"):  # amendments R10-19 and R10-20: their texts, the step limit and the shared caps
            import labeltest2
            import newmoney
            __import__("labeltest2" if run.exp == "L2" else "harmless").check_amendment()
            reserve = labeltest2.RESERVE
            if step == "pilot" and name in labeltest2.NO_PILOT:
                sys.exit(f"Not run. {name} has no pilot: run `r10/labeltest2.py pilot-copy`.")
            if "--approve" in sys.argv:
                bound = float(sys.argv[sys.argv.index("--approve") + 1])
                if bound > labeltest2.MAX_BOUND:
                    sys.exit(f"Not run. {name}: R10-19 and R10-20 allow at most {labeltest2.MAX_BOUND:.2f} USD per step.")
                newmoney.check(run.account, bound)
        if run.exp in ("L3", "K2"):  # amendments R10-21 and R10-22: their texts, the step limit and their own cap
            import labeltest3
            import newmoney
            __import__("labeltest3" if run.exp == "L3" else "harmless2").check_amendment()
            reserve = labeltest3.RESERVE
            if "--approve" in sys.argv:
                bound = float(sys.argv[sys.argv.index("--approve") + 1])
                if bound > labeltest3.MAX_BOUND:
                    sys.exit(f"Not run. {name}: R10-21 and R10-22 allow at most {labeltest3.MAX_BOUND:.2f} USD per step.")
                newmoney.check(run.account, bound, newmoney.R21)
        if run.exp in ("Q", "K3"):  # amendments R10-23 and R10-24: their texts, the step limit and the cap group R23
            import newmoney
            import steer3
            mod = __import__("steer3" if run.exp == "Q" else "harmless3")
            mod.check_amendment()
            reserve = steer3.RESERVE
            if run.exp == "Q" and step == "pilot":  # the conversation pilot of R10-23 (every round, synchronous)
                if steer3.parse_run(name)[1] != 1:
                    sys.exit(f"Not run. {name}: the conversation pilot of {steer3.run_name(run.model, 1)} covers every "
                             f"round.")
                return steer3.pilot(run.model, sys.argv[sys.argv.index("--approve") + 1]
                                    if "--approve" in sys.argv else None)
            if "--approve" in sys.argv:
                bound = float(sys.argv[sys.argv.index("--approve") + 1])
                if bound > mod.MAX_BOUND:
                    sys.exit(f"Not run. {name}: {mod.AMENDMENT.strip('# ')} allows at most {mod.MAX_BOUND:.2f} USD per "
                             f"step.")
                newmoney.check(run.account, bound, newmoney.R23)
                if run.exp == "Q" and step == "submit":
                    steer3.check_projection(name, bound)
        if run.exp == "V":  # amendment R10-25: its texts, the step limit, the cap group R25 and the R10-23 projection
            import confirm25
            import newmoney
            confirm25.check_amendment()
            reserve = confirm25.RESERVE
            if "--approve" in sys.argv:
                bound = float(sys.argv[sys.argv.index("--approve") + 1])
                if bound > confirm25.MAX_BOUND:
                    sys.exit(f"Not run. {name}: R10-25 allows at most {confirm25.MAX_BOUND:.2f} USD per step.")
                newmoney.check(run.account, bound, newmoney.R25)
                confirm25.check_projection(name, bound)
        if "--approve" in sys.argv:
            bound = float(sys.argv[sys.argv.index("--approve") + 1])
            if not budget_gate.fits(run.account, bound, reserve):
                sys.exit(f"Not run. {name}: a bound of {bound:.2f} USD does not fit the free money of {run.account} "
                         f"minus the reserve ({reserve:.2f} USD).")
    if step in ("submit", "run"):
        man = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
        if man.get(name, {}).get("sha256") != digest(requests(name)):
            sys.exit(f"Not run. {name}: the requests differ from {MANIFEST.name} or have no entry.")
    provider = accounts.ACCOUNTS[run.account].provider
    if run.pilot:  # a smaller pilot (R10-13, R10-14); anth.pilot_sample serves both clients
        anth.PILOT_PER_CELL = run.pilot
    if provider == "anthropic":
        return anth.main(name, lambda: requests(name), PLANNING_OUT[provider], account=run.account)
    try:
        return oc.main(name, lambda: requests(name), PLANNING_OUT[provider], account=run.account)
    except RuntimeError as x:  # R10-19 and R10-20: a prepaid DeepInfra balance that is empty answers HTTP 402
        if run.exp in ("L2", "K", "K3", "V") and provider == "deepinfra" and ": HTTP 402 " in str(x):
            sys.exit(f"Stopped. {name}: DeepInfra answered HTTP 402 (no money left on the prepaid balance; no charge "
                     f"for that call). The answers so far stay in {name}/responses.jsonl, and the ledger row holds the "
                     f"money used. After a top-up, run the same step again: it sends only the requests without a "
                     f"stored answer, at a new printed bound.")
        raise


def write_scripts():
    """One thin script per run, so that lib/watch.py can run its fetch step. Never overwrites a file."""
    for n in RUNS:
        path = HERE / f"{n}.py"
        if path.exists():
            continue
        path.write_text(f'"""Round 10 run {n} (r10/runs.py)."""\nimport pathlib\nimport sys\n\n'
                        f'sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\nimport runs  # noqa: E402\n\n'
                        f'runs.main("{n}")\n')


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "manifest":
        write_manifest(sys.argv[2:] or None)
    elif cmd == "list":
        for n, r in RUNS.items():
            print(n, r.exp, r.model, r.account, r.reads)
    elif cmd == "scripts":
        write_scripts()
    elif cmd == "amend":
        amend_manifest(sys.argv[2], sys.argv[3:])
    elif cmd == "verify":
        sys.exit(0 if verify() else 1)
    else:
        sys.exit(__doc__)
