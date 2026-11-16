"""Answer-level tables of the round-9 and round-10 runs: one row per answer (or per conversation), scored with the
parsers of the analysis scripts. Written for the supplementary packages and this repository; it makes no model call.

Inputs: <run>/raw.jsonl and <run>/conversations.jsonl of every run folder, and the public corpus (corpus/MULTIWOZ2.4)
for the columns that need the brief or the venue data. Outputs, in ../tables/ (gzip CSV):
- answers_hotel.csv.gz       form answers and tool calls on the hotel field (round 9 and round 10)
- answers_next_step.csv.gz   the second step and the returned flag (round 10, experiments A2 and W)
- answers_word_pairs.csv.gz  the 12 constructed word pairs (round 10, experiment H)
- conversations_turns.csv.gz the later turns with a simulated traveller (round 10, experiment T), one row per conversation
Validity columns of answers_hotel.csv.gz:
- valid: the answer is scorable. It finished, and the parser of its analysis script read it after the declared
  normalization (tools.clean_nulls, amendment R10-3). The parser does not check the allowed values of the schema.
- schema_valid: the answer is scorable, and the arguments of its tool call after the same normalization fit the full
  input schema of the called tool in the answer's own condition. The checker is tool_validity.problems
  (r10/analysis/tool_validity.py). An answer without a tool call has no arguments, so it gets the value of valid. A form
  or verifier answer also gets the value of valid: this script does not check form answers against their schema.
- schema_problems: the problems that the checker found in the tool call (also for a call that is not scorable).
Usage (from explore/): .venv/bin/python -I answer_tables.py
"""
import csv
import gzip
import io
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free", "r10", "r10/analysis"):
    sys.path.insert(0, str(EXPLORE / sub))
import a_analyze  # noqa: E402
import b_analyze  # noqa: E402
import briefsearch as bs  # noqa: E402
import common  # noqa: E402
import efg_analyze  # noqa: E402
import flag  # noqa: E402
import forms10  # noqa: E402
import gold  # noqa: E402
import h_analyze  # noqa: E402
import natural  # noqa: E402
import natural_analyze as na  # noqa: E402
import release  # noqa: E402
import release_analyze  # noqa: E402
import runs  # noqa: E402
import tool_validity  # noqa: E402  (the full-schema checker; its main() does not run)
import tools  # noqa: E402
import turns_analyze  # noqa: E402
import zanalyze  # noqa: E402
import zforms  # noqa: E402
import zruns  # noqa: E402

OUT = EXPLORE.parent / "tables"
CUT = {"max_tokens", "length", "incomplete", "max_output_tokens"}
HOTEL_COLS = ["series", "run", "experiment", "model", "dialogue", "cell", "read", "status", "stop", "valid",
              "invalid_reason", "schema_valid", "schema_problems", "kind", "type", "hotel", "hotel_only",
              "verifier_answer", "brief_type", "search_failure", "fields"]
TOOL_CELLS = {"A": ("t0", "t1", "t0ask"), "R": ("t0", "tedit")}  # the cells of this table whose answers are tool calls
_SCHEMAS = {}


def call_schemas(exp, cell):
    """{tool name: input schema} of the tools that the condition (experiment, cell) offered."""
    if (exp, cell) not in _SCHEMAS:
        t0, ask = tools.SEARCH_T0["input_schema"], tools.ASK["input_schema"]
        if cell == "tedit":  # the frozen edit of amendment R10-6
            t = release.edit()["obj"]["tool"]
            offered = {t["name"]: t["input_schema"]}
        else:
            offered = {"search_hotels": tools.SEARCH_T1["input_schema"] if cell == "t1" else t0}
            if cell == "t0ask":
                offered["ask_traveller"] = ask
        _SCHEMAS[(exp, cell)] = offered
    return _SCHEMAS[(exp, cell)]


def schema_check(row, exp, cell):
    """The problems of the one tool call of a row after tools.clean_nulls, against the input schema of the called tool
    in this condition: a list of texts (empty: the call fits), or None when there is no single call to check."""
    calls = row.get("tool_calls") or []
    if status_of(row) or len(calls) != 1 or not isinstance(calls[0].get("input"), dict):
        return None
    schema = call_schemas(exp, cell).get(calls[0].get("name"))
    if schema is None:
        return None
    return tool_validity.problems(tools.clean_nulls(calls[0]["input"]), schema)


def jsonable(v):
    if isinstance(v, tuple):
        return [jsonable(x) for x in v]
    if isinstance(v, dict):
        return {k: jsonable(x) for k, x in v.items()}
    if isinstance(v, list):
        return [jsonable(x) for x in v]
    return v


def rows_of(run, name="raw.jsonl"):
    path = EXPLORE / run / name
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()] if path.exists() else []


