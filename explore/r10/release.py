"""Amendment R10-6 (PROTOCOL.md): a forward run of the release test of Section 8 of the paper
(the paper), on a tool edit that the authors did not write. Exploratory.

1. `rewrite`: Claude Opus 5.5 (models.MODELS["opus"], account anthropic_r9a) acts as the developer. One user message:
   REWRITE_TEXT, two line breaks, and the JSON of tools.SEARCH_T0 (name, description, input_schema; indent 2). No system
   text and no answer format. Synchronous calls, at most MAX_CALLS. Every answer goes into release/answers.jsonl. The
   first answer that `accept` takes is frozen as release/edit.json. Ledger row: experiment "erp_edit", step "rewrite".
2. `build` (runs erp_sonnet and erp_sol, r10/runs.py): arm t0 (the request of build_a) and arm tedit (the same user and
   system texts, tools = [the edited tool], strict) on the 554 prefixes of experiment A.
3. `parse_call(row, "tedit")`: the call goes back to the F0 names and values (value_map reversed), then natural.parse
   with form f0, as tools.parse_call does for t0.
Usage (from explore/): .venv/bin/python -I r10/release.py rewrite [--approve <bound>] | show | check
"""
import hashlib
import itertools
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXPLORE = HERE.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(HERE))
import natural  # noqa: E402
import tools  # noqa: E402
import zforms  # noqa: E402

REWRITE_TEXT = (
    "You maintain a search tool that an AI booking agent calls. Its JSON definition follows. Rewrite the definition to "
    "make it clearer for the agent. Keep the tool name search_hotels, the same parameters and the same options with the "
    "same meaning; you may rename parameter names and option values and rewrite every description. Return only one "
    "JSON object with two keys: \"tool\" (the new definition, with the keys name, description and input_schema) and "
    "\"value_map\" (for each parameter, a map from each old option value to its new value; use the same value when you "
    "keep a name)."
)
ACCOUNT, MODEL, MAX_CALLS, LEDGER_NAME = "anthropic_r9a", "opus", 3, "erp_edit"
MAX_BOUND = 6.00  # USD per run of R10-6 (pilot or batch)
RELEASE = HERE / "release"
EDIT, ANSWERS, REQUEST = RELEASE / "edit.json", RELEASE / "answers.jsonl", RELEASE / "request.json"
AMENDMENT = "### R10-6 "
TOOL_NAME = "search_hotels"
# Keywords that both providers take in a strict tool schema (claude-api skill, structured outputs; OpenAI structured
# outputs guide). Any other keyword (for example default, examples, minimum, maxItems, $ref) makes an answer invalid.
ALLOWED = {"type", "enum", "const", "anyOf", "items", "properties", "required", "additionalProperties", "description",
           "title", "minItems"}
TYPES = {"null", "string", "array", "boolean", "integer", "number", "object"}


class Invalid(ValueError):
    """An answer that the acceptance rule of R10-6 does not take; the message is the reason."""


def original():
    return {k: tools.SEARCH_T0[k] for k in ("name", "description", "input_schema")}


def rewrite_user():
    return REWRITE_TEXT + "\n\n" + json.dumps(original(), indent=2)


def rewrite_request():
    import models
    return models.request(MODEL, "erp_edit-rewrite", rewrite_user(), None, None)


def key(v):
    """A hashable key of a JSON value that keeps its type ("1" and 1 differ)."""
    return json.dumps(v, sort_keys=True)


def types_of(node):
    t = node.get("type")
    return t if isinstance(t, list) else [] if t is None else [t]


def strict_problems(node, path="input_schema"):
    """The reasons why a schema is not valid for strict tool calls on both providers (an empty list: valid)."""
    if not isinstance(node, dict):
        return [f"{path} is not an object"]
    out = [f"{path}: keyword {k!r}" for k in node if k not in ALLOWED]
    if "minItems" in node and node["minItems"] not in (0, 1):
        out.append(f"{path}: minItems {node['minItems']!r}")
    if any(t not in TYPES for t in types_of(node)):
        out.append(f"{path}: type {node.get('type')!r}")
    if "enum" in node and not isinstance(node["enum"], list):
        out.append(f"{path}: enum is not a list")
    if "object" in types_of(node) or "properties" in node:
        props = node.get("properties")
        if not isinstance(props, dict):
            return out + [f"{path}: an object without properties"]
        if node.get("additionalProperties") is not False:
            out.append(f"{path}: additionalProperties is not false")
        if not isinstance(node.get("required"), list) or set(node["required"]) != set(props):
            out.append(f"{path}: required does not list every property")
        for name, sub in props.items():
            out += strict_problems(sub, f"{path}.{name}")
    if "anyOf" in node:
        if not isinstance(node["anyOf"], list):
            out.append(f"{path}: anyOf is not a list")
        else:
            for i, sub in enumerate(node["anyOf"]):
                out += strict_problems(sub, f"{path}.anyOf[{i}]")
    if "items" in node:
        out += strict_problems(node["items"], f"{path}.items")
    return out


