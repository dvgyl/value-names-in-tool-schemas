"""Request test of zruns on the MultiWOZ files (no API call). Usage: python3 -I r9/additions/test_runs.py

It checks the dialogue groups, the Z1 text edit on all 994 dialogues, the Z2 prefixes, the model settings, and that the
request count per model and run equals review/plan13/r9_counts.py --balance.
"""
import collections
import json
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import zforms  # noqa: E402
import zruns  # noqa: E402
from zforms import anth, common  # noqa: E402

COUNTS = zforms.EXPLORE.parents[1] / "review" / "plan13" / "r9_counts.py"
FULL = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5", "luna": "gpt-6-luna", "sol": "gpt-6.1-sol",
        "deepseek": "DeepSeek-V4.1-Flash", "qwen": "Qwen3.8-27B", "gemma": "gemma-4-31B-it"}
RUN_OF = {"ez1": "Z1", "ez2": "Z2", "ez3": "Z3", "eb2": "B2", "eb3": "B3", "eb4": "B4"}
# Batch limits of the provider docs (requests, bytes), with a margin; not reread on 2026-11-03, so UNVERIFIED.
# Anthropic: 100,000 requests or 256 MB per Message Batch. OpenAI: 50,000 requests and 200 MB per input file.
LIMITS = {"anthropic": (100_000, 200e6), "openai": (50_000, 180e6)}


def plan_counts():
    """{(run, model): calls} from the table that r9_counts.py --balance prints."""
    lines = subprocess.run([sys.executable, "-I", str(COUNTS), "--balance"], capture_output=True, text=True,
                           check=True).stdout.splitlines()
    runs = [c.strip() for c in lines[0].split("|")[2:-2]]
    out = {}
    for line in lines[2:]:
        cells = [c.strip() for c in line.split("|")[1:-1]]
        for run, value in zip(runs, cells[1:-1]):
            if value and not cells[0].startswith("**"):
                out[(run, cells[0].strip("`"))] = int(value.replace(",", ""))
    return out


def test_groups(data, g):
    booked = collections.Counter(g.venue[d]["type"] for d in g.booked)
    assert booked == {"guesthouse": 355, "hotel": 199}, booked  # review/plan13/revealed_r9b.out
    assert collections.Counter(g.venue[d]["type"] for d in g.s2 if d in g.venue)["hotel"] == 293  # addon-opus D8
    assert set(g.frame500) <= set(g.t994) and len(set(g.frame500)) == 500
    assert set(g.t994) <= set(g.s1) and not set(g.s1) & set(g.rest) and set(g.s2) <= set(g.rest)
    assert collections.Counter(g.brief[d] for d in g.t994) == {None: 807, "hotel": 109, "guesthouse": 78}  # D3


def test_text_edit_on_all_994(data, g):
    """Only a traveller's "hotel" word may change, each into its own phrase, and only outside a venue name."""
    kept = replaced = 0
    names = [h["name"] for h in zforms.HOTELS if "hotel" in h["name"].split()]
    for d in g.t994:
        pattern, words = [], []
        for i, t in enumerate(data[d]["log"]):
            turn = t["text"].strip()
            if i % 2:
                pattern.append(re.escape("Assistant: " + turn))
                continue
            pieces, found = zforms.WORD.split(turn), list(zforms.WORD.finditer(turn))
            pattern.append(re.escape("Traveller: " + pieces[0]) + "".join(
                f"({re.escape(w.group(0))}|{re.escape(zforms._place_to_stay(w.group(0)))})" + re.escape(p)
                for w, p in zip(found, pieces[1:])))
            words += [(turn, w) for w in found]
        m = re.fullmatch("\\n".join(pattern), zforms.edited_text(data[d]))
        assert m, d
        for (turn, w), got in zip(words, m.groups()):
            before = (re.findall(r"[\w'&-]+", turn[:w.start()]) or [""])[-1].lower()
            before = {"marriot": "marriott"}.get(before, before)  # the misspelt name in MUL0601
            in_name = any(n == f"{before} hotel" or n.endswith(f" {before} hotel") for n in names)
            assert (got == w.group(0)) == in_name, (d, w.group(0), before, got)
            kept += got == w.group(0)
            replaced += got != w.group(0)
    print(f"  text edit: {replaced} words replaced, {kept} kept inside a venue name, in {len(g.t994)} dialogues")