def run_folders():
    return sorted(p.name for p in EXPLORE.iterdir() if p.is_dir() and (p / "raw.jsonl").exists()
                  or p.is_dir() and (p / "conversations.jsonl").exists())


def status_of(row):
    if row.get("type") != "succeeded":
        return "failed"
    if row.get("stop") in CUT:
        return "cut"
    return None


class Hotel:
    """One CSV row per answer on the hotel field."""

    def __init__(self, data, db):
        self.data, self.db, self.turns = data, db, {}

    def row(self, rnd, run, exp, model, d, cell, read, r, valid, reason, kind, fields, verifier=None):
        t = fields.get("type") if isinstance(fields, dict) else None
        dd = self.data.get(d)
        scored = valid and kind in ("form", "search")
        none = valid and kind in ("ask", "none")  # a valid answer without a search scores 0
        # The venue type that the written task sets: its first request (info), else the request that had no venue
        # (fail_info). "none" when both set no type, as briefsearch.brief_subsets defines the no-type briefs.
        brief = (gold.brief_type(dd) or gold.brief_type(dd, "fail_info")) if dd else None
        sf = ""
        if dd is not None and scored and isinstance(fields, dict):
            sf = int(bool(bs.search_failure(fields, dd, self.db)))
        elif dd is not None and none:  # a valid answer without a search is not a search failure
            sf = 0
        problems = schema_check(r, exp, cell) if cell in TOOL_CELLS.get(exp, ()) else None
        return {"series": rnd, "run": run, "experiment": exp, "model": model, "dialogue": d.removesuffix(".json"),
                "cell": cell, "read": read, "status": r.get("type"), "stop": r.get("stop"), "valid": int(valid),
                "invalid_reason": "" if valid else reason, "schema_valid": int(bool(valid) and not problems),
                "schema_problems": "; ".join(problems or []), "kind": kind if valid else "",
                "type": json.dumps(jsonable(t)) if scored else "",
                "hotel": int(na.hotel(t)) if scored else (0 if none else ""),
                "hotel_only": int(na.hides(t)) if scored else (0 if none else ""),
                "verifier_answer": verifier or "", "brief_type": "" if dd is None else (brief or "none"),
                "search_failure": sf,
                "fields": json.dumps(jsonable(fields)) if valid and isinstance(fields, dict) else ""}

    def r10(self, run, exp, model):
        for r in rows_of(run):
            _, did, cell, read = r["custom_id"].split("-")
            d, read = did + ".json", int(read)
            bad = status_of(r)
            verifier = None
            if exp == "A":
                kind, val = a_analyze.read_of(r, cell)
                valid, fields, reason = kind != "invalid", val, val
            elif exp in ("B", "Y"):  # Y: the verifier runs of R10-17 (cells f0 and verify, as in B)
                if cell == "b_evidence" and d not in self.turns:
                    self.turns[d] = forms10.traveller_turns(self.data[d])
                parsed = b_analyze.parse_row(r, cell, self.turns.get(d))
                valid, reason = parsed is not None, bad or "parse"
                if cell == "verify":
                    kind, fields, verifier = "verify", None, (parsed or {}).get("answer")
                else:
                    kind, fields = "form", parsed
            elif exp in ("E", "F", "G"):
                valid, val = efg_analyze.read_of(r, cell)
                kind, fields, reason = "form", val, val
            elif exp == "I":
                kind, reason = "form", bad
                try:
                    fields = None if bad else natural.parse(r.get("text", ""), natural.FORMS[cell.rsplit("_", 1)[1]])
                except (ValueError, KeyError, TypeError):
                    fields, reason = None, "parse"
                valid = fields is not None
            elif exp == "R":
                kind, val = release_analyze.read_of(r, cell)
                valid, fields, reason = kind != "invalid", val, val
            else:
                return
            yield self.row(10, run, exp, model, d, cell, read, r, valid, reason, kind,
                           fields if valid else None, verifier)

    def r9_natural(self, run):
        for r in rows_of(run):
            exp, model, form, unit, read = na.key(r["custom_id"])
            f = na.label(exp, form, unit)
            if f is None:
                continue
            reason = None if r["type"] == "succeeded" and r.get("stop") == "end_turn" else (
                "failed" if r["type"] != "succeeded" else "cut")
            fields = None
            if reason is None:
                try:
                    fields = natural.parse(r["text"], natural.FORMS[f.removesuffix("_drift")])
                except (ValueError, KeyError, TypeError):
                    reason = "parse"
            d = unit + ".json"
            yield self.row(9 if run not in ("e13", "e14") else 8, run, "natural", model, d, f, read, r,
                           fields is not None, reason, "form", fields)

    def r9_additions(self, run):
        for r in rows_of(run):
            try:
                _, d, form, read, model = common.split_custom_id(r["custom_id"])
            except ValueError:
                continue
            cell = zanalyze.ALIASES.get(form, form)
            if cell not in zruns.CELLS:
                continue
            reason, fields = None, None
            if r["type"] != "succeeded":
                reason = "failed"
            elif r.get("stop") != "end_turn":
                reason = "cut"
            else:
                try:
                    fields = zforms.parse(zruns.CELLS[cell].form, r["text"])
                except (ValueError, KeyError, TypeError, AttributeError):
                    reason = "parse"
            yield self.row(9, run, "additions", model, d, cell, read, r, fields is not None, reason, "form",
                           fields if isinstance(fields, dict) else None)


