"""Prompt test: p4 and p5 are byte-identical to the prototype scripts, and each form adds only its intended part.

Usage: python3 -I test_prompts.py
"""
import ast
import difflib
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import common  # noqa: E402

NAME_PART = ["name,", "Give name as the hotel name if the traveller asked for one hotel by name, else null."]
UNCLEAR_PART = ["If the traveller's words allow more than one reasonable reading for a field, write \"unclear\" "
                "for that field instead of choosing a reading."]
OFFER_PART = ["An option that the traveller only accepted from the assistant's offers is not a requirement."]
INTENDED = {"p4": [], "p4_name": NAME_PART, "p4_unclear": UNCLEAR_PART, "p5": NAME_PART + UNCLEAR_PART,
            "p_main": NAME_PART + OFFER_PART}


def script_system(path):
    tree = ast.parse(path.read_text())
    return next(n.value for n in tree.body if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == "SYSTEM")


def p4_script_system():
    return ast.literal_eval(script_system(common.P4_DIR / "run.py"))


def p5_script_system(p4_system):
    node, calls = script_system(common.P4_DIR.parent / "p5_unclear" / "run.py"), []
    while isinstance(node, ast.Call):
        assert node.func.attr == "replace", ast.unparse(node)
        calls.append([ast.literal_eval(a) for a in node.args])
        node = node.func.value
    assert ast.unparse(node) == "p4.SYSTEM", ast.unparse(node)
    for old, new in reversed(calls):
        p4_system = p4_system.replace(old, new)
    return p4_system


def insertions(base, other):
    a, b = base.split(" "), other.split(" ")
    ops = difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
    changed = [op for op in ops if op[0] != "equal"]
    assert all(op[0] == "insert" for op in changed), f"text removed or replaced: {changed}"
    return [" ".join(b[j1:j2]) for _, _, _, j1, j2 in changed]


def main():
    p4 = p4_script_system()
    assert common.FORMS["p4"].system == p4, "p4 prompt differs from p4_multiwoz/run.py"
    assert common.FORMS["p5"].system == p5_script_system(p4), "p5 prompt differs from p5_unclear/run.py"
    for name, form in common.FORMS.items():
        if form.renamed:
            base = name.removesuffix("_renamed")
            expected = common.FORMS[base].system.replace(", stars, type, parking,", ", stars, property_kind, parking,")
            expected = expected.replace("type: guesthouse, hotel.", "property_kind: guesthouse, large_property.")
            assert form.system == expected and form.system != common.FORMS[base].system, f"{name}: not exactly {base} renamed"
            assert (form.name, form.unclear) == (common.FORMS[base].name, common.FORMS[base].unclear), name
            print(f"--- {name}: {base} with type renamed property_kind and hotel renamed large_property, nothing else")
            continue
        added = insertions(p4, form.system)
        print(f"--- {name} (name field {form.name}, unclear option {form.unclear})\n{form.system}\n  added to p4: {added}")
        assert added == INTENDED[name], f"{name}: added {added}, intended {INTENDED[name]}"
        assert form.name == bool(set(NAME_PART) & set(added)) and form.unclear == bool(set(UNCLEAR_PART) & set(added))
    print("prompt test passed: p4 and p5 match the scripts byte for byte; each form adds only its intended part")


if __name__ == "__main__":
    main()
