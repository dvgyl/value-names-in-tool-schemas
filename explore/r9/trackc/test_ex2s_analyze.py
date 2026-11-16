"""Offline test of ex2s_analyze.py on synthetic rows. No API call. onsite/test_analyze.py tests the scorer itself.

1. Each X2 row reaches the model, arm, and read of its custom_id; no row is lost or given to another model.
2. Q5 holds with the renamed arm lower for 3 of 5 models, fails with 2, and is open while a model has no rate.
3. The E2 model table is back to the Claude models after the wrapper runs.
Run:  harness/.venv/bin/python r9/trackc/test_ex2s_analyze.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ex2s_analyze as xa  # noqa: E402
import tasks  # noqa: E402
import x2s  # noqa: E402

CASES, MAP_BACK = tasks.e2.onsite_cases(), tasks.e2.load_p3().map_back
CLAUDE = dict(tasks.e2.MODELS)


def test_rows():
    rows = []
    for cid, case, arm, read, short in x2s.cells("openai", tasks.onsite_table()):
        if short == "luna":
            rows.append({"custom_id": cid, "type": "errored", "error": "synthetic"})
        elif arm == "orig" and read == 1:
            rows.append({"custom_id": cid, "type": "succeeded", "model": "gpt-6.1-sol", "stop": "max_tokens",
                         "input_tokens": 1300, "output_tokens": 4000, "text": ""})
    s = xa.summarize(rows, "openai", CASES, MAP_BACK)
    luna, sol = s["models"]["gpt-6-luna"], s["models"]["gpt-6.1-sol"]
    assert all(luna[arm]["pooled"]["error"] == 190 and luna[arm]["pooled"]["absent"] == 0 for arm in tasks.e2.ARMS)
    assert sol["orig"]["per_read"]["1"]["truncated"] == 38 and sol["orig"]["pooled"]["absent"] == 152
    assert sol["office"]["pooled"]["absent"] == sol["renamed"]["pooled"]["absent"] == 190
    assert s["rows"] == len(rows) and s["expected_rows"] == 1140 and set(s["models"]) == {"gpt-6.1-sol", "gpt-6-luna"}
    assert tasks.e2.MODELS == CLAUDE, "the wrapper left the X2 model table in place"
    print("1. rows reach their model, arm, and read; the E2 model table is restored")


def summary(rates):
    pooled = lambda wrong: {"right": 100 - wrong, "wrong": wrong, "parse_fail": 0}  # noqa: E731
    return {"models": {m: {"orig": {"pooled": pooled(o)}, "renamed": {"pooled": pooled(r)}} for m, (o, r) in rates.items()}}


def test_q5():
    three = {"m1": (10, 5), "m2": (10, 5), "m3": (10, 5), "m4": (5, 10), "m5": (5, 5)}
    assert xa.q5([summary(three)])["q5_holds"] is True
    assert xa.q5([summary({**three, "m3": (5, 10)})])["q5_holds"] is False
    open_ = summary(three)
    open_["models"]["m5"]["renamed"]["pooled"] = {"right": 0, "wrong": 0, "parse_fail": 0}
    assert xa.q5([open_])["q5_holds"] is None
    print("2. Q5: 3 of 5 lower holds, 2 of 5 fails, a model with no rate leaves it open")


if __name__ == "__main__":
    test_rows()
    test_q5()
    print("test_ex2s_analyze.py: PASS")
