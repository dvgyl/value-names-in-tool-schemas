"""Word search of the nine service rewrites (the paper, round 11; post hoc). No model call; no held-out answer.

The paper says that no rewrite names the commission. Before this script, that statement rested on a model reading
(steer/reading.json and steer2/reading.json, by Opus 5.5). This script checks it with a fixed word search: it reads the
stored definition of each accepted rewrite (the "tool" object of the answer, as JSON text) and counts, case-insensitive,
the words of an interest (commission, revenue, earn/earns/earned/earning, profit, margin, incentive, sponsor) and two
words of preference (featured, recommended).
Rewrites: H1 and G1 (steer/edit_h.json, edit_g.json), N1 (release/edit.json), H2, H3, G2, G3, N2, N3
(steer2/edit_*.json).
Outputs: r10/analysis/out/steer_words.md and .json. Usage (from explore/):
.venv/bin/python -I r10/analysis/steer_words.py
"""
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
OUT = HERE / "out"
FILES = {"h1": R10 / "steer" / "edit_h.json", "g1": R10 / "steer" / "edit_g.json", "n1": R10 / "release" / "edit.json",
         **{k: R10 / "steer2" / f"edit_{k}.json" for k in ("h2", "h3", "g2", "g3", "n2", "n3")}}
INTEREST = re.compile(r"\b(commissions?|revenues?|earn(s|ed|ing)?|profits?|margins?|incentives?|sponsor\w*)\b", re.I)
PREFERENCE = re.compile(r"\b(featured|recommended)\b", re.I)


def tool_text(path):
    obj = json.loads(path.read_text())
    tool = obj.get("tool", obj) if isinstance(obj, dict) else obj
    return json.dumps(tool, ensure_ascii=False)


def main():
    res = {"post_hoc": True, "rewrites": {}}
    for k, path in FILES.items():
        text = tool_text(path)
        res["rewrites"][k] = {"file": str(path.relative_to(R10)), "chars": len(text),
                              "interest_words": sorted(m.group(0).lower() for m in INTEREST.finditer(text)),
                              "preference_words": sorted(m.group(0).lower() for m in PREFERENCE.finditer(text))}
    res["rewrites_with_an_interest_word"] = sorted(k for k, v in res["rewrites"].items() if v["interest_words"])
    L = ["## Word search of the nine service rewrites (post hoc)", "",
         "Interest words: commission, revenue, earn, profit, margin, incentive, sponsor. Preference words: featured, "
         "recommended. Case-insensitive, whole words, on the stored tool definition (JSON text).", "",
         "| Rewrite | File | Characters | Interest words | Preference words |", "|---|---|---|---|---|"]
    for k, v in res["rewrites"].items():
        L.append(f"| {k} | {v['file']} | {v['chars']} | {', '.join(v['interest_words']) or 'none'} | "
                 f"{', '.join(v['preference_words']) or 'none'} |")
    L += ["", f"Rewrites with an interest word: {', '.join(res['rewrites_with_an_interest_word']) or 'none'}"]
    OUT.mkdir(exist_ok=True)
    (OUT / "steer_words.json").write_text(json.dumps(res, indent=1))
    (OUT / "steer_words.md").write_text("\n".join(L) + "\n")
    print((OUT / "steer_words.md").read_text())


if __name__ == "__main__":
    main()
