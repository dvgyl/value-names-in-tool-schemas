"""Values for the fixes after the independent review (2026-11-16): the held-out Table D6 columns from the stored
summary counts, and the denominators that the review asked for. Reads only out/n1_heldout_stored.json and
out/n2_gated_soft.json; writes out/review_values.json and prints the Markdown rows.
Usage (from explore/): python3 -I posthoc/checks/repair-display/make_review_values.py
"""
import json
import pathlib

OUT = pathlib.Path(__file__).resolve().parent / "out"
NAME = {"sonnet": "Sonnet", "haiku": "Haiku", "sol": "Sol", "luna": "Luna", "deepseek": "DeepSeek", "qwen": "Qwen",
        "gemma": "Gemma"}


def g(x):
    return f"{x:.0f}" if abs(x - round(x)) < 1e-9 else f"{x:.1f}"


def main():
    n1 = json.loads((OUT / "n1_heldout_stored.json").read_text())["models"]
    n2 = json.loads((OUT / "n2_gated_soft.json").read_text())["models"]
    rows = {}
    for m, r in n1.items():
        P = r["policies"]
        assert P["relax_any"]["gross_losses_H"] == P["soft"]["gross_losses_H"] == 0
        assert P["relax_any"]["gross_gains_H"] == P["soft"]["gross_gains_H"] == P["planned"]["gross_gains_H"] == 0
        rows[m] = {
            "original_failures": g(r["original_failures_NT"]),
            "avoided": " / ".join(g(P[p]["net_avoided_NT"]) for p in ("planned", "relax_any", "soft")),
            "verifier_losses_added_ended": f"{g(P['planned']['gross_losses_H'])} / {g(P['planned']['gross_gains_H'])}",
            "verifier_calls": str(r["verifier_calls"]),
            "second_searches": f"{P['relax_any']['second_searches']} / {P['soft']['second_searches']}",
            "answers": r["answers"], "dialogues": r["dialogues"]}
    out = {"d6_new_columns": rows,
           "heldout_qwen_G_dialogues": n1["qwen"]["dialogues"]["G"],
           "heldout_H_dialogues": {NAME[m]: n1[m]["dialogues"]["H"] for m in n1},
           "dev_qwen_hotel_dialogues": n2["qwen"]["dialogues"]["h"],
           "dev_hotel_dialogues": {m: n2[m]["dialogues"]["h"] for m in n2},
           "dev_gated_gross_gains": {m: n2[m]["policies"]["G"]["gross_gains"] for m in n2},
           "dev_gated_gross_losses": {m: n2[m]["policies"]["G"]["gross_losses"] for m in n2}}
    (OUT / "review_values.json").write_text(json.dumps(out, indent=1))
    for m, r in rows.items():
        print(NAME[m], r["original_failures"], r["avoided"], r["verifier_losses_added_ended"], r["verifier_calls"],
              r["second_searches"], r["answers"], r["dialogues"])
    print({k: v for k, v in out.items() if k != "d6_new_columns"})


if __name__ == "__main__":
    main()
