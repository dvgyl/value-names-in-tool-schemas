"""Test of n1_heldout_stored.extract with a constructed stored row (values chosen by hand). Run: python3 -I <file>"""
import importlib.util
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("n1", HERE / "n1_heldout_stored.py")
n1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n1)


def pol(avoided, ended, caused, lost, gained):
    return {"net_avoided_NT": avoided, "failures_ended_NT": ended, "failures_caused_NT": caused,
            "losses_caused_H": lost, "losses_ended_H": gained, "net_added_H": lost - gained}


row = {"missing": {}, "read1": {
    "verifier_answers": {"NT": {"yes": 3, "no": 19, "unclear": 8}, "H": {"yes": 20, "no": 10, "unclear": 16},
                         "G": {"yes": 0, "no": 0, "unclear": 0}},
    "display": {"dialogues": {"NT": 213, "H": 66, "G": 11}, "answers": 290,
                "original": {"failures_NT": 20.0, "losses_H": 5.0, "failures_G": 0.0},
                "searches_per_answer": {"planned": 1.0, "relax_any": 1 + 14 / 290, "soft": 1 + 79 / 290},
                "relax_any_on_H": {"dialogues_changed": 1, "stated_dialogues_changed": 1},
                "planned": pol(10, 10, 0, 2, 0), "relax_any": pol(10, 10, 0, 0, 0), "soft": pol(10, 10, 0, 0, 0)}}}
r = n1.extract(row)
# By hand: calls 3 + 19 + 8 + 20 + 10 + 16 = 76; second searches 14 and 79; the verifier lost 2 and gained 0.
assert r["verifier_calls"] == 76
assert r["policies"]["relax_any"]["second_searches"] == 14 and r["policies"]["soft"]["second_searches"] == 79
assert r["policies"]["planned"]["gross_losses_H"] == 2 and r["policies"]["planned"]["net_added_H"] == 2
assert r["policies"]["planned"]["second_searches"] == 0 and r["policies"]["soft"]["model_calls"] == 0
assert r["guesthouse_newly_shown_stated_H"]["planned"] is None
# A symbolic policy with a stored gross loss must stop the extraction.
bad = {**row, "read1": {**row["read1"], "display": {**row["read1"]["display"], "soft": pol(10, 10, 0, 1, 0)}}}
try:
    n1.extract(bad)
    raise SystemExit("FAILED: a stored loss of the soft filter did not stop the extraction")
except AssertionError:
    pass
print("test_n1_heldout_stored: all tests passed")
