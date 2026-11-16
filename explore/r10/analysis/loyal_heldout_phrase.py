"""Final 9 (the paper): the phrase rule and the strict rule on the first requests of the 213 held-out no-type dialogues.

This is a corpus-only check (post hoc). It reads the MultiWOZ 2.4 dialogue text, the stage-1 id lists and the rules.
It opens no em* folder, no answer file, no *.sealed file and no key file. An audit hook (sys.addaudithook) stops the
script if any open or directory listing inside the project names such a path, and the output lists every project file
that the script opened. It reads no agent answer, so it gives no statement about the counted exclusion cases.

This file is a copy of the project script (an internal file) with the paths
of the study folder. The lists of opened files in its output depend on the folders.
Usage (from explore/):
  python3 -I r10/analysis/loyal_heldout_phrase.py
      writes r10/analysis/out/loyal_heldout_phrase.json and loyal_heldout_phrase.md
  python3 -I r10/analysis/loyal_heldout_phrase.py check <paper.md>
      checks the final-9 values of the paper (this result, Table D2, Table E6, Appendix F.4, result.md) and that no
      value from the em1 answers is left in the paper

Data and rules (read only):
- The 213 dialogues: prototypes/explore/main/wave1_ids.json through stage1_units of main/exp0/analysis.py (the
  "natural" stage-1 units), and the no-type subset of briefsearch.brief_subsets (the brief sets no type).
- The first request: zforms.prefix_end. The rules: clear_rule.label (the phrase rule) and clear_rule.label_strict (the
  strict rule) of prototypes/explore/r10/analysis/clear_rule.py, the rules of Appendices E.4 and G. A type sentence is
  any label other than "unclear" (hotel_only, guesthouse_only or mixed).
"""
import collections
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
ROOT = HERE.parents[2]  # the folder that holds explore/
OUT = HERE / "out"
OPENED, OPENED_OUTSIDE = set(), set()
PYTHON = tuple(str(pathlib.Path(p).resolve()) for p in {sys.prefix, sys.base_prefix, sys.exec_prefix})


def _refused(path, listing):
    """True for a path that the operator rules close to agents. It uses only the path text (no stat of the path):
    inside the project, a folder whose name starts with "em" (for a listing, the listed folder too)."""
    parts = path.parts
    rel = parts[len(ROOT.parts):] if parts[:len(ROOT.parts)] == ROOT.parts else None
    if rel is not None:
        dirs = rel if listing else rel[:-1]
        if any(p.startswith("em") for p in dirs):
            return True
    name = path.name
    return (name.endswith(".sealed") or name.endswith(".env") or name == "raw.jsonl" or "seal_key" in name
            or "seal-key" in parts or "private folder" in parts)


def _audit(event, args):
    if event not in ("open", "os.listdir", "os.scandir") or not args or not isinstance(args[0], (str, bytes, pathlib.Path)):
        return
    raw = args[0].decode() if isinstance(args[0], bytes) else str(args[0])
    path = pathlib.Path(raw)
    if not path.is_absolute():
        path = pathlib.Path.cwd() / path
    path = pathlib.Path(*path.parts)
    if _refused(path, event != "open"):
        raise PermissionError(f"refused by the operator rule: {path}")
    if event != "open" or path.suffix == ".pyc":
        return
    if path.parts[:len(ROOT.parts)] == ROOT.parts:
        OPENED.add(str(path.relative_to(ROOT)))
    elif not str(path).startswith(PYTHON) and path.suffix not in (".py", ".so"):
        OPENED_OUTSIDE.add(str(path))


sys.addaudithook(_audit)  # before any project import, so that module-level reads are checked too

EXPLORE = ROOT / "explore"
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("stage1_analysis", EXPLORE / "main" / "exp0" / "analysis.py")
an = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(an)  # it puts main, lib, forms, r9 and r10 on the path; it reads no answer at import
import clear_rule  # noqa: E402
import zforms  # noqa: E402

bs, wave1 = an.bs, an.wave1


