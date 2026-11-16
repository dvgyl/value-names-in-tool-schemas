"""Final 8, part 2 (the paper): compute the new numbers of the part-2 text from stored files, and check them in the
Markdown.

This file is a copy of the project script (an internal file) with the paths of
the study folder; it reads files that are not in the supplementary package (README.md, section 10).
Usage (from explore/):
  python3 -I r10/analysis/loyal_values_b.py compute     (writes out/loyal_values_b.json and .md)
  python3 -I r10/analysis/loyal_values_b.py check <the paper>
No model call and no network call. Reads only these stored files:
- an internal file, section "Chapter 3" (never labels_local.jsonl or key2.json)
- workshops/release-test/out/result3.md and workshops/release-test/VERIFIED-RELEASE3.md (R10-24)
- workshops/combined-plan/REFS-VERIFIED.md (entries 42, 45, 46, 49 and 51)
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
EXPLORE = HERE.parents[1]
ROOT = EXPLORE.parents[1]  # the project folder: the files under workshops/ are not in the supplementary package
REP = ROOT / "an internal file"
RES3 = ROOT / "workshops/release-test/out/result3.md"
VER3 = ROOT / "workshops/release-test/VERIFIED-RELEASE3.md"
REFS = ROOT / "workshops/combined-plan/REFS-VERIFIED.md"
OUT = HERE / "out"


def chapter3():
    t = REP.read_text(encoding="utf-8")
    t = t[t.index("## Chapter 3"):]

    def agree(label):
        m = re.search(re.escape(label) + r"[^:]*: the person agrees on (\d+) of (\d+) items \((\d+)%\); Cohen's kappa "
                      r"(-?\d+\.\d+)", t)
        return [int(m.group(1)), int(m.group(2)), int(m.group(3)), float(m.group(4))]

    rows = re.findall(r"^\| r\d \| (\w\d) \| (\w+) / (\w+) \| (\w+) / (\w+) \| (\w+) / (\w+) \|$", t, re.M)
    interest_person_yes_model_no = [r[0] for r in rows if r[1] == "no" and r[2] == "yes"]
    interest_person_no_model_yes = [r[0] for r in rows if r[1] == "yes" and r[2] == "no"]
    interest_unsure = [r[0] for r in rows if r[2] == "unsure"]
    claim_disagree = [r[0] for r in rows if r[3] != r[4]]
    f6 = re.search(r"Of the (\d+) sampled texts, the person agrees for (\d+) \((\d+)%\); another reason (\d+)", t)
    ctrl = re.search(r"the person says \"another reason\" for (\d+) of (\d+)", t)
    return {
        "interest": agree("States the company's interest"),
        "interest_not_sure": int(re.search(r"The person answered \"Not sure\" for (\d+)", t).group(1)),
        "claim": agree("Claims a fact about venues that the data cannot show"),
        "steer": agree("The type to search first when the traveller names none"),
        "rewrites": len(rows),
        "interest_person_yes_model_no": sorted(interest_person_yes_model_no),
        "interest_person_no_model_yes": interest_person_no_model_yes,
        "interest_unsure": interest_unsure,
        "claim_disagree": claim_disagree,
        "f6": {"sampled": int(f6.group(1)), "agree": int(f6.group(2)), "pct": int(f6.group(3)),
               "other": int(f6.group(4))},
        "controls": {"other": int(ctrl.group(1)), "n": int(ctrl.group(2))},
    }


def r1024():
    t = RES3.read_text(encoding="utf-8")
    spec = {m: re.search(rf"^\| {m} \| \(\w\) \| specific \| 59 \| ([+\-][\d.]+) \| \[([^\]]+)\] \|", t, re.M)
            for m in ("deepseek", "luna")}
    model = {m: re.search(rf"^\| {m} \| \(\w\) \| \*\*model\*\* \|[ |]*\*\*(\w+)\*\* \| \*\*(\w+)\*\* \|", t, re.M)
             for m in ("deepseek", "luna")}
    levels = re.search(r"Levels: DeepSeek ([\d.]+)%, Luna ([\d.]+)%", t)
    v = VER3.read_text(encoding="utf-8")
    tpar2 = re.search(r"Luna tpar2: \*\*([+\-][\d.]+) points \[([^\]]+)\]\*\*", v)
    p0 = re.search(r"DeepSeek p0: ([+\-][\d.]+) \[([^\]]+)\]", v)
    pooled = re.search(r"\| DeepSeek \(b\) \| specific \| 59 \| ([+\-][\d.]+) \| \[([^\]]+)\] at 99.17% \|", v)
    guest = re.search(r"−14.9 points \[−29.8, −4.3\] at 98.75%", v)
    pilots = re.search(r"Pilots \(not part of the analysis\): `erk3_deepseek` ([\d.]+) USD; `erk3_luna` ([\d.]+) USD",
                       v).groups()
    cost_d = re.search(r"\| `erk3_deepseek` \| [\d,]+ \| [\d,]+ \| [^|]+ \| ([\d.]+) USD \|", v)
    cost_l = re.search(r"\| `erk3_luna` \| [\d,]+ \| [\d,]+ \| [^|]+ \| ([\d.]+) USD \|", v)
    reqs = re.findall(r"\| `erk3_(?:deepseek|luna)` \| [^|]+ \| ([\d,]+) \|", v)
    cuts = re.findall(r"\| `erk3_deepseek` \| p\w+ \([^)]*\) \| [\d,]+ \| (\d+) cut \|", v)
    verdict = re.search(r"\| DeepSeek \(b\) \| flag / flag \|[^\n]*\| \*\*wrong flag\*\* \| \*\*wrong flag\*\* \|", v)
    verdict_l = re.search(r"\| Luna \(e\) \| flag / hold \|[^\n]*\| \*\*wrong flag\*\* \| no flag to judge", v)
    return {
        "levels": [levels.group(1), levels.group(2)],
        "specific": {m: [spec[m].group(1), spec[m].group(2)] for m in spec},
        "model_decisions": {m: [model[m].group(1), model[m].group(2)] for m in model},
        "luna_paraphrase_between_batches": [tpar2.group(1), tpar2.group(2)],
        "deepseek_control_between_runs": [p0.group(1), p0.group(2)],
        "deepseek_pooled_specific": [pooled.group(1), pooled.group(2)],
        "luna_guesthouse_replication_found": bool(guest),
        "pilot_usd": [float(x) for x in pilots],
        "cost_usd": {"deepseek": float(cost_d.group(1)), "luna": float(cost_l.group(1))},
        "requests_per_run": reqs[:2],
        "deepseek_cut": sum(int(x) for x in cuts),
        "verdicts": {"deepseek": "wrong flag / wrong flag" if verdict else None,
                     "luna": "wrong flag / no flag to judge" if verdict_l else None},
    }


def refs():
    t = REFS.read_text(encoding="utf-8")
    out = {}
    for n in (42, 45, 46, 49, 51):
        block = t[t.index(f"### {n}. "):]
        block = block[:block.index("\n### ", 5)] if "\n### " in block[5:] else block
        entry = re.search(r"\*\*Entry(?: \(safe form\))?:\*\* (.+)", block)
        out[n] = {"entry": entry.group(1) if entry else None,
                  "safe_claim": re.search(r"\*\*Safe claim:\*\* (.+)", block).group(1)}
    return out


CH2 = ROOT / "an internal file"
SCHEMA = EXPLORE / "main/track_i/schema_snapshot.json"
AMD = EXPLORE / "r10/analysis/out/a.md"


def step_c():
    """Values behind the fixes of VERIFIED-LOYAL8.md (sections 0, 2, 4, 8, 10)."""
    t = CH2.read_text(encoding="utf-8")
    rows = re.findall(r"^\| (c\d+) \| ([^|]+) \| \w+ \| [^|]+ \| ([^|]+) \| (tell|no tell) \| [^|]+ \| ([^|]+) \|$",
                      t, re.M)
    missed = [(i, g.strip(), k.strip()) for i, g, k, r, p in rows if r == "no tell" and "limit" in p]
    widen = [i for i, g, k in missed if k == "widen_silent"]
    widen_groups = sorted({g for i, g, k in missed if k == "widen_silent"})
    sample_models = re.search(r"\(both arms; ([^;]+);", t).group(1)
    s = json.loads(SCHEMA.read_text())
    legacy = [a for a in s["families"]["large"]["variants"]["a_legacy"]["attributes"] if a["name"] == "size"][0]
    described = [a for a in s["families"]["large"]["variants"]["c_described"]["attributes"] if a["name"] == "size"][0]
    return {"chapter2_missed": [m[0] for m in missed], "missed_widen_silent": widen, "widen_groups": widen_groups,
            "chapter2_models": sample_models, "size_described_original": legacy["described"],
            "size_described_c": described["described"]}


def compute():
    res = {"post_hoc": True, "chapter3": chapter3(), "r10_24": r1024(), "refs": refs(), "step_c": step_c()}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "loyal_values_b.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    c, r = res["chapter3"], res["r10_24"]
    md = ["## the paper, final 8 part 2: new numbers (no model call)", "",
          f"- Chapter 3, rewrites ({c['rewrites']}): interest {c['interest']} (not sure {c['interest_not_sure']}; "
          f"author yes and model no: {c['interest_person_yes_model_no']}; author no and model yes: "
          f"{c['interest_person_no_model_yes']}; unsure: {c['interest_unsure']}); claim {c['claim']} (disagreement "
          f"{c['claim_disagree']}); steer {c['steer']}.",
          f"- Chapter 3, F.6 texts: {c['f6']}; controls {c['controls']}.",
          f"- R10-24: levels {r['levels']}; specific set {r['specific']}; decisions {r['model_decisions']}; verdicts "
          f"{r['verdicts']}; Luna paraphrase arm between batches {r['luna_paraphrase_between_batches']}; costs "
          f"{r['cost_usd']} (rounded 0.23 and 0.10); requests per run {r['requests_per_run']}; DeepSeek cut "
          f"{r['deepseek_cut']}."]
    (OUT / "loyal_values_b.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


def check(md_path):
    res = json.loads((OUT / "loyal_values_b.json").read_text())
    text = open(md_path, encoding="utf-8").read()
    flat = re.sub(r"\s+", " ", text)
    fails = 0

    def ok(name, cond):
        nonlocal fails
        print(("ok   " if cond else "FAIL ") + name)
        fails += 0 if cond else 1

    def has(*ps):
        return all(p in flat for p in ps)

    c, r = res["chapter3"], res["r10_24"]
    ok("chapter 3 values: interest 3 of 8, kappa -0.11, 1 not sure; claim 8 of 9, kappa 0.73; steer 9 of 9",
       c["interest"][:2] == [3, 8] and c["interest"][3] == -0.11 and c["interest_not_sure"] == 1
       and c["claim"][:2] == [8, 9] and c["claim"][3] == 0.73 and c["steer"][:2] == [9, 9] and c["rewrites"] == 9)
    ok("chapter 3 disagreements: G1, H1, H2, N2 (author yes); H3 (author no); N3 unsure; claim N3",
       c["interest_person_yes_model_no"] == ["G1", "H1", "H2", "N2"] and c["interest_person_no_model_yes"] == ["H3"]
       and c["interest_unsure"] == ["N3"] and c["claim_disagree"] == ["N3"])
    ok("chapter 3 text", has("for 8 of 9 rewrites", "for only 3 of 8", "(Cohen's kappa 0.73)", "−0.11",
                             "G1, H1, H2 and N2", "H3", "N3"))
    ok("F.6: 10 of 12, another reason 2; controls 3 of 3",
       c["f6"] == {"sampled": 12, "agree": 10, "pct": 83, "other": 2} and c["controls"] == {"other": 3, "n": 3}
       and has("12 of the 25 texts and 3 control texts", "10 of the 12", "another reason in 2", "all 3"))
    ok("R10-24 specific set and levels",
       r["specific"] == {"deepseek": ["+1.1", "-1.9, +4.1"], "luna": ["+0.5", "-2.9, +3.9"]}
       and r["levels"] == ["99.17", "98.75"]
       and has("+1.1 points [−1.9, +4.1] (99.17% interval)", "+0.5 points [−2.9, +3.9] (98.75%)"))
    ok("R10-24 decisions pass / pass and verdicts",
       r["model_decisions"] == {"deepseek": ["pass", "pass"], "luna": ["pass", "pass"]}
       and r["verdicts"] == {"deepseek": "wrong flag / wrong flag", "luna": "wrong flag / no flag to judge"}
       and has("Both models passed under both rules", "DeepSeek's flag was a wrong flag under both rules and Luna's "
                                                      "under the first rule", "no flag to judge"))
    ok("R10-24 between-batch change +5.1 [+2.2, +8.3]",
       r["luna_paraphrase_between_batches"] == ["+5.1", "+2.2, +8.3"] and has("+5.1 points [+2.2, +8.3]"))
    ok("R10-24 costs 0.2260 and 0.0956 USD, rounded 0.23 and 0.10; pilots under 0.01 USD",
       round(r["cost_usd"]["deepseek"], 2) == 0.23 and round(r["cost_usd"]["luna"], 2) == 0.10
       and sum(r["pilot_usd"]) < 0.01 and len(r["pilot_usd"]) == 2
       and has("Repeating the two flagged comparisons cost 0.23 and 0.10 USD"))
    ok("R10-24 limits: pooled +3.5 [+0.6, +6.6]; DeepSeek control +2.2 [+0.5, +4.2]; Luna guesthouse −14.9",
       r["deepseek_pooled_specific"] == ["+3.5", "+0.6, +6.6"] and r["deepseek_control_between_runs"] == ["+2.2",
                                                                                                         "+0.5, +4.2"]
       and r["luna_guesthouse_replication_found"]
       and has("+3.5 points [+0.6, +6.6] (99.17%)", "+2.2 [+0.5, +4.2] between the two runs",
               "−14.9 points [−29.8, −4.3] in the replication (98.75%; a description)"))
    ok("Table B6 row: 2,170 requests per run, DeepSeek 3 cut",
       r["requests_per_run"] == ["2,170", "2,170"] and r["deepseek_cut"] == 3
       and has("DeepSeek: 3 of 2,170 answers cut; Luna: 0"))
    refs_ = res["refs"]
    ok("references equal REFS-VERIFIED entries 42, 45, 46, 49",
       all(refs_[str(n)]["entry"].split(" DOI ")[0] in text for n in (42, 45, 46, 49)))
    ok("Feng et al. wording: errors of their own tracker (entry 51)",
       has("For the tracker of Feng et al. (2023), most errors in this corpus are in the hotel `type` field",
           "the tracker of Feng et al. (2023) confuses \"not mentioned\" and \"hotel\" in most hotel-type errors")
       and "Feng" in refs_["51"]["safe_claim"])
    sc = res["step_c"]
    ok("chapter 2: 3 of the 7 misses are new searches without the filter (hotel briefs); 4 of 7 bear on no mention; "
       "Luna not in the sample",
       len(sc["chapter2_missed"]) == 7 and sc["missed_widen_silent"] == ["c08", "c17", "c28"]
       and sc["widen_groups"] == ["hotel brief"] and "Luna" not in sc["chapter2_models"]
       and has("In 3 of the 7 misses, all on hotel briefs", "The other 4 of the 7 misses",
               "Luna, which gives the highest share, is not in the sample"))
    ok("Table D2 no longer cited for shares; page description",
       "shares with no mention in Tables D1 and D2" not in flat
       and has("The page showed the chat, the empty search, the reply and any new search"))
    ok("asks 2.5% to 6.4% over all 554 first requests with the ask tool (Table D1 column 'Asks (554 first requests)')",
       has("| Opus | 25.9% | 11.9% | 51 | 2.0% | 51.0% | 47.1% | 2.5% |", "| Haiku | 7.2% | 3.1% | 28 | 17.9% | 39.3% | "
           "42.9% | 6.4% |", "When the ask tool was offered, agents asked the traveller in only 2.5% to 6.4% of their "
                             "answers to all 554 first requests"))
    ok("abstract: Test 1 quantity named", has("lowered hotel filters in answers to the full dialogue by 13.0 percentage "
                                               "points when the task sets no type"))
    ok("Section 5 and Table 2 wording", has("the first rule flagged 2 of 7 paraphrase decisions", "an unchanged tool or form (five models)",
                                            "Sonnet's +3.8 with H1 and +8.7 with G1"))
    ok("original form does not define small and large",
       sc["size_described_original"] is False and sc["size_described_c"] is True
       and has("The original form does not define these values"))
    ok("headline places name the agent and one search",
       has("Haiku and, to a lesser extent, Sonnet follow steering instructions in the service's tool text with one "
           "search", "on one model, Haiku, with one search per request",
           "With one search per request and no type in the brief (448 requests)", "Under G, with one search, Haiku's",
           "The runs allowed one search per answer, so the agents could not make the second search"))
    print(f"{fails} failures")
    return fails


if __name__ == "__main__":
    if sys.argv[1] == "compute":
        compute()
    else:
        sys.exit(1 if check(sys.argv[2]) else 0)
