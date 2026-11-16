"""Full-schema validity of the stored tool calls. Post hoc; no model call; it reads stored answers only.

For each stored answer of the tool-call arms, this script checks the arguments of the search call against the input
schema of the answer's own condition:
- first-request runs (era1_<model> and the fill runs of a_analyze.FILL): arm t0 (original tool, tools.SEARCH_T0) and
  arm t1 (renamed tool, tools.SEARCH_T1), six models; for comparison also the form arm p0 (the last JSON object of the
  answer text against the same schema, under structured output; no normalization);
- forward release test (erp_<model>, amendment R10-6): arm t0 and arm tedit (the frozen edit of release.edit());
- steering run (ers_<model>, amendment R10-14): cells th and tg (the frozen edits of steer.edit()), and for Haiku t0;
- control updates (amendment R10-16, Haiku): erc_haiku cells t0 (the control) and tord (control.ordered_tool(): the
  original schema with its fields in alphabetical order), and erc2_haiku cell trep (the original tool again). All
  reads of each cell (10 per prefix on the specific set, 1 on the open and guesthouse sets).
The check covers every keyword that these schemas use: type, enum (the allowed strings), const, anyOf, items, minItems,
properties, required (every key present) and additionalProperties false. Any other keyword stops the script, so no
rule is skipped without notice.

Answer classes (one stored answer each):
- not completed: the row did not succeed, or it stopped at the output limit;
- non-call: no tool call (the scored analyses count it as an answer without a hotel value);
- other call: more than one call, a call of another tool, or input that is not an object;
- search call: one search_hotels call with an object input. "raw valid": the arguments as stored fit the schema.
  "valid after normalization": the arguments after tools.clean_nulls (amendment R10-3: the text "null" is read as
  null, an item "null" of a list is dropped, and a list that is then empty is read as null) fit the schema.

Sensitivity variant: the scored analyses again, with every search call that is not valid after normalization counted
as missing (an invalid answer, as release_analyze.py treats a parse failure). The fixed analyses stay the primary
result; this script changes none of them and none of their outputs.
- forward release test: the decision rule of release_analyze.py (L = 5, 98.75%, 2,000 draws, seed 20261112);
- steering run: the release rule of steer_analyze.py on the hotel value;
- first-request runs: renamed minus original tool, per prefix (a_analyze.paired), on all 554 prefixes (Table 2 of the
  paper) and on the 59 prefixes whose brief sets hotel (Table 4);
- control updates: the rule of control_analyze.py (release_analyze.analyse, unchanged), with all reads and with read 1
  of each arm only. This part was added on 2026-11-12 (round 11) after the control results were known; it is post hoc.
Outputs: r10/analysis/out/tool_validity.md and tool_validity.json.
Usage (from explore/): .venv/bin/python -I r10/analysis/tool_validity.py
"""
import collections
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import a_analyze as aa  # noqa: E402  (its imports set the paths; its main() does not run)
import control_analyze as ca  # noqa: E402
import release_analyze as ra  # noqa: E402
import steer_analyze as sa  # noqa: E402

import briefsearch as bs  # noqa: E402
import control  # noqa: E402
import gold  # noqa: E402
import release  # noqa: E402
import steer  # noqa: E402
import tools  # noqa: E402

OUT = HERE / "out"
CUT = {"max_tokens", "length", "incomplete", "max_output_tokens"}
KNOWN = {"type", "enum", "const", "anyOf", "items", "minItems", "properties", "required", "additionalProperties",
         "description", "title"}