def next_step(run, exp, model):
    for r in rows_of(run):
        _, did, cell, read = r["custom_id"].split("-")
        kind, detail = flag.classify(r)
        yield {"run": run, "experiment": exp, "model": model, "dialogue": did, "cell": cell, "read": int(read),
               "status": r.get("type"), "stop": r.get("stop"), "kind": kind,
               "detail": json.dumps(jsonable(detail)) if detail is not None else ""}


def word_pairs(run, model, index):
    for r in rows_of(run):
        _, unit, form, read = r["custom_id"].split("-")
        info = index.get(f"{unit}-{form}")
        if info is None:
            continue
        ok, val = h_analyze.score(r, info)
        yield {"run": run, "model": model, "pair": info["pair"], "kind": info["kind"], "scenario": info["scenario"],
               "form": info["form"], "unit": info["unit"], "read": int(read), "status": r.get("type"),
               "stop": r.get("stop"), "valid": int(ok), "invalid_reason": "" if ok else val,
               "writes_colliding_value": int(val[0]) if ok else "", "only_colliding_value": int(val[1]) if ok else "",
               "values_outside_schema": val[2] if ok else "", "type": json.dumps(type_values(r)) if ok else ""}


def type_values(row):
    """The `type` list of a valid word-pair answer, as h_analyze.score reads it."""
    text = row.get("text", "") or ""
    t = json.loads(text[text.rfind("{"):text.rfind("}") + 1])["type"]
    return t if isinstance(t, list) else []


def conversations(run, data, db):
    by_name = {gold.norm(v["name"]): v for v in db}
    guest = sorted({gold.norm(v["name"]) for v in db if v["type"] == "guesthouse"}, key=len, reverse=True)
    names = sorted({gold.norm(v["name"]) for v in db}, key=len, reverse=True)
    for rec in rows_of(run, "conversations.jsonl"):
        base = {"run": run, "dialogue": rec["dialogue"].removesuffix(".json"), "arm": rec.get("arm"),
                "group": rec.get("group"), "status": rec.get("status")}
        if rec.get("status") != "complete":
            yield base
            continue
        o = turns_analyze.outcomes(rec, data, db, by_name, guest, names)
        o.pop("dialogue", None)
        o.pop("group", None)
        yield {**base, **{k: (int(v) if isinstance(v, bool) else v) for k, v in o.items()}}


def write(name, rows):
    rows = list(rows)
    if not rows:  # this repository holds no run of the table
        return
    cols = list(dict.fromkeys(k for r in rows for k in r))
    OUT.mkdir(exist_ok=True)
    # mtime=0: the gzip header holds no time, so the same rows give the same file
    with io.TextIOWrapper(gzip.GzipFile(OUT / name, "wb", mtime=0), encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"{name}: {len(rows)} rows")


def main():
    data, _ = runs.context()
    db = gold.hotel_db()
    hotel, step, pairs_rows, conv = Hotel(data, db), [], [], []
    index = h_analyze.spec_index()
    hot = []
    natural_runs = set(natural.EXPERIMENTS) | {"e13", "e14"}
    for run in run_folders():
        if run in runs.RUNS:
            spec = runs.RUNS[run]
            model = spec.model
            if spec.exp in ("A", "B", "E", "F", "G", "I", "R", "Y"):
                hot += list(hotel.r10(run, spec.exp, model))
            elif spec.exp in ("A2", "W"):
                step += list(next_step(run, spec.exp, model))
            elif spec.exp == "H":
                pairs_rows += list(word_pairs(run, model, index))
            elif spec.exp == "T":
                conv += list(conversations(run, data, db))
            else:
                print(f"{run}: experiment {spec.exp} has no scored table; its answers are in {run}/raw.jsonl")
        elif run in natural_runs:
            hot += list(hotel.r9_natural(run))
        elif run in zruns.RUNS:
            hot += list(hotel.r9_additions(run))
        else:
            print(f"{run}: no table here; its answers are in {run}/raw.jsonl (see README.md)")
    write("answers_hotel.csv.gz", hot)
    write("answers_next_step.csv.gz", step)
    write("answers_word_pairs.csv.gz", pairs_rows)
    write("conversations_turns.csv.gz", conv)


if __name__ == "__main__":
    main()