def value_space(node):
    """(options, null_ok, free, nested) of one parameter schema. options: {key: value} of its enum and const values
    (and true and false of a boolean type without enum); null_ok: null is allowed; free: a string or number without
    enum or const is allowed; nested: an object is inside."""
    opts, flags = {}, {"null": False, "free": False, "nested": False}

    def walk(n):
        if not isinstance(n, dict):
            return
        ts = types_of(n)
        listed = "enum" in n or "const" in n
        for v in (n.get("enum") or []) + ([n["const"]] if "const" in n else []):
            if v is None:
                flags["null"] = True
            else:
                opts[key(v)] = v
        flags["null"] |= "null" in ts
        flags["free"] |= not listed and any(t in ts for t in ("string", "integer", "number"))
        flags["nested"] |= "object" in ts or "properties" in n
        if "boolean" in ts and not listed:
            opts.update({key(True): True, key(False): False})
        for sub in n.get("anyOf") or []:
            walk(sub)
        if "items" in n:
            walk(n["items"])
    walk(node)
    return opts, flags["null"], flags["free"], flags["nested"]


def spaces(schema):
    return {p: value_space(s) for p, s in schema["properties"].items()}


def pair_map(p, q, old, new, vm):
    """{key(old value): new value} when the new parameter q keeps exactly the options of the old parameter p under
    value_map (keyed by p or by q; an old value that value_map does not name keeps its value), still accepts null and
    holds no object; for name (no options): q accepts any string and null and has no options. Else None."""
    o_opts, _, _, _ = old[p]
    n_opts, n_null, n_free, n_nested = new[q]
    if not n_null or n_nested:
        return None
    if not o_opts:
        return {} if n_free and not n_opts else None
    if n_free:
        return None
    entries = [vm[k] for k in dict.fromkeys((p, q)) if k in vm]
    if len(entries) == 2 and entries[0] != entries[1]:
        return None
    m = entries[0] if entries else {}
    if not isinstance(m, dict):
        return None
    mapped = {k: m.get(v, v) for k, v in o_opts.items()}
    images = [key(v) for v in mapped.values()]
    if len(set(images)) != len(images) or set(images) != set(n_opts):
        return None
    return mapped


def param_map(old, new, vm):
    """Rule P of R10-6: a kept name maps to itself; the renamed parameters map by the only one-to-one assignment that
    uses pairs for which pair_map is not None. No such assignment, or more than one: Invalid."""
    fixed = {p: p for p in old if p in new}
    for p in fixed:
        if pair_map(p, p, old, new, vm) is None:
            raise Invalid(f"parameter {p}: its options, null or free text are not kept under value_map")
    rest_old = [p for p in old if p not in fixed]
    rest_new = [q for q in new if q not in old]
    if len(rest_old) != len(rest_new):
        raise Invalid(f"{len(new)} parameters instead of {len(old)}")
    found = [dict(zip(rest_old, perm)) for perm in itertools.permutations(rest_new)
             if all(pair_map(p, q, old, new, vm) is not None for p, q in zip(rest_old, perm))]
    if not found:
        raise Invalid(f"no mapping of the renamed parameters {rest_old} to {rest_new} keeps every option")
    if len(found) > 1:
        raise Invalid(f"the mapping of the renamed parameters is not explicit: {len(found)} mappings fit")
    return {**fixed, **found[0]}


def texts(node):
    """Every description and title string in a schema."""
    if isinstance(node, dict):
        own = [v for k, v in node.items() if k in ("description", "title") and isinstance(v, str)]
        return own + [t for v in node.values() for t in texts(v)]
    if isinstance(node, list):
        return [t for v in node for t in texts(v)]
    return []


def answer_object(text):
    """The JSON object from the first "{" to the last "}" of the answer text."""
    s, e = text.find("{"), text.rfind("}")
    if s < 0 or e < s:
        raise Invalid("no JSON object in the answer")
    try:
        obj = json.loads(text[s:e + 1])
    except ValueError as x:
        raise Invalid(f"not valid JSON: {x}") from None
    if not isinstance(obj, dict):
        raise Invalid("the JSON is not an object")
    return obj


