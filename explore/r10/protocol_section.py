"""Write the PROTOCOL.md section "## Round 10 runs" (wave 1: A, B, I, E, F, G) and its lock. Offline.

The experiment blocks are copied verbatim from ROUND10-EXPERIMENT-PLAN.md; every fixed prompt text comes from the code
constants, so no text is typed twice. Experiment H gets its own section later. The script refuses to write a second
section or to overwrite the lock.
Usage (from explore/): .venv/bin/python -I r10/protocol_section.py print | write
"""
import datetime
import inspect
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import forms10  # noqa: E402
import models  # noqa: E402
import runs  # noqa: E402
import textedit  # noqa: E402
import tools  # noqa: E402
import zforms  # noqa: E402

PLAN = HERE.parents[2] / "ROUND10-EXPERIMENT-PLAN.md"  # explore/r10 -> explore -> prototypes -> improvement-plan
ACTION = HERE.parents[2] / "review" / "plan15" / "ACTION-PLAN.md"


def block(text, head, next_heads):
    start = text.index(head)
    ends = [text.index(h, start + 1) for h in next_heads if h in text[start + 1:]]
    return text[start:min(ends)].strip()


def section():
    plan, action = PLAN.read_text(), ACTION.read_text()
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rule = next(line for line in plan.splitlines() if line.startswith("- **The trade rule**"))
    diffs = block(action, "| # | Difference | Reason |", ["\n## 1. Critical path"])
    parts = [
        runs.SECTION + " (wave 1: A, B, I, E, F, G)",
        "",
        f"Written {now}, before any round-10 call. Exploratory. Authority: an internal file "
        "(design and predictions, copied below verbatim), an internal file (build; its "
        "section 0 differences, copied below, govern where they differ). Code: `r10/runs.py` (runs, reads, accounts), "
        "`r10/models.py` (settings), `r10/tools.py`, `r10/forms10.py`, `r10/textedit.py`, `r10/groups.py`, "
        "`r10/briefsearch.py`, `r10/analysis/stats.py`. Request counts and hashes: `r10/manifest.json`. "
        "No round-10 call reads a Track P pool, gate-set, validation or test dialogue (`groups.assert_unprotected`).",
        "",
        "### Differences of the action plan (section 0)",
        "",
        diffs,
        "",
        "Two decisions of Opus at the build (2026-11-12):",
        "- B-verify gates only a `type` value that keeps `hotel` and not `guesthouse`; a list that holds both types does "
        "not change (`forms10.b_verify`).",
        "- B-list keeps the F0 value space for `accepted_types` (null, \"any\", or a list); a list that holds both types "
        "gives `type` null for scoring, and the raw list is kept.",
        "",
        "### The trade rule",
        "",
        rule,
        "",
    ]
    for head, nxt in (("### A. Agent loop", ["### B. "]), ("### B. Structural fixes", ["### I. "]),
                      ("### I. The reverse text edit", ["### H. "]), ("### E. Opus as a panel model", ["### F. "]),
                      ("### F. Does more reasoning fix it?", ["### G. "]),
                      ("### G. `gpt-6-astra` as a panel model", ["### The fill rule"])):
        parts += [block(plan, head, nxt).replace("### ", "#### ", 1), ""]
    parts += [
        "### Fixed texts",
        "",
        "Experiment A, tool arms (`tools.tool_system`): in the F0 or F1 form text,",
        f"- \"{tools.ASK_OLD}\" becomes \"{tools.ASK_NEW}\"",
        f"- \"{tools.END_OLD}\" becomes \"{tools.END_NEW}\" (t0, t1) or \"{tools.END_NEW_ASK}\" (t0ask).",
        f"- Tool descriptions: search_hotels \"{tools.SEARCH_DESCRIPTION}\"; ask_traveller \"{tools.ASK_DESCRIPTION}\".",
        "- The search tool schema is the closed form schema (`zforms.FORMS[\"f0\"].schema`, `[\"f1\"]` for t1), strict; "
        "tool_choice auto with one call at most. P0 is the round-9 Z2 request (`zforms.FORMS[\"f0\"]`, prefix text).",
        "- Step 2: the stored assistant output unchanged, then the tool result "
        "`json.dumps(briefsearch.result_rows(briefsearch.search(db, fields)))` (at most 5 rows: name, type, area, "
        "pricerange, stars; and the total). No other text.",
        "",
        "Experiment B (`forms10.FORMS`), each inserted after \"internet: yes, no.\" unless stated:",
        f"- b_list: the key `type` becomes `accepted_types` in the field list and the values, then \"{forms10.LIST_RULE}\"",
        f"- b_evidence: \"{forms10.EVIDENCE_RULE}\"",
        f"- verify (its own system text): \"{forms10.VERIFY_SYSTEM}\" with the schema {{\"answer\": yes | no | unclear}}.",
        "- b_shot: the two examples below, after \"internet: yes, no.\", separated by blank lines.",
        "",
        "```",
        forms10.EXAMPLE_1,
        "",
        forms10.EXAMPLE_2,
        "```",
        "",
        "- b_define: `zforms.FORMS[\"p_define\"]` (round 9), Sol and Luna, S2 and S3 only.",
        "",
        "Experiment I (`textedit.insert_turn`), traveller turns only:",
        "",
        "```",
        (textedit.__doc__ or "").strip(),
        "```",
        "",
        "Groups: 233 dialogues (115 where an assistant turn says \"hotel\", 118 where no turn says it); the analysis "
        "reports the two parts apart (difference 3).",
        "",
    ]
    parts += settings_part() + verbatim_part()
    return "\n".join(parts)