def main():
    # self-test of the refusal rule, on path text only (nothing is opened)
    assert _refused(ROOT / "explore/main/exp0/open/em1_x/raw.jsonl", False)
    assert _refused(ROOT / "explore/main/exp0/open/em1_x", True)
    assert _refused(ROOT / "a/b.sealed", False) and not _refused(ROOT / "explore/main/wave1_ids.json", False)
    data, lists, db = wave1.anth.multiwoz(), wave1.ids(), bs.gold.hotel_db()
    units, _ = an.stage1_units(lists)
    subsets = bs.brief_subsets(data, [d + ".json" for d in units["natural"]], db)
    no_type = [d.removesuffix(".json") for d in subsets["no_type"]]
    assert len(no_type) == 213, len(no_type)
    phrase, strict = collections.Counter(), collections.Counter()
    for d in no_type:
        dlg = data[d + ".json"]
        pe = zforms.prefix_end(dlg)
        phrase[clear_rule.label(dlg, pe)] += 1
        strict[clear_rule.label_strict(dlg, pe)] += 1
    res = {
        "post_hoc": True,
        "corpus_only": True,
        "dialogues": "the 213 held-out (stage-1) natural dialogues whose brief sets no type; first request only",
        "first_request_labels_phrase_rule": dict(phrase),
        "first_request_labels_strict_rule": dict(strict),
        "type_sentences_phrase_rule": sum(n for k, n in phrase.items() if k != "unclear"),
        "type_sentences_strict_rule": sum(n for k, n in strict.items() if k != "unclear"),
        "answers_read": 0,
        "project_files_opened": sorted(OPENED),
        "other_data_files_opened": sorted(OPENED_OUTSIDE),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "loyal_heldout_phrase.json").write_text(json.dumps(res, indent=1) + "\n")
    lines = ["## the paper, final 9: the phrase rule on the 213 held-out no-type first requests (post hoc; corpus "
             "only)", "",
             f"- Phrase rule: {dict(phrase)}.", f"- Strict rule: {dict(strict)}.",
             "- Agent answers read: 0. No em* folder, answer file, sealed file or key file was opened (audit hook).",
             "- Project files opened (compiled modules not listed):"] + [f"  - {p}" for p in res["project_files_opened"]]
    lines += ["- Data files opened outside the project:"] + [f"  - {p}" for p in res["other_data_files_opened"]]
    (OUT / "loyal_heldout_phrase.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def check(md_path):
    """Check the final-9 values of the paper. Reads only the paper, out/loyal_heldout_phrase.json and
    workshops/steer-search/out/result.md."""
    res = json.loads((OUT / "loyal_heldout_phrase.json").read_text())
    flat = re.sub(r"\s+", " ", open(md_path, encoding="utf-8").read())
    fails = 0

    def ok(name, cond):
        nonlocal fails
        print(("ok   " if cond else "FAIL ") + name)
        fails += 0 if cond else 1

    def has(*ps):
        return all(p in flat for p in ps)

    ok("phrase rule and strict rule: no type sentence in the 213 held-out no-type first requests",
       res["first_request_labels_phrase_rule"] == {"unclear": 213}
       and res["first_request_labels_strict_rule"] == {"unclear": 213} and res["answers_read"] == 0
       and not any(part.startswith("em") for f in res["project_files_opened"] for part in f.split("/")[:-1])
       and has("The phrase rule and its stricter version, the strict rule (Appendix E.4), also found no such "
               "sentence in the first requests of the 213 held-out no-type dialogues (post hoc)", "We did not examine the exclusion cases "
               "that Table 1 counts, either by reading or with a rule", "Our phrase rule finds no sentence that "
               "states the type in the first requests of the 213 held-out no-type dialogues. We did not examine the "
               "exclusion cases themselves."))
    gone = ["Table B7", "The words of the held-out exclusion cases", "168 of the 170", "12.0% (Haiku) to 40.0% (Sol)",
            "the 43 where at least one model", "43 dialogues where at least one model", "held-out exclusion cases and "
            "gives the exclusion share", "of these exclusion cases", "No person read these exclusion cases blind"]
    ok("no value or sentence from the em1 answers is left", not any(g in flat for g in gone))
    ok("Table D2: Luna non-empty 15 removes and 66 new hotel-only searches of 179; five agents 0",
       has("| Luna | not empty | 179 | 96 | 15 | 0 | 66 | 49 | 49 |", "15 of 179 trials and repeated the hotel-only "
           "search in 66") and all(f"| {m} | not empty |" in flat for m in ("Sonnet", "Haiku", "Opus", "Sol", "Astra")))
    ok("Table E6: 9 against 7 of 130 (renamed against original, only guesthouses fit); pointer Appendix E",
       has("| Renamed | Only guesthouses fit | 130 | 1 (0.8%) | 121 (93.1%) | 9 (6.9%) |",
           "| Original | Only guesthouses fit | 130 | 20 (15.4%) | 123 (94.6%) | 7 (5.4%) |",
           "9 of the 130 guesthouse-only conversations never showed a fitting venue, against 7 with the original "
           "tool (Appendix E)"))
    ok("Appendix F.4: 29 pairs held 25, passed 2, flagged 2; revised rule no flag; N1 hold, eight flags",
       has("It held the tool in 25 pairs, passed it in 2 and flagged it in 2", "With this condition, none of the 29 "
           "pairs gives a flag", "turns Haiku's N1 from a flag into a hold, and the other eight rewrites keep their "
           "flags", "the first rule held 25, passed 2 and flagged 2", "flags eight and holds the clarity rewrite N1"))
    v = (ROOT / "workshops/steer-search/out/result.md").read_text()
    again = [tuple(map(int, x)) for x in re.findall(r"  - (?:h1|g1): [^\n]*?searched again (\d+)/(\d+)", v)]
    pct = [100 * a / b for a, b in again]
    ok(f"6% to 17%: searched again with H1 or G1, {min(pct):.1f}% to {max(pct):.1f}%",
       (round(min(pct)), round(max(pct))) == (6, 17) and has("only 6% to 17% of conversations did"))
    print(f"{fails} failures")
    return fails


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        sys.exit(1 if check(sys.argv[2]) else 0)
    sys.exit(main())
