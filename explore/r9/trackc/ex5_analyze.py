"""Score X5 with the E3 reader (annot/analyze.py) and check the X5 prediction of PREDICTIONS.md. Offline.

Measures, all on the field class (clear, ambiguous, outside_form) that annot/analyze.py parses:
- disagreement between `claude-opus-5-5` and `gpt-6-astra` on read 1: the target field and all fields of the
  ambiguous E4 items, of the clear E4 items, and all fields of the E7 dialogues
- agreement of each annotator with the construction on the E4 target field: ambiguous when the item has two or more
  readings, else clear (a condition d item has the one reading null, so it counts as clear)
- read 1 against read 2 of each annotator on the 20 repeated units
A field counts only when both codes of a comparison parse. Writes summary.json into ex5_an and ex5_oa.
Usage: python3 -I r9/trackc/ex5_analyze.py
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import panel  # noqa: E402
import tasks  # noqa: E402
import x5  # noqa: E402

ANNOT = tasks.load(panel.EXPLORE / "annot" / "analyze.py", "annot_analyze")
RUNS = {"anthropic": "ex5_an", "openai": "ex5_oa"}
ITEMS = {i.id: i for i in tasks.templates.items()}


def codes(got, reader, cells):
    """{(unit key, read): code}; a code is a dict of parsed fields or the kind of missing cell."""
    return {(key, read): reader.code(got[cid]) if cid in got else "absent" for cid, key, read, _ in cells}


def field_class(code, field):
    f = code["fields"][field] if isinstance(code, dict) else None
    return f.cls if isinstance(f, ANNOT.Field) else None


def rate(pairs):
    """Disagreement over the pairs in which both classes exist."""
    both = [(a, b) for a, b in pairs if a is not None and b is not None]
    return {"fields": len(both), "disagree": sum(a != b for a, b in both),
            "rate": sum(a != b for a, b in both) / len(both) if both else None}


def expected_class(item):
    return "ambiguous" if len(item.interpretations) > 1 else "clear"


def group(key):
    item = ITEMS.get(key)
    return "dialogue" if item is None else expected_class(item)


def summarize(by_annotator, keys):
    """`by_annotator`: {"opus": codes, "astra": codes}; `keys`: the unit keys of read 1."""
    opus, astra = by_annotator["opus"], by_annotator["astra"]
    out = {"disagreement": {}, "construction": {}, "repeat_change": {}}
    for g in ("ambiguous", "clear", "dialogue"):
        units = [k for k in keys if group(k) == g]
        out["disagreement"][f"{g}_all_fields"] = rate([(field_class(opus[(k, 1)], f), field_class(astra[(k, 1)], f))
                                                       for k in units for f in tasks.e3.FIELDS])
        if g != "dialogue":
            out["disagreement"][f"{g}_target"] = rate([(field_class(opus[(k, 1)], ITEMS[k].target),
                                                        field_class(astra[(k, 1)], ITEMS[k].target)) for k in units])
    for name, c in by_annotator.items():
        items = [k for k in keys if group(k) != "dialogue"]
        out["construction"][name] = rate([(field_class(c[(k, 1)], ITEMS[k].target), expected_class(ITEMS[k]))
                                          for k in items])
        repeats = sorted(k for k, read in c if read == 2)
        out["repeat_change"][name] = rate([(field_class(c[(k, 1)], f), field_class(c[(k, 2)], f))
                                           for k in repeats for f in tasks.e3.FIELDS])
    amb, clr = out["disagreement"]["ambiguous_target"]["rate"], out["disagreement"]["clear_target"]["rate"]
    out["prediction_more_disagreement_on_ambiguous"] = None if amb is None or clr is None else amb > clr
    out["missing"] = {name: sum(not isinstance(v, dict) for v in c.values()) for name, c in by_annotator.items()}
    return out


def main():
    reader = ANNOT.Reader(tasks.e3.load_p5().p4)
    first, _, _ = x5.units()
    by_annotator, got_any = {}, False
    for provider, name in RUNS.items():
        got = panel.rows(name)
        got_any |= bool(got)
        by_annotator[x5.SHORT[provider]] = codes(got, reader, x5.cells(provider))
    summary = summarize(by_annotator, [p.key for p in first])
    for name in RUNS.values():
        if got_any:
            (panel.EXPLORE / name / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