def settings_part():
    rows = ["### Model settings (`r10/models.py`)", "", "| Key | Model | max_tokens | effort | thinking |",
            "|---|---|---:|---|---|"]
    for k in ("sonnet", "haiku", "opus", "sol", "luna", "astra", "sonnet_high", "haiku_high", "opus_high", "sol_high",
              "luna_high"):
        m = models.MODELS[k]
        rows.append(f"| {k} | `{m.id}` | {m.max_tokens} | {m.effort} | {json.dumps(m.thinking) if m.thinking else 'no field'} |")
    rows += ["",
             "- Opus has no `thinking` field: the API runs adaptive thinking at the given effort (claude-api skill, "
             "cached 2026-11-03: its thinking cannot be turned off).",
             "- Sonnet with `between_tools` can think after a tool result. So step 2 of A can hold thinking for Sonnet, "
             "and stage 1 cannot. The step-2 pilot measures the output size.",
             "- For Haiku, experiment F changes two settings (thinking and effort). For Sonnet, it changes thinking only.",
             "- The larger max_tokens of the high settings raises the hard bound of their pilots; the batch bound uses "
             "the pilot mean.",
             "- The tool name `search_hotels`, \"Search for hotels\" and \"hotel database\" are the same in T0 and T1, as "
             "the frame words of F0 and F1 are the same. T1 against T0 is a clean rename of the field and its value; T1 "
             "against the F1 form is not a pure rename.",
             ""]
    return rows


def fence(label, text):
    return [label, "", "```", text, "```", ""]


def verbatim_part():
    """Every distinct system text, the schemas that are not the round-9 form schemas, the user-text format, and the
    code of the experiment-I rule, verbatim."""
    out = ["### Verbatim texts and schemas", "",
           "User text: `common.dialogue_text` writes one line per turn, \"Traveller: \" or \"Assistant: \" and the "
           "turn text stripped, joined by line breaks. A uses `zforms.prefix_text` (all turns up to and including the "
           "first traveller turn that says \"hotel\"). The form schemas are `zforms.FORMS[...].schema` (round 9).", ""]
    texts = {"F0 form (p0, f0; B arm f0)": zforms.FORMS["f0"].system, "F1 form (f1)": zforms.FORMS["f1"].system,
             "Tool arm t0": tools.tool_system("t0"),
             "Tool arm t1": tools.tool_system("t1"), "Tool arm t0ask": tools.tool_system("t0ask")}
    for arm in ("b_list", "b_shot", "b_evidence", "verify", "b_define"):
        texts[f"B arm {arm}"] = forms10.FORMS[arm].system
    for label, text in texts.items():
        out += fence(f"{label}:", text)
    out += fence("ask_traveller input schema:", json.dumps(tools.ASK["input_schema"], indent=1))
    out += fence("b_evidence schema:", json.dumps(forms10.FORMS["b_evidence"].schema, indent=1))
    out += fence("b_list schema:", json.dumps(forms10.FORMS["b_list"].schema, indent=1))
    out += fence("verify schema:", json.dumps(forms10.FORMS["verify"].schema, indent=1))
    out += fence("Experiment I rule, the code of `r10/textedit.py`:", inspect.getsource(textedit).strip())
    out += ["Edited-text check (builder I read all 243 edited traveller turns of the 233 dialogues): after the rule fix, "
            "0 turns are not grammatical because of the rule; 9 turns keep an error that is already in the original "
            "traveller text. The request audit noted turns that are grammatical but awkward (PMUL0242, PMUL0346: \"the "
            "restaurant and a hotel\") and one turn that now asks for a hotel and then for a guesthouse (PMUL4943). No "
            "single dialogue is corrected by hand.", ""]
    return out


def write():
    text = runs.PROTOCOL.read_text()
    if runs.SECTION in text:
        sys.exit(f"Not written: {runs.PROTOCOL.name} already has {runs.SECTION!r}.")
    if runs.LOCK.exists():
        sys.exit(f"Not written: {runs.LOCK.name} exists.")
    new = text.rstrip("\n") + "\n\n" + section() + "\n" + runs.AMEND + "\n\nNone yet.\n"
    runs.PROTOCOL.write_text(new)
    h = runs.section_hash(new)
    runs.LOCK.write_text(json.dumps({"sha256": h, "section": runs.SECTION,
                                     "time": datetime.datetime.now(datetime.timezone.utc).isoformat()}, indent=1))
    print(f"section written and locked: {h}")


if __name__ == "__main__":
    {"print": lambda: print(section()), "write": write}[sys.argv[1] if len(sys.argv) > 1 else "print"]()