def test_prefixes(data, g):
    for d in g.booked:
        log, end = data[d]["log"], zforms.prefix_end(data[d])
        assert end % 2 == 0 and zforms.WORD.search(log[end]["text"]), d
        assert not any(zforms.WORD.search(t["text"]) for k, t in enumerate(log[:end]) if k % 2 == 0), d
        assert common.dialogue_text(data[d]).startswith(zforms.prefix_text(data[d])), d


def test_requests(data, g):
    plan, mine = plan_counts(), collections.Counter()
    for name, run in zruns.RUNS.items():
        reqs = zruns.requests(name, data, g)
        for model, n in run.counts.items():
            mine[(RUN_OF[name[:3]], FULL[model])] += n + run.pilot
        ids = [r["custom_id"] for r in reqs]
        assert len(ids) == len(set(ids)) and all(len(i) <= 64 for i in ids), name
        seen = set()
        for r in reqs:
            _, d, cell, read, model = common.split_custom_id(r["custom_id"])
            if (cell, model) in seen:
                continue
            seen.add((cell, model))
            check_request(r, d, zruns.CELLS[cell], model, data)
        provider = zruns.accounts.ACCOUNTS[run.account].provider
        if provider in LIMITS:
            size = sum(len(json.dumps(r).encode()) for r in reqs)
            assert len(reqs) <= LIMITS[provider][0] and size <= LIMITS[provider][1], (name, len(reqs), size)
        if run.pilot:
            anth.PILOT_PER_CELL = run.pilot
            sample = anth.pilot_sample(reqs, anth.cell)
            assert collections.Counter(anth.cell(r)[0] for r in sample) == dict.fromkeys(
                (FULL[m] for m in run.counts), run.pilot), name
        print(f"  {name}: {len(reqs)} requests on {run.account}, cells {sorted({c for c, _ in seen})}")
    wanted = {k: v for k, v in plan.items() if k[0] in RUN_OF.values()}
    assert dict(mine) == wanted, (dict(mine), wanted)


def check_request(r, d, cell, model, data):
    form = zforms.FORMS[cell.form]
    system = zforms.framed(form.system) if cell.frame == "accommodation" else form.system
    user = zforms.TEXTS[cell.text](data[d])
    if model in ("haiku", "sonnet"):
        p = r["params"]
        thinking, effort = {"haiku": ({"type": "disabled"}, "medium"), "sonnet": ({"type": "between_tools"}, "high")}[model]
        assert (p["model"], p["thinking"], p["output_config"]["effort"], p["max_tokens"]) == (
            FULL[model], thinking, effort, 4096), p
        assert p["system"] == system and p["messages"] == [{"role": "user", "content": user}]
        assert p["output_config"]["format"] == {"type": "json_schema", "schema": form.schema}
        return
    b = r["body"]
    msgs = b.get("input") or b["messages"]
    assert msgs == [{"role": "system", "content": system}, {"role": "user", "content": user}]
    if model in ("luna", "sol"):
        assert (b["model"], b["reasoning"], b["max_output_tokens"]) == (FULL[model], {
            "effort": {"luna": "none", "sol": "low"}[model]}, 4000), b
        assert b["text"]["format"]["schema"] == form.schema and b["text"]["format"]["strict"]
    else:
        assert b["model"].endswith(FULL[model]) and b["response_format"]["json_schema"]["schema"] == form.schema
        assert b == zruns.ds.request(zruns.ds.MODELS[b["model"]], r["custom_id"], user, system, form.schema)["body"], b


if __name__ == "__main__":
    data = anth.multiwoz()
    g = zruns.groups(data)
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(data, g)
            print("ok", name)
    print("zruns test passed")