def accept_obj(obj):
    """The acceptance rule of R10-6 for one answer object. Returns (params, values): {old name: new name} and
    {old name: {key(old value): new value}}. Raises Invalid with the reason."""
    import groups as grp
    if not {"tool", "value_map"} <= set(obj):
        raise Invalid(f"keys {sorted(obj)}, not tool and value_map")
    tool, vm = obj["tool"], obj["value_map"]
    if not isinstance(tool, dict) or not {"name", "description", "input_schema"} <= set(tool):
        raise Invalid("tool does not hold name, description and input_schema")
    if tool["name"] != TOOL_NAME:
        raise Invalid(f"tool name {tool['name']!r}")
    if not isinstance(tool["description"], str) or not tool["description"].strip():
        raise Invalid("no tool description")
    if not isinstance(vm, dict):
        raise Invalid("value_map is not an object")
    problems = strict_problems(tool["input_schema"])
    if problems:
        raise Invalid("not valid for strict tool calls: " + "; ".join(problems[:6]))
    old, new = spaces(tools.SEARCH_T0["input_schema"]), spaces(tool["input_schema"])
    params = param_map(old, new, vm)
    values = {p: pair_map(p, q, old, new, vm) for p, q in params.items()}
    try:
        grp.assert_new_text([tool["description"]] + texts(tool["input_schema"]))
    except ValueError as x:
        raise Invalid(f"a text copies a main-study item: {x}") from None
    return params, values


def accept(row):
    """The acceptance rule for one answer row (anth.message_row): the answer ended normally and its object passes
    accept_obj. Returns the object."""
    if row.get("stop") != "end_turn":
        raise Invalid(f"stop {row.get('stop')!r}")
    obj = answer_object(row.get("text") or "")
    accept_obj(obj)
    return obj


_edit = {}


def edit():
    """The frozen edit: {"obj", "params", "values", "rev"}; rev: {old name: {key(new value): old value}}."""
    if "obj" not in _edit:
        if not EDIT.exists():
            sys.exit(f"Not built. {EDIT} does not exist; run the rewrite step of R10-6 first.")
        obj = json.loads(EDIT.read_text())
        params, values = accept_obj(obj)
        rev = {p: {key(new): json.loads(k) for k, new in m.items()} for p, m in values.items()}
        _edit.update(obj=obj, params=params, values=values, rev=rev)
    return _edit


def tedit_tool():
    t = edit()["obj"]["tool"]
    return tools.tool(t["name"], t["description"], t["input_schema"])


def new_texts():
    t = edit()["obj"]["tool"]
    return (t["description"], *texts(t["input_schema"]))


def to_old(args):
    """A tedit call's arguments with the F0 names and values (after tools.clean_nulls, amendment R10-3)."""
    e = edit()
    args = tools.clean_nulls(args)
    out = {}
    for p, q in e["params"].items():
        rev = e["rev"][p]
        back = lambda x: rev.get(key(x), x)  # noqa: E731
        v = args.get(q)
        out[p] = None if v is None else [back(x) for x in v] if isinstance(v, list) else back(v)
    return out


def parse_call(row, arm):
    """As tools.parse_call. Arm tedit: one search_hotels call, mapped back by to_old, then natural.parse with f0."""
    if arm != "tedit":
        return tools.parse_call(row, arm)
    calls = row.get("tool_calls") or []
    if not calls:
        return ("none", row.get("text", ""))
    if len(calls) > 1:
        return ("invalid", f"{len(calls)} tool calls")
    c = calls[0]
    if c["name"] != TOOL_NAME or not isinstance(c.get("input"), dict):
        return ("invalid", f"tool {c.get('name')!r} with input {type(c.get('input')).__name__}")
    try:
        return ("search", natural.parse(json.dumps(to_old(c["input"])), natural.FORMS["f0"]))
    except (ValueError, KeyError, TypeError) as x:
        return ("invalid", f"{type(x).__name__}: {x}")


def build(name, model, reads, data, g):
    """Arms t0 (the request of runs.build_a, unchanged) and tedit, on the 554 prefixes."""
    import models
    import runs
    edited, system = tedit_tool(), tools.tool_system("t0")
    out = []
    for d in g["booked"]:
        user = zforms.prefix_text(data[d])
        for read in range(1, reads + 1):
            out.append(models.request(model, runs.cid(name, d, "t0", read), user, system, None,
                                      tools=tools.TOOLS["t0"], cell="t0"))
            out.append(models.request(model, runs.cid(name, d, "tedit", read), user, system, None, tools=[edited],
                                      cell="tedit"))
    return out