JSON_TYPES = {"null": lambda v: v is None, "string": lambda v: isinstance(v, str),
              "array": lambda v: isinstance(v, list), "object": lambda v: isinstance(v, dict),
              "boolean": lambda v: isinstance(v, bool),
              "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
              "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)}


def problems(value, node, path="$"):
    """The reasons why `value` does not fit the schema `node` (an empty list: it fits)."""
    unknown = set(node) - KNOWN
    if unknown:
        raise SystemExit(f"schema keyword(s) {sorted(unknown)} at {path}: not covered by this validator")
    out = []
    if "anyOf" in node:
        branches = [problems(value, sub, path) for sub in node["anyOf"]]
        if all(branches):
            typed = [b for b, sub in zip(branches, node["anyOf"]) if "type" not in sub or any(
                JSON_TYPES[t](value) for t in (sub["type"] if isinstance(sub["type"], list) else [sub["type"]]))]
            out += typed[0] if typed else [f"{path}: {json.dumps(value)[:40]} is not of an allowed type"]
    if "type" in node:
        ts = node["type"] if isinstance(node["type"], list) else [node["type"]]
        if not any(JSON_TYPES[t](value) for t in ts):
            return out + [f"{path}: not of type {node['type']}"]
    if "enum" in node and value not in node["enum"]:
        out.append(f"{path}: {json.dumps(value)[:40]} not in the allowed values")
    if "const" in node and value != node["const"]:
        out.append(f"{path}: not the constant value")
    if isinstance(value, list):
        if "minItems" in node and len(value) < node["minItems"]:
            out.append(f"{path}: fewer than {node['minItems']} items")
        if "items" in node:
            for i, x in enumerate(value):
                out += problems(x, node["items"], f"{path}[{i}]")
    if isinstance(value, dict):
        props = node.get("properties", {})
        for k in node.get("required", []):
            if k not in value:
                out.append(f"{path}: key {k} missing")
        if node.get("additionalProperties") is False:
            out += [f"{path}: extra key {k}" for k in value if k not in props]
        for k, sub in props.items():
            if k in value:
                out += problems(value[k], sub, f"{path}.{k}")
    return out


def reason_kind(p):
    """A short class of one problem text, for the counts."""
    for key, words in (("missing key", "missing"), ("extra key", "extra key"), ("wrong JSON type", "allowed type"),
                       ("wrong JSON type", "not of type"), ("value outside the allowed values", "not in the allowed"),
                       ("too few items", "fewer than")):
        if words in p:
            return key
    return "other"


def value_kinds(args, schema):
    """Finer kinds of the problems of normalized arguments, per field: "quoted value" (a string inside extra quote
    marks, such as the text "any" with its quotes), "bare value" (one allowed list item given without a list),
    "option word in a list" (the any-option of the field given as a list item), or "other"."""
    kinds = set()
    for k, sub in schema["properties"].items():
        v = args.get(k)
        if k not in args or not problems(v, sub):
            continue
        branches = sub.get("anyOf", [sub])
        word = {x for b in branches if b.get("type") == "string" for x in b.get("enum", [])}
        items = {x for b in branches if b.get("type") == "array" for x in b.get("items", {}).get("enum", [])}
        vals = v if isinstance(v, list) else [v]
        if any(isinstance(x, str) and len(x) > 1 and x[0] == x[-1] and x[0] in "\"'" for x in vals):
            kinds.add("quoted value")
        elif isinstance(v, str) and v in items:
            kinds.add("bare value")
        elif isinstance(v, list) and any(x in word for x in v):
            kinds.add("option word in a list")
        else:
            kinds.add("other")
    return kinds


def classify(row, schema, arm):
    """(class, raw problems, normalized problems). class: not completed, non-call, other call, search. A form answer
    (arm p0) is checked as the last JSON object of its text, with no normalization ("non-call": no JSON object)."""
    if row.get("type") != "succeeded" or row.get("stop") in CUT:
        return "not completed", None, None
    if arm == "p0":
        text = row.get("text") or ""
        try:
            obj = json.loads(text[text.rfind("{"):text.rfind("}") + 1])
        except ValueError:
            return "non-call", None, None
        found = problems(obj, schema)
        return "search", found, found
    calls = row.get("tool_calls") or []
    if not calls:
        return "non-call", None, None
    if len(calls) > 1 or calls[0].get("name") != "search_hotels" or not isinstance(calls[0].get("input"), dict):
        return "other call", None, None
    args = calls[0]["input"]
    return "search", problems(args, schema), problems(tools.clean_nulls(args), schema)


# ---- the runs: (run, model, condition) -> folders, arm in the custom id, schema ----
def conditions():
    out = []
    t0, t1 = tools.SEARCH_T0["input_schema"], tools.SEARCH_T1["input_schema"]
    for m in aa.MODELS:
        folders = [f"era1_{m}", *aa.FILL.get(m, ())]
        out.append(("first request", m, "form (p0)", folders, "p0", t0))
        out.append(("first request", m, "original tool (t0)", folders, "t0", t0))
        out.append(("first request", m, "renamed tool (t1)", folders, "t1", t1))
    for m, folder in ra.MODELS.items():
        if (ra.EXPLORE / folder / "raw.jsonl").exists():
            out.append(("forward release test", m, "original tool (t0)", [folder], "t0", t0))
            out.append(("forward release test", m, "edited tool (tedit)", [folder], "tedit",
                        release.edit()["obj"]["tool"]["input_schema"]))
    for d in steer.directions():
        cell = steer.CELL[d]
        for m in ("sonnet", "haiku"):
            out.append(("steering run", m, f"{'hotel' if d == 'h' else 'guesthouse'} rewrite ({cell})",
                        [f"ers_{m}"], cell, steer.edit(d)["obj"]["tool"]["input_schema"]))
    out.append(("steering run", "haiku", "original tool (t0)", ["ers_haiku"], "t0", t0))
    for cond, folder, cell, schema in (("control (t0)", "erc_haiku", "t0", t0),
                                       ("repeat (trep)", "erc2_haiku", "trep", t0),
                                       ("field-order edit (tord)", "erc_haiku", "tord",
                                        control.ordered_tool()["input_schema"])):
        if (ra.EXPLORE / folder / "raw.jsonl").exists():
            out.append(("control updates", "haiku", cond, [folder], cell, schema))
    return out


def rows_of(folders, arm):
    for folder in folders:
        path = ra.EXPLORE / folder / "raw.jsonl"
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            r = json.loads(line)
            if r["custom_id"].split("-")[2] == arm:
                yield folder, r


def audit():
    """Counts per condition, and the set of (folder, custom_id) whose search call is invalid after normalization."""
    table, bad, examples = [], set(), collections.defaultdict(list)
    for run, model, cond, folders, arm, schema in conditions():
        c, raw_kinds, norm_kinds = collections.Counter(), collections.Counter(), collections.Counter()
        for folder, r in rows_of(folders, arm):
            cls, raw, norm = classify(r, schema, arm)
            c["answers"] += 1
            c[cls] += 1
            if cls != "search":
                continue
            c["raw valid"] += not raw
            c["valid after normalization"] += not norm
            raw_kinds.update({reason_kind(p) for p in raw})
            if norm and arm != "p0":
                args = tools.clean_nulls(r["tool_calls"][0]["input"])
                norm_kinds.update(value_kinds(args, schema))
                type_key = next(k for k in schema["properties"] if k in ("type", "property_kind",
                                                                         "accommodation_type"))
                c["invalid with a problem in the type field"] += bool(problems(args.get(type_key),
                                                                               schema["properties"][type_key]))
                bad.add((folder, r["custom_id"]))
                if len(examples[(run, model, cond)]) < 3:
                    examples[(run, model, cond)].append(norm[:2])
        table.append({"run": run, "model": model, "condition": cond, "folders": folders, "counts": dict(c),
                      "raw_problem_kinds": dict(raw_kinds), "normalized_problem_kinds": dict(norm_kinds),
                      "examples": examples.get((run, model, cond), [])})
    return table, bad


# ---- sensitivity variant ----
def first_request_variant(bad):
    data, g = aa.runs.context()
    db = gold.hotel_db()
    ids = list(g["booked"])
    spec = [i for i in ids if gold.brief_type(data[i]) == "hotel"]
    open_ = [i for i in ids if gold.brief_type(data[i]) is None and gold.brief_type(data[i], "fail_info") is None]
    assert (len(spec), len(open_)) == (59, 448)
    out = {}
    for m in aa.MODELS:
        folders = [f"era1_{m}", *aa.FILL.get(m, ())]
        reads = collections.defaultdict(list)
        for folder in folders:
            rr = aa.rows(folder)
            if rr is None:
                continue
            for r in rr:
                d, arm, read = aa.split(r["custom_id"])
                if arm not in ("t0", "t1"):
                    continue
                kind, val = aa.read_of(r, arm)
                if (folder, r["custom_id"]) in bad:
                    kind, val = "invalid", "full schema"
                reads[(d, arm)].append((read, kind, val if isinstance(val, dict) else None, folder))
        block = {}
        for arm in ("t0", "t1"):
            k = n = 0
            for d in open_:
                for _, kind, f, _ in reads.get((d, arm), []):
                    if kind == "invalid":
                        continue
                    n += 1
                    k += kind == "search" and bs.search_failure(f, data[d], db)
            block[arm] = {"k": k, "n": n, "share": k / n}
        out.setdefault("_blocking", {})[m] = block
        out[m] = {"all 554": aa.paired(reads, ids, "t0", "t1", aa.is_hotel),
                  "brief no type 448": aa.paired(reads, open_, "t0", "t1", aa.is_hotel),
                  "brief hotel 59": aa.paired(reads, spec, "t0", "t1", aa.is_hotel)}
    return out


def release_variant(bad):
    data, g = ra.runs.context()
    sets = ra.request_sets(data, g)
    out = {}
    for m, folder in ra.MODELS.items():
        reads = ra.load(folder, False)
        if reads is None:
            continue
        path = ra.EXPLORE / folder / "raw.jsonl"
        for line in path.read_text().splitlines():
            r = json.loads(line)
            if (folder, r["custom_id"]) in bad:
                _, d, arm, _ = r["custom_id"].split("-")
                reads[(d + ".json", arm)] = [("invalid", "full schema")]
        res = {}
        for s in ("open", "specific"):
            ci, n_pairs, _ = ra.change(reads, sets[s])
            res[s] = {"pairs": n_pairs, "change": ci[0], "interval": [ci[1], ci[2]], "decision": ra.decide(*ci, ra.L)}
        tup = lambda e: (e["change"], *e["interval"])  # noqa: E731
        res["release"] = ra.release(tup(res["open"]), tup(res["specific"]), ra.L, ra.N_MAX, ra.N_MAX)
        out[m] = res
    return out


def steer_variant(bad):
    data, g = ra.runs.context()
    sets = ra.request_sets(data, g)
    cells = tuple(steer.CELL[d] for d in steer.directions())
    out = {}
    for agent, src in sa.SOURCES.items():
        reads, _, missing = sa.load(agent, False)
        if missing:
            continue
        for folder in dict.fromkeys(src.values()):
            wanted = {c for c, f in src.items() if f == folder}
            for line in (ra.EXPLORE / folder / "raw.jsonl").read_text().splitlines():
                r = json.loads(line)
                _, d, cell, _ = r["custom_id"].split("-")
                if cell in wanted and (folder, r["custom_id"]) in bad:
                    reads[(d + ".json", cell)] = [("invalid", "full schema")]
        out[agent] = sa.analyse(reads, sets, cells)["release_rule"]
    return out


def control_variant(bad):
    """The control updates (R10-16) under the rule of control_analyze.py, with every search call that is not valid
    after normalization counted as missing. key "all": all reads; key "read1": read 1 of each arm only."""
    data, g = ra.runs.context()
    db = gold.hotel_db()
    sets = ra.request_sets(data, g)
    out = {}
    for u, (_, (cf, cc), (uf, uc)) in ca.UPDATES.items():
        if not all((ra.EXPLORE / f / "raw.jsonl").exists() for f in (cf, uf)):
            continue
        res = {}
        for key, first_only in (("all", False), ("read1", True)):
            arms, dropped = [], []
            for folder, cell in ((cf, cc), (uf, uc)):
                reads, n = collections.defaultdict(list), 0
                for line in (ra.EXPLORE / folder / "raw.jsonl").read_text().splitlines():
                    r = json.loads(line)
                    _, d, c, read = r["custom_id"].split("-")
                    if c != cell or (first_only and read != "1"):
                        continue
                    if (folder, r["custom_id"]) in bad:
                        reads[d + ".json"].append(("invalid", "full schema"))
                        n += 1
                    else:
                        reads[d + ".json"].append(ra.read_of(r, "t0"))
                arms.append(reads)
                dropped.append(n)
            a = ra.analyse(ca.reads_of(*arms), sets, data, db)
            res[key] = {"dropped": {"control": dropped[0], "update": dropped[1]}, "release": a["release"],
                        "sets": a["sets"], "rates": a["rates"]}
        out[u] = res
    return out


def sign_p(lower, higher):
    """Exact two-sided sign test."""
    n, k = lower + higher, min(lower, higher)
    if n == 0:
        return None
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def pts(x):
    return f"{x:+.1f}"


def markdown(out):
    L = ["## Full-schema validity of the stored tool calls (post hoc)", "",
         "No model call. Each answer of a tool-call arm is checked against the input schema of its own condition "
         "(type, allowed values, anyOf, items, minItems, required keys, no extra keys). Raw: the arguments as stored. "
         "After normalization: after tools.clean_nulls (amendment R10-3). Non-call: no tool call.", "",
         "| Run | Model | Condition | Answers | Not completed | Non-call | Other call | Search calls | Raw valid | "
         "Valid after normalization | Invalid after normalization | Problems after normalization |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for e in out["audit"]:
        c = e["counts"]
        s = c.get("search", 0)
        L.append(f"| {e['run']} | {e['model']} | {e['condition']} | {c.get('answers', 0)} | {c.get('not completed', 0)} | "
                 f"{c.get('non-call', 0)} | {c.get('other call', 0)} | {s} | {c.get('raw valid', 0)} | "
                 f"{c.get('valid after normalization', 0)} | {s - c.get('valid after normalization', 0)} | "
                 f"{json.dumps(e['normalized_problem_kinds'])} |")
    L += ["", "Raw problems per condition (answers with each kind):", ""]
    for e in out["audit"]:
        if e["raw_problem_kinds"]:
            L.append(f"- {e['run']}, {e['model']}, {e['condition']}: {json.dumps(e['raw_problem_kinds'])}")
    L += ["", "Examples of problems after normalization (at most 3 answers per condition):", ""]
    for e in out["audit"]:
        for ex in e["examples"]:
            L.append(f"- {e['run']}, {e['model']}, {e['condition']}: {'; '.join(ex)}")
    L += ["", "### Sensitivity: invalid search calls counted as missing", "",
          "Forward release test (98.75%, 2,000 draws, seed 20261112, L = 5):", ""]
    for m, r in out["variant"]["forward release test"].items():
        for s in ("open", "specific"):
            e = r[s]
            L.append(f"- {m} {s}: {e['pairs']} pairs, {e['change']:+.2f} [{e['interval'][0]:+.2f}, "
                     f"{e['interval'][1]:+.2f}], {e['decision']}")
        L.append(f"- {m}: model decision {r['release']}")
    L += ["", "Steering run (release rule of steer_analyze.py on the hotel value):", ""]
    for m, cells in out["variant"]["steering run"].items():
        for c, e in cells.items():
            sets = "; ".join(f"{s} {x['pairs']} pairs {x['mean']:+.2f} [{x['ci'][0]:+.2f}, {x['ci'][1]:+.2f}] "
                             f"{x['decision']}" for s, x in e["sets"].items())
            L.append(f"- {m} {c}: {sets}; model decision {e['model_decision']}")
    L += ["", "First-request runs, renamed minus original tool (95% interval, a_analyze.paired):", "",
          "| Model | All 554: prefixes, change [95%] | Brief no type 448 | Brief hotel 59 |", "|---|---|---|---|"]
    for m, r in out["variant"]["first request"].items():
        if m == "_blocking":
            continue
        cols = [f"{x['dialogues']}, {pts(100 * x['mean'])} [{pts(100 * x['ci'][0])}, {pts(100 * x['ci'][1])}], "
                f"lower {x['lower']} / higher {x['higher']}"
                for x in (r["all 554"], r["brief no type 448"], r["brief hotel 59"])]
        L.append(f"| {m} | " + " | ".join(cols) + " |")
    L += ["", "Exact two-sided sign test on the 59 prefixes whose brief sets hotel, invalid search calls missing:", ""]
    for m, r in out["variant"]["first request"].items():
        if m == "_blocking":
            continue
        x = r["brief hotel 59"]
        p = sign_p(x["lower"], x["higher"])
        L.append(f"- {m}: lower {x['lower']} / higher {x['higher']}, p = {'-' if p is None else f'{p:.3g}'}")
    L += ["", "Blocking filters on the 448 no-type prefixes, invalid search calls missing (share of valid answers):", ""]
    for m, b in out["variant"]["first request"]["_blocking"].items():
        L.append(f"- {m}: original {100 * b['t0']['share']:.1f}% ({b['t0']['k']}/{b['t0']['n']}), renamed "
                 f"{100 * b['t1']['share']:.1f}% ({b['t1']['k']}/{b['t1']['n']})")
    L += ["", "Control updates (R10-16; rule of control_analyze.py: L = 5, 98.75%, 2,000 draws, seed 20261112), invalid "
          "search calls missing. Post hoc (added after the control results were known):", "",
          "| Update | Reads | Dropped: control / update | Set | Pairs | Rate: control | Rate: update | Change [98.75%] | "
          "Set decision | Update decision |", "|---|---|---|---|---|---|---|---|---|---|"]
    for u, e in out["variant"]["control updates"].items():
        for key, label in (("all", "all reads"), ("read1", "read 1 only")):
            r = e[key]
            for s in ("open", "specific", "guesthouse"):
                x = r["sets"][s]
                a, b = r["rates"][s]["t0"], r["rates"][s]["tedit"]
                iv = "-" if not x["interval"] else f"{x['change']:+.2f} [{x['interval'][0]:+.2f}, {x['interval'][1]:+.2f}]"
                L.append(f"| {u} | {label} | {r['dropped']['control']} / {r['dropped']['update']} | {s} | {x['pairs']} | "
                         f"{100 * a['share']:.1f}% ({a['k']}/{a['n']}) | {100 * b['share']:.1f}% ({b['k']}/{b['n']}) | "
                         f"{iv} | {x['decision'] or 'no decision'} | {r['release'] if s == 'open' else ''} |")
    return "\n".join(L) + "\n"


def main():
    table, bad = audit()
    out = {"post_hoc": True, "no_model_call": True, "audit": table, "invalid_after_normalization": len(bad),
           "variant": {"forward release test": release_variant(bad), "steering run": steer_variant(bad),
                       "first request": first_request_variant(bad), "control updates": control_variant(bad)}}
    OUT.mkdir(exist_ok=True)
    (OUT / "tool_validity.json").write_text(json.dumps(out, indent=1))
    (OUT / "tool_validity.md").write_text(markdown(out))
    print((OUT / "tool_validity.md").read_text())


if __name__ == "__main__":
    main()
