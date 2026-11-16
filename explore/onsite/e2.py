"""E2 (PROTOCOL.md): the three P3 on-site arms on the Claude 5.5 models through the Message Batches API.

38 P1 cases whose text says "on-site" x 3 arms x 5 reads x 3 models, effort low, max_tokens 4096.
The arms are P3's A, B, and C:
  orig     the original text and schema (the P1 request)
  office   the text with "on-site" replaced by "in the office", original schema
  renamed  the original text, attributes renamed work_mode and office_region with their values listed

Two interpreters, because the repository needs numpy and scipy and the batch steps need the anthropic package:
  harness/.venv/bin/python onsite/e2.py freeze    builds the prompts, checks them against P3, writes prompts.json
  explore/.venv/bin/python -I onsite/e2.py estimate          (and pilot, submit, fetch) read prompts.json only
"""
import dataclasses
import importlib.util
import json
import pathlib
import re
import sys

sys.dont_write_bytecode = True  # the P1, P3, and repository modules sit in folders that E2 must not write to

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
PROTOTYPES = EXPLORE.parent
sys.path.insert(0, str(EXPLORE / "lib"))
import anth  # noqa: E402

REPO = anth.HARNESS / "harness"
PROMPTS = HERE / "prompts.json"
MODELS = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5"}
ARMS = ("orig", "office", "renamed")
READS = range(1, 6)
EFFORT, MAX_TOKENS = "low", 4096
ATTR_LINE = ("Attributes that requirements may refer to: remote, site",
             "Attributes that requirements may refer to: work_mode (\"remote\" or \"on_site\"), "
             "office_region (\"north\" or \"south\")")
RULE = ('(true/false for remote,\n  "north"/"south" for site)',
        '("remote"/"on_site" for work_mode,\n  "north"/"south" for office_region)')


def onsite_cases():
    sys.path.insert(0, str(REPO / "src"))
    from sib.objects import load_cases_dir

    cases = load_cases_dir(REPO / "cases" / "dev")
    p1 = {json.loads(line)["case_id"] for line in (PROTOTYPES / "p1_saturation" / "raw.jsonl").read_text().splitlines()}
    ids = sorted(c for c in p1 if "on-site" in (cases[c].prose or "").lower())
    assert len(ids) == 38, len(ids)
    return {c: cases[c] for c in ids}


def prompts(case):
    """(system, user) for each arm."""
    from si_eval.extraction_task import build_extraction_request

    orig = build_extraction_request(case, "anthropic", "e2")
    office = build_extraction_request(
        dataclasses.replace(case, prose=re.sub("on-site", "in the office", case.prose, flags=re.IGNORECASE)), "anthropic", "e2")
    assert ATTR_LINE[0] in orig.user_content and RULE[0] in orig.user_content, "the repository prompt changed"
    renamed = orig.user_content.replace(*ATTR_LINE).replace(*RULE)
    return {"orig": (orig.system, orig.user_content), "office": (office.system, office.user_content),
            "renamed": (orig.system, renamed)}


def load_p3():
    spec = importlib.util.spec_from_file_location("p3_schema_run", PROTOTYPES / "p3_schema" / "run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_p3(cases, table):
    """Rebuild each arm as P3's run.py built it and compare it with the E2 prompt, byte for byte."""
    p3 = load_p3()
    unequal, same_as_orig = [], []
    for cid, case in cases.items():
        a = p3.build_extraction_request(case, "anthropic", p3.MODEL)
        # P3 built arm B inline in main(), so this line copies it from p3_schema/run.py.
        b = p3.build_extraction_request(
            dataclasses.replace(case, prose=re.sub(r"on-site", "in the office", case.prose, flags=re.I)), "anthropic", p3.MODEL)
        p3_arms = {"orig": (a.system, a.user_content), "office": (b.system, b.user_content),
                   "renamed": (a.system, p3.renamed_prompt(a.user_content))}
        unequal += [(cid, arm) for arm in ARMS if table[cid][arm] != p3_arms[arm]]
        same_as_orig += [(cid, arm) for arm in ARMS[1:] if table[cid][arm] == table[cid]["orig"]]
    assert not unequal, f"E2 prompts differ from P3: {unequal[:5]}"
    assert not same_as_orig, f"an arm equals the original prompt: {same_as_orig[:5]}"
    assert all("on-site" not in table[c]["office"][1].lower() for c in cases)
    print(f"P3 prompt check: {len(cases) * len(ARMS)} of {len(cases) * len(ARMS)} (system, user) pairs equal the P3 "
          f"construction ({len(cases)} cases x {len(ARMS)} arms); the office and renamed prompts differ from the "
          f"original in {len(cases)} of {len(cases)} cases each")


def freeze():
    cases = onsite_cases()
    table = {cid: prompts(case) for cid, case in cases.items()}
    check_p3(cases, table)
    PROMPTS.write_text(json.dumps({cid: {arm: {"system": s, "user": u} for arm, (s, u) in arms.items()}
                                   for cid, arms in table.items()}, indent=1))
    print(f"wrote {PROMPTS}")


def custom_id(short, arm, read, case_id):
    return f"{short}_{arm}_r{read}_{case_id}"


def parse_id(cid):
    short, arm, read, case_id = cid.split("_", 3)
    return MODELS[short], arm, int(read[1:]), case_id


def build():
    if not PROMPTS.exists():
        sys.exit(f"{PROMPTS.name} is missing. Run the freeze step with the repository venv first.")
    table = json.loads(PROMPTS.read_text())
    assert len(table) == 38 and all(tuple(arms) == ARMS for arms in table.values()), "prompts.json is not the E2 table"
    return [anth.request(custom_id(short, arm, k, cid), model, EFFORT, MAX_TOKENS,
                         user=table[cid][arm]["user"], system=table[cid][arm]["system"])
            for short, model in MODELS.items() for cid in table for arm in ARMS for k in READS]


if __name__ == "__main__":
    if sys.argv[1:] == ["freeze"]:
        freeze()
    else:
        anth.main("e2", build, planning_out=400, account="anthropic_old")