def amendment_text():
    import runs
    text = runs.PROTOCOL.read_text().split(runs.AMEND, 1)[-1]
    if AMENDMENT not in text:
        return None
    body = text.split(AMENDMENT, 1)[1]
    ends = [i for i in (body.find("\n## "), body.find("\n### ")) if i >= 0]
    return AMENDMENT + body[:min(ends)] if ends else AMENDMENT + body


def sha256():
    return hashlib.sha256(EDIT.read_bytes()).hexdigest() if EDIT.exists() else None


def check_amendment(require_log=True):
    """R10-6 is in PROTOCOL.md under the round-10 amendments, holds REWRITE_TEXT verbatim, and (require_log) holds the
    SHA-256 of release/edit.json."""
    text = amendment_text()
    if text is None:
        sys.exit(f"Not run. PROTOCOL.md has no amendment {AMENDMENT.strip()!r}.")
    if REWRITE_TEXT not in " ".join(text.split()):
        sys.exit("Not run. The amendment does not hold REWRITE_TEXT verbatim.")
    if require_log and (sha256() is None or sha256() not in text):
        sys.exit(f"Not run. The amendment does not hold the SHA-256 of {EDIT.name}.")


def rewrite(approve):
    import accounts
    import anth
    import budget_gate
    import runs
    runs.check_lock()
    check_amendment(require_log=False)
    if EDIT.exists():
        sys.exit(f"Not run. {EDIT} exists; the edit is frozen.")
    a = accounts.account(ACCOUNT, ("anthropic",))
    req = rewrite_request()
    done = [json.loads(x) for x in ANSWERS.read_text().splitlines()] if ANSWERS.exists() else []
    if len(done) >= MAX_CALLS:
        sys.exit(f"Not run. {len(done)} calls made and none accepted; the runs of R10-6 do not go.")
    p = req["params"]
    left = MAX_CALLS - len(done)
    bound = round(left * anth.cost(p["model"], anth.est_in(req) * 1.5, p["max_tokens"], batch=False), 2)
    print(f"rewrite: at most {left} synchronous calls, hard bound {bound:.2f} USD at max_tokens and list prices")
    if approve is not None and not budget_gate.fits(ACCOUNT, bound):
        sys.exit(f"Not run. {bound:.2f} USD does not fit the free money of {ACCOUNT} minus the reserve.")
    accounts.check_approval(a, approve, bound)
    RELEASE.mkdir(exist_ok=True)
    REQUEST.write_text(json.dumps(req, indent=1) + "\n")
    cl = anth.client(a)
    held = accounts.hold(a, LEDGER_NAME, "rewrite", bound)
    spent, obj = 0.0, None
    try:
        for i in range(len(done) + 1, MAX_CALLS + 1):
            msg = cl.messages.create(**p)
            spent += anth.cost(msg.model, msg.usage.input_tokens, msg.usage.output_tokens, batch=False)
            row = anth.message_row(f"erp_edit-rewrite-{i}", msg)
            try:
                obj, ok, reason = accept(row), True, "accepted"
            except Invalid as x:
                ok, reason = False, str(x)
            with open(ANSWERS, "a") as fh:
                fh.write(json.dumps({"call": i, "utc": accounts.now(timespec="seconds"), "accepted": ok,
                                     "reason": reason, "row": row}) + "\n")
            print(f"call {i}: stop {row['stop']}, out {row['output_tokens']} tokens: {reason}")
            if ok:
                break
    finally:
        accounts.ledger(a, LEDGER_NAME, "rewrite", bound, spent)
        held.unlink()
        try:
            held.parent.rmdir()
        except OSError:
            pass
    print(f"spent {spent:.4f} USD at list prices")
    if obj is None:
        sys.exit("No answer accepted.")
    EDIT.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")
    print(f"{EDIT.relative_to(EXPLORE)} SHA-256 {sha256()}")


def show():
    e = edit()
    print(f"SHA-256 {sha256()}")
    for p, q in e["params"].items():
        vals = {json.loads(k): v for k, v in e["values"][p].items()}
        print(f"  {p} -> {q}: {json.dumps(vals)}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "rewrite":
        rewrite(sys.argv[sys.argv.index("--approve") + 1] if "--approve" in sys.argv else None)
    elif cmd == "show":
        show()
    elif cmd == "check":
        check_amendment()
        print("R10-6 holds the text and the SHA-256 of edit.json")
    else:
        sys.exit(__doc__)
