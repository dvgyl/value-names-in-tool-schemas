"""SPEC-N1-heldout.md: held-out display outcomes from the stored aggregate result (no per-answer data, no em* folder).

Usage (from explore/): python3 -I posthoc/checks/repair-display/n1_heldout_stored.py
Reads r10/analysis/out/heldout_confirm.json only. Writes posthoc/checks/repair-display/out/n1_heldout_stored.json.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]  # explore/ of the repository
HERE = pathlib.Path(__file__).resolve().parent
RESULT = ROOT / "r10/analysis/out/heldout_confirm.json"
POLICIES = ("planned", "relax_any", "soft")


def extract(model_row):
    r1 = model_row["read1"]
    dsp = r1["display"]
    calls = sum(sum(v.values()) for v in r1["verifier_answers"].values())
    row = {"dialogues": dsp["dialogues"], "answers": dsp["answers"],
           "original_failures_NT": dsp["original"]["failures_NT"], "original_losses_H": dsp["original"]["losses_H"],
           "verifier_calls": calls, "policies": {}}
    for p in POLICIES:
        e = dsp[p]
        second = round((dsp["searches_per_answer"][p] - 1) * dsp["answers"])
        assert abs((dsp["searches_per_answer"][p] - 1) * dsp["answers"] - second) < 1e-6
        assert e["failures_ended_NT"] - e["failures_caused_NT"] == e["net_avoided_NT"]
        assert e["losses_caused_H"] - e["losses_ended_H"] == e["net_added_H"]
        row["policies"][p] = {"net_avoided_NT": e["net_avoided_NT"], "failures_ended_NT": e["failures_ended_NT"],
                              "failures_caused_NT": e["failures_caused_NT"], "gross_losses_H": e["losses_caused_H"],
                              "gross_gains_H": e["losses_ended_H"], "net_added_H": e["net_added_H"],
                              "second_searches": second, "model_calls": calls if p == "planned" else 0}
    for p in ("relax_any", "soft"):
        assert row["policies"][p]["gross_losses_H"] == 0, (p, row)
    row["guesthouse_newly_shown_stated_H"] = {
        "relax_any": dsp["relax_any_on_H"]["stated_dialogues_changed"], "planned": None, "soft": None,
        "why_none": "not computed: needs the per-answer held-out original answers, which exist only in em* folders"}
    row["missing"] = model_row["missing"]
    return row


def main():
    res = json.loads(RESULT.read_text())
    out = {"spec": "SPEC-N1-heldout.md", "source": str(RESULT.relative_to(ROOT)),
           "models": {m: extract(res["models"][m]) for m in res["M"]}}
    o = HERE / "out" / "n1_heldout_stored.json"
    o.parent.mkdir(exist_ok=True)
    o.write_text(json.dumps(out, indent=1))
    print("model    NT  H  orig f/l | avoided V R S | V lost/gained | R,S lost/gained | calls | 2nd search R S | gh R")
    for m, r in out["models"].items():
        P = r["policies"]
        print(f"{m:8} {r['dialogues']['NT']:3} {r['dialogues']['H']:2} {r['original_failures_NT']:4g}/"
              f"{r['original_losses_H']:<3g}| {P['planned']['net_avoided_NT']:g} {P['relax_any']['net_avoided_NT']:g} "
              f"{P['soft']['net_avoided_NT']:g} | {P['planned']['gross_losses_H']:g}/{P['planned']['gross_gains_H']:g} | "
              f"{P['relax_any']['gross_losses_H']:g}/{P['relax_any']['gross_gains_H']:g} "
              f"{P['soft']['gross_losses_H']:g}/{P['soft']['gross_gains_H']:g} | {r['verifier_calls']} of {r['answers']} | "
              f"{P['relax_any']['second_searches']} {P['soft']['second_searches']} | "
              f"{r['guesthouse_newly_shown_stated_H']['relax_any']} | missing {r['missing']}")


if __name__ == "__main__":
    main()
