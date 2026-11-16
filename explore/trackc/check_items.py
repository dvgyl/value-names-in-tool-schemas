"""Mechanical checks of every E4 item and form. Prints one line per check and exits 1 when any check fails.

Usage: python3 -I check_items.py
"""
import ast
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import templates as tp  # noqa: E402

PROTOTYPES = HERE.parents[1]
MIN_WORDS = 4  # shorter MultiWOZ turns ("thank you", "yes please") are stock phrases; they must still not be a whole item turn
MENTION = {
    "area": {v: rf"\b{v}\b" for v in tp.ALLOWED["area"]},
    "pricerange": {"cheap": r"\bcheap\b", "moderate": r"\bmoderate(ly)?\b", "expensive": r"\bexpensive\b"},
    "stars": {v: rf"\b{v} stars?\b" for v in tp.ALLOWED["stars"]},
    "type": {"hotel": r"\bhotels?\b", "guesthouse": r"\bguest ?houses?\b|\bbed and breakfast\b"},
    "parking": {"yes": r"\bparking\b"},
    "internet": {"yes": r"\binternet\b|\bwi-?fi\b"},
    "name": {h["name"]: re.escape(h["name"]) for h in tp.HOTELS},
}
RESOLVING = {  # sentences that would settle the target field of an ambiguous item
    "a": r"\bguest ?houses?\b|\bbed and breakfast\b|\breal hotel\b",
    "b": r"\b(need|must|have to|require|driving|car)\b[^.?]*\bparking\b|\bparking\b[^.?]*\b(must|need)",
    "c": r"\b(first|second) choice\b|\bstill\b|\bif there is nothing\b|\bfall ?back\b",
}


def traveller(item, negated=True):
    """The traveller's sentences in lower case. With negated=False, sentences that hold "not" are left out."""
    said = [s.lower() for turn in item.turns[::2] for _, s in turn]
    return " ".join(s for s in said if negated or not re.search(r"\bnot\b", s))


def mentioned(field, text):
    """The values of one field that a text mentions, in the order of their first mention."""
    hits = [(m.start(), v) for v, rx in MENTION[field].items() if (m := re.search(rx, text))]
    return [v for _, v in sorted(hits)]


def expected_readings(item):
    """The target reading set, recomputed from the traveller's words only."""
    said = mentioned(item.target, traveller(item, negated=False))
    if item.condition == "c":
        assert len(said) == 2, f"{item.id}: two target values expected, found {said}"
        v0, v1 = said
        return {(v0, v1)} if item.kind == "clear" else {(v1,), (v0, v1)}
    if item.kind == "clear":
        assert len(said) == 1, f"{item.id}: one target value expected, found {said}"
        return {(said[0],)}
    return {None} if item.condition == "d" else {None, (said[0],)}


def check_ids(items):
    bad = [x for x in [f.id for f in tp.FAMILIES] + [i.goal.id for i in items] + [i.id for i in items] if x[0] != "x"]
    bad += ["duplicate item ids"] * (len({i.id for i in items}) != len(items))
    for c in tp.CONDITIONS:
        goals = {i.goal.id for i in items if i.condition == c}
        families = {f.id for f in tp.FAMILIES if f.condition == c}
        if len(goals) != tp.GOALS_PER_CONDITION or len(families) < 2:
            bad.append(f"condition {c}: {len(goals)} goals, {len(families)} families")
        for g in goals:
            kinds = sorted(i.kind for i in items if i.goal.id == g)
            if kinds != ["ambiguous", "clear"]:
                bad.append(f"{g}: items {kinds}")
    return len(items), bad


def check_pairs(items):
    """The clear control minus its clarifying sentences equals the ambiguous item, turn by turn and word for word.

    For condition d, this is: adding the stating sentence to the ambiguous item gives the clear control.
    """
    by = {(i.goal.id, i.kind): i for i in items}
    bad = []
    for item in items:
        roles = [r for turn in item.turns for r, _ in turn]
        if item.text.count("\n") + 1 != len(item.turns) or not all(item.turns) or re.search(r"[{}]", item.text):
            bad.append(f"{item.id}: an empty turn, a broken line, or an unfilled slot")
        triggers, clarify = roles.count(tp.TRIGGER), roles.count(tp.CLARIFY)
        if item.kind == "ambiguous" and (clarify or (triggers == 0) != (item.condition == "d")):
            bad.append(f"{item.id}: {triggers} trigger and {clarify} clarifying sentences")
        if item.kind == "clear" and not clarify:
            bad.append(f"{item.id}: no clarifying sentence")
    for (g, kind), clear in by.items():
        if kind != "clear":
            continue
        amb = by[(g, "ambiguous")]
        stripped = []
        for turn, line in zip(clear.turns, [line.split(": ", 1)[1] for line in clear.text.split("\n")]):
            for role, s in turn:
                if role == tp.CLARIFY:
                    line = line.replace(s, "", 1)
            stripped.append(" ".join(line.split()))
        if stripped != [line.split(": ", 1)[1] for line in amb.text.split("\n")]:
            bad.append(f"{g}: the pair differs outside the clarifying sentences")
    return len(by) // 2, bad


def check_wording(items):
    """No ambiguous item holds a resolving sentence, and no text mentions a field that every interpretation leaves null."""
    bad = []
    for item in items:
        if item.kind == "ambiguous" and item.condition in RESOLVING and re.search(RESOLVING[item.condition], item.text.lower()):
            bad.append(f"{item.id}: resolving wording")
        if item.kind == "ambiguous" and item.condition == "b":
            asks = [s for turn in item.turns[::2] for _, s in turn if "parking" in s.lower()]
            if not asks or not all(s.endswith("?") for s in asks):
                bad.append(f"{item.id}: the traveller states parking instead of asking about it")
        for f in tp.FIELDS:
            if all(i[f] is None for i in item.interpretations) and mentioned(f, traveller(item)):
                bad.append(f"{item.id}: the traveller mentions {f}, which every interpretation leaves null")
        if item.condition != "a" and re.search(MENTION["type"]["hotel"], item.text.lower()):
            bad.append(f"{item.id}: the collision word hotel outside condition a")
    return len(items), bad


