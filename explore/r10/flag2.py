"""Amendment R10-13 (PROTOCOL.md): the returned flag with travellers who require a hotel, and the GPT models.
Exploratory, for the paper. The design copies R10-7 (r10/flag.py) and R10-12 (no one-call sentence).

Arm (a), Claude models (runs eru_sonnet, eru_haiku, eru_opus). Sample (`sample_a`): the stage-1 t0 rows of a source run
on the 59 prefixes of experiment A whose brief sets type hotel. A row goes in when its call is a valid search whose type
keeps hotel and not guesthouse, and the same search without its type finds 1 or more guesthouses (N). Source runs:
Sonnet era1_sonnet, Opus era1_opus, Haiku era1_sonnet (Haiku answers after the stored Sonnet call, because Haiku set a
hotel-only type in only 11 calls on these prefixes, and only 2 of them, in 1 dialogue, have a guesthouse with N >= 1).
The tool result is constructed: `{"results": [], "total": 0}` for every sampled call, also when the real search finds a
hotel (in every sampled call it does). The flag arm adds `flag.flag_line(N)`. Two text conditions: "brief" (the prefix
unchanged) and "explicit" (EXPLICIT added to the last traveller turn of the prefix). Cells plain, flag, xplain, xflag.
Outcome (`classify_a`): widen_silent, widen_told, kept, tell, neither, invalid (see the function).

Arm (b), GPT models (runs eru_sol, eru_astra). Sample (`sample_b`): the R10-7 rule (flag.sample) on era1_sol (reads 1 and
2) and era1_astra (read 1), without the calls whose brief sets type hotel. Requests: as stage2.requests for OpenAI, with
the system item replaced by flag.multi_system("t0"). Cells plain and flag. Outcome: flag.classify, unchanged.
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(HERE))
import briefsearch as bs  # noqa: E402
import flag  # noqa: E402
import gold  # noqa: E402
import models  # noqa: E402
import stage2  # noqa: E402
import tools  # noqa: E402

AMENDMENT = "### R10-13 "
MODELS_A = ("sonnet", "haiku", "opus")
MODELS_B = ("sol", "astra")
SOURCE_A = {"sonnet": "sonnet", "haiku": "sonnet", "opus": "opus"}  # the model whose stored stage-1 call is replayed
CELLS_A = ("plain", "flag", "xplain", "xflag")
ARMS = flag.ARMS
MAX_BOUND = 2.50  # USD per run (pilot or batch)
EXPLICIT = "It must be a hotel, not a guesthouse."
NEW_TEXTS = (EXPLICIT,)
EMPTY = json.dumps(bs.result_rows([]))  # the tool result of stage2.py when the search finds nothing


def spec_ids(data):
    """The prefixes of experiment A (runs.context group "booked") whose brief sets type hotel, without ".json"."""
    import runs
    _, g = runs.context()
    return {d.removesuffix(".json") for d in g["booked"] if gold.brief_type(data[d]) == "hotel"}


def guesthouses(fields, db):
    """N: the venues that the same search without its type finds; all are guesthouses in a sampled call."""
    return [v for v in bs.search(db, {**fields, "type": None}) if v["type"] == "guesthouse"]


def sample_a(model, db=None):
    """[(stage-1 row, fields, N, real count)] of era1_<SOURCE_A[model]>, sorted by custom_id. real count: the hotels
    that the call finds in the venue data (a description; the agent sees an empty result)."""
    import runs
    db = db or gold.hotel_db()
    data, _ = runs.context()
    spec = spec_ids(data)
    out = []
    for row in stage2.rows_of(EXPLORE / f"era1_{SOURCE_A[model]}", "raw"):
        if row.get("type", "succeeded") != "succeeded" or "-t0-" not in row["custom_id"]:
            continue
        if row["custom_id"].split("-")[1] not in spec:
            continue
        kind, fields = tools.parse_call(row, "t0")
        if kind != "search" or not gold.hides_guesthouse(fields.get("type")):
            continue
        n = len(guesthouses(fields, db))
        if n == 0:
            continue
        out.append((row, fields, n, len(bs.search(db, fields))))
    return sorted(out, key=lambda x: x[0]["custom_id"])


def explicit_user(content):
    """The stage-1 user message with EXPLICIT added to the last traveller turn (the prefix ends with that turn)."""
    assert isinstance(content, str) and content.rsplit("\n", 1)[-1].startswith("Traveller: "), content[-80:]
    return content.rstrip() + " " + EXPLICIT


def build_a(name, model, reads, data, g):
    """Cells plain, flag, xplain, xflag for each sampled stage-1 call (one answer each; `reads` must be 1)."""
    assert reads == 1 and model in MODELS_A, (name, model, reads)
    db = gold.hotel_db()
    source = SOURCE_A[model]
    stage1 = stage2.build_stage1(source, f"era1_{source}")
    system = flag.multi_system("t0")
    out = []
    for row, fields, n, _ in sample_a(model, db):
        first = stage1[row["custom_id"]]["params"]["messages"][0]
        call = row["tool_calls"][0]
        _, did, _, read = row["custom_id"].split("-")
        for cell in CELLS_A:
            content = EMPTY + ("\n" + flag.flag_line(n) if cell.endswith("flag") else "")
            user = first if not cell.startswith("x") else {"role": "user", "content": explicit_user(first["content"])}
            messages = [user, {"role": "assistant", "content": flag.strip_thinking(row["content"])},
                        {"role": "user", "content": [{"type": "tool_result", "tool_use_id": call["id"],
                                                      "content": content}]},
                        {"role": "system", "content": stage2.STEP2_TEXT}]
            out.append(models.request(model, f"{name}-{did}-{cell}-{read}", None, system, None,
                                      tools=tools.TOOLS["t0"], messages=messages, cell=cell))
    return out


def sample_b(model, db=None):
    """[(stage-1 row, fields, N)] of the R10-7 rule (flag.sample) on era1_<model>, without hotel briefs."""
    import runs
    data, _ = runs.context()
    return [x for x in flag.sample(model, db) if gold.brief_type(data[x[0]["custom_id"].split("-")[1] + ".json"]) != "hotel"]


def build_b(name, model, reads, data, g):
    """Arms plain and flag for each sampled stage-1 call of a GPT model (one answer each; `reads` must be 1)."""
    assert reads == 1 and model in MODELS_B, (name, model, reads)
    db = gold.hotel_db()
    stage1 = stage2.build_stage1(model, f"era1_{model}")
    old, new = tools.tool_system("t0"), flag.multi_system("t0")
    out = []
    for row, fields, n in sample_b(model, db):
        items = list(stage1[row["custom_id"]]["body"]["input"])
        assert items[0] == {"role": "system", "content": old}, row["custom_id"]
        items[0] = {"role": "system", "content": new}
        call = row["tool_calls"][0]
        _, did, _, read = row["custom_id"].split("-")
        for arm in ARMS:
            content = EMPTY + ("\n" + flag.flag_line(n) if arm == "flag" else "")
            full = items + list(row["output_items"]) + [
                {"type": "function_call_output", "call_id": call["id"], "output": content},
                {"role": "system", "content": stage2.STEP2_TEXT}]
            out.append(models.request(model, f"{name}-{did}-{arm}-{read}", None, None, None, tools=tools.TOOLS["t0"],
                                      input_items=full, cell=arm))
    return out


def build(name, model, reads, data, g):
    return build_a(name, model, reads, data, g) if model in MODELS_A else build_b(name, model, reads, data, g)


def told(text):
    """The word rule of R10-7: the text names a guesthouse or the hotel-only limit, or asks about the type of place."""
    return bool(flag.GUEST_OR_LIMITED.search(text or "")) or flag.asks_type(text or "")


def classify_a(row):
    """(kind, details) of one arm-(a) answer. Fixed in R10-13 before any call.
    - widen_silent: a search_hotels call whose type does not hide guesthouses (null, "any", or a list that holds
      guesthouse), and the text of the same answer does not match `told`.
    - widen_told: the same call, and the text matches `told`.
    - kept: a search call whose type keeps hotel and not guesthouse.
    - tell: no call and a text that is not empty (the agent tells or asks the traveller). details: told(text).
    - neither: no call and no text. invalid: the row failed, stopped at the length limit, or holds a call that does
      not parse as one search."""
    kind, details = flag.classify(row)
    if kind == "widen":
        return ("widen_told" if told(row.get("text")) else "widen_silent"), details
    if kind in ("tell", "other"):
        return "tell", {"word": told(row.get("text"))}
    return kind, details


def amendment_text():
    import runs
    text = runs.PROTOCOL.read_text().split(runs.AMEND, 1)[-1]
    if AMENDMENT not in text:
        return None
    body = text.split(AMENDMENT, 1)[1]
    ends = [i for i in (body.find("\n## "), body.find("\n### ")) if i >= 0]
    return AMENDMENT + (body[:min(ends)] if ends else body)


def check_amendment():
    """R10-13 is in PROTOCOL.md under the round-10 amendments and holds EXPLICIT and the R10-7 texts verbatim."""
    text = amendment_text()
    if text is None:
        sys.exit(f"Not run. PROTOCOL.md has no amendment {AMENDMENT.strip()!r}.")
    flat = " ".join(text.split())
    missing = [t for t in (EXPLICIT, flag.MULTI_ASK, flag.MULTI_END, flag.flag_line(1),
                           flag.flag_line(2).replace("2 guesthouses", "N guesthouses")) if t not in flat]
    if missing:
        sys.exit(f"Not run. R10-13 does not hold the text {missing[0]!r} verbatim.")


if __name__ == "__main__":
    import collections
    db = gold.hotel_db()
    for m in MODELS_A:
        s = sample_a(m, db)
        print(m, "(source", SOURCE_A[m] + ")", len(s), "calls,", len({r["custom_id"].split("-")[1] for r, *_ in s}),
              "dialogues; real hotel count of the call", dict(collections.Counter(min(x[3], 3) for x in s)),
              "(3 = 3 or more); N", dict(sorted(collections.Counter(x[2] for x in s).items())))
    for m in MODELS_B:
        s = sample_b(m, db)
        print(m, len(s), "calls,", len({r["custom_id"].split("-")[1] for r, _, _ in s}), "dialogues")