def valid_form(form):
    if tuple(form) != tp.FIELDS:
        return False
    for f, v in form.items():
        domain = [h["name"] for h in tp.HOTELS] if f == "name" else tp.ALLOWED[f]
        ok = v is None or v == "any" or (isinstance(v, tuple) and v and len(set(v)) == len(v) and set(v) <= set(domain))
        if not ok:
            return False
    return bool(tp.matches(form))


def check_interpretations(items):
    bad = []
    for item in items:
        interps = item.interpretations
        if not all(valid_form(i) for i in interps):
            bad.append(f"{item.id}: an interpretation that is not a valid form or that no hotel matches")
        rest = {json.dumps({f: v for f, v in i.items() if f != item.target}) for i in interps}
        if len(rest) != 1:
            bad.append(f"{item.id}: interpretations differ outside the target field")
        others = {f: v for f, v in interps[0].items() if f != item.target and v is not None}
        if any(mentioned(f, traveller(item)) != list(v) for f, v in others.items()):
            bad.append(f"{item.id}: a stated field that the traveller's words do not give")
        readings = [i[item.target] for i in interps]
        try:
            want = expected_readings(item)
        except AssertionError as e:
            bad.append(str(e))
            continue
        if set(readings) != want or len(readings) != len(want):
            bad.append(f"{item.id}: stored readings {readings}, recomputed {sorted(want, key=str)}")
        if item.kind == "clear":
            base = tp.matches(interps[0] | {item.target: None})
            first, *_ = interps[0][item.target]
            if item.condition == "c":
                v0, v1 = interps[0][item.target]
                fact = not base & tp.accepts(item.target, (v0,)) and base & tp.accepts(item.target, (v1,))
            else:
                narrowed = base & tp.accepts(item.target, (first,))
                fact = narrowed and narrowed != base
            if not fact:
                bad.append(f"{item.id}: the database does not make the dialogue true")
    return len(items), bad


def words(text):
    return tuple(re.findall(r"[a-z0-9']+", text.lower()))


def check_multiwoz(items):
    data = json.loads((tp.anth.DATA / "data.json").read_text())
    turns = {words(t["text"]) for d in data.values() for t in d["log"]}
    long = {}
    for t in turns:
        if len(t) >= MIN_WORDS:
            long.setdefault(len(t), set()).add(t)
    bad = []
    for item in items:
        for turn in item.turns:
            w = words(" ".join(s for _, s in turn))
            if w in turns:
                bad.append(f"{item.id}: the turn '{' '.join(w)}' is a MultiWOZ turn")
            for n, pool in long.items():
                bad += [f"{item.id}: holds the MultiWOZ turn '{' '.join(w[i:i + n])}'"
                        for i in range(len(w) - n + 1) if w[i:i + n] in pool]
    return f"{len(items)} items against {len(turns)} distinct turns of {len(data)} dialogues", sorted(set(bad))


def script_system(path):
    tree = ast.parse(path.read_text())
    return next(n.value for n in tree.body if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == "SYSTEM")


def check_forms(_):
    p4 = ast.literal_eval(script_system(PROTOTYPES / "p4_multiwoz" / "run.py"))
    node, calls = script_system(PROTOTYPES / "p5_unclear" / "run.py"), []
    while isinstance(node, ast.Call):
        calls.append([ast.literal_eval(a) for a in node.args])
        node = node.func.value
    p5 = p4
    for old, new in reversed(calls):
        p5 = p5.replace(old, new)
    bad = []
    if tp.P4_SYSTEM != p4:
        bad.append("P4_SYSTEM differs from p4_multiwoz/run.py")
    if tp.FORMS["p_unclear"] != p5:
        bad.append("p_unclear differs from the P5 prompt")
    if tp.FORMS["p_main"] != p5.replace(tp.AMBIGUITY, "") or "unclear" in tp.FORMS["p_main"]:
        bad.append("p_main is not the P5 prompt without the ambiguity sentence")
    if tp.FORMS["p_null"] != p5.replace('write "unclear"', "write null") or "unclear" in tp.FORMS["p_null"]:
        bad.append("p_null is not the P5 prompt with 'write null' in place of 'write \"unclear\"'")
    return len(tp.FORMS), bad


CHECKS = {
    "ids start with x, 40 goals and 2 or more families per condition, one pair per goal": check_ids,
    "clear control = ambiguous item + clarifying sentences (condition d: + the stating sentence)": check_pairs,
    "no resolving wording in an ambiguous item, no mention of a field left null": check_wording,
    "interpretations are valid forms, match the recomputed reading sets and the database": check_interpretations,
    f"no item turn is a MultiWOZ turn, no item holds a MultiWOZ turn of {MIN_WORDS} or more words": check_multiwoz,
    "p_unclear = P5 prompt, p_main = P5 without the sentence, p_null = P5 with 'write null'": check_forms,
}


def check():
    items = tp.items()
    return [(name, *fn(items)) for name, fn in CHECKS.items()]


if __name__ == "__main__":
    failed = False
    for name, checked, bad in check():
        print(f"{'FAIL' if bad else 'PASS'}  {name} ({checked} checked)")
        for b in bad[:20]:
            print(f"      {b}")
        failed |= bool(bad)
    print("FAIL" if failed else "PASS: every E4 item and form passes")
    sys.exit(1 if failed else 0)
