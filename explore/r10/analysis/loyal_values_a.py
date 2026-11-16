"""Final 8 (the paper): compute the new numbers of the final-8 text from stored files, and check them in the Markdown.

This file is a copy of the project script (an internal file) with the paths of
the study folder; it reads files that are not in the supplementary package (README.md, section 10).
Usage (from explore/):
  python3 -I r10/analysis/loyal_values_a.py compute     (writes out/loyal_values_a.json and .md)
  python3 -I r10/analysis/loyal_values_a.py check <the paper>
No model call and no network call. Reads only these stored files:
- an internal file (the author's chapter-2 check; never labels_local.jsonl or key2.json)
- prototypes/explore/r10/analysis/out/trade_prospective.json (the verifier run of DeepSeek, Qwen and Gemma)
- prototypes/explore/main/track_i/schema_snapshot.json (the schemas of the registered test on constructed texts)
- prototypes/explore/r10/analysis/out/steer_search.md (first service run: Haiku's exclusion under G1)
- prototypes/explore/r10/analysis/out/r2_posthoc.md (hotel-only score of the registered Test 1)
- prototypes/explore/r10/analysis/out/a.md (second step: no-mention shares; asks)
All values are post hoc descriptions; none is a new test.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
EXPLORE = HERE.parents[1]
ROOT = EXPLORE.parents[1]  # the project folder: the files under workshops/ are not in the supplementary package
CH2 = ROOT / "an internal file"
TP = EXPLORE / "r10/analysis/out/trade_prospective.json"
SCHEMA = EXPLORE / "main/track_i/schema_snapshot.json"
STEER = EXPLORE / "r10/analysis/out/steer_search.md"
R2 = EXPLORE / "r10/analysis/out/r2_posthoc.md"
OUT = HERE / "out"


def ch2():
    t = CH2.read_text(encoding="utf-8")
    n = re.search(r"labelled (\d+) of (\d+) agent replies", t)
    rule = re.search(r"Word rule of the flag test \(tell or not\) against the person: the person agrees on (\d+) of "
                     r"(\d+) items \((\d+)%\); Cohen's kappa (-?\d+\.\d+)", t)
    groups = {g: int(re.search(rf"{re.escape(g)}: the person agrees on \d+ of (\d+) items", t).group(1))
              for g in ("The same, Claude, audited only", "The same, Sol/Astra only", "The same, hotel brief only")}
    table = re.search(r"\| tell \| (\d+) \| (\d+) \| (\d+) \|\n\| no tell \| (\d+) \| (\d+) \| (\d+) \|\n"
                      r"\| total \| (\d+) \| (\d+) \| (\d+) \|", t)
    tt, tn, _, nt, nn, _, person_tell, person_none, total = map(int, table.groups())
    # Disagreements of the word rule with the person (rows of the disagreement table).
    rows = re.findall(r"^\| (c\d+) \| [^|]+ \| \w+ \| [^|]+ \| [^|]+ \| (tell|no tell) \| [^|]+ \| ([^|]+) \|$", t, re.M)
    rule_dis = [(i, r, p.strip()) for i, r, p in rows if (r == "tell") != (p.strip() != "none")]
    missed_limit = [x for x in rule_dis if x[1] == "no tell" and "limit" in x[2]]
    return {
        "labelled": int(n.group(1)), "items": int(n.group(2)),
        "rule_agrees": int(rule.group(1)), "rule_n": int(rule.group(2)), "rule_pct": int(rule.group(3)),
        "rule_kappa": float(rule.group(4)),
        "group_sizes": {"Claude replies from the flag runs (audited)": groups["The same, Claude, audited only"],
                        "Sol and Astra replies": groups["The same, Sol/Astra only"],
                        "Claude replies on hotel briefs": groups["The same, hotel brief only"]},
        "person_tell": person_tell, "person_none": person_none, "total": total,
        "rule_tell_person_tell": tt, "rule_tell_person_none": tn, "rule_none_person_tell": nt,
        "rule_none_person_none": nn,
        "rule_disagreements": len(rule_dis), "rule_missed_hotels_only_statements": len(missed_limit),
        "missed_items": [x[0] for x in missed_limit],
    }


def verifier_run():
    d = json.loads(TP.read_text())
    size = d["sizes"]
    per_model = 2 * (size["no_type"] + size["hotel"])  # two answers per dialogue and form
    cut = {}
    for m in ("deepseek", "qwen", "gemma"):
        h = d["models"][m]["descriptions"]["hotel_only_share"]
        valid = h["f0 | no_type"]["n"] + h["f0 | hotel"]["n"]
        cut[m] = per_model - valid
    return {"sizes": size, "original_form_answers_per_model": per_model, "original_form_answers_cut": cut}


def schema():
    s = json.loads(SCHEMA.read_text())
    fam = s["families"]
    out = {}
    for f, v in fam.items():
        out[f] = {k: v["variants"][k]["attribute_block"] for k in ("a_legacy", "b_renamed", "e_value_renamed")}
    size = [a for a in fam["large"]["variants"]["a_legacy"]["attributes"] if a["name"] == "size"][0]
    return {"blocks": out, "size_values": [x[0] for x in size["values"]], "size_glosses": size["glosses"]}


def steer():
    t = STEER.read_text(encoding="utf-8")
    hotel = re.search(r"\| haiku \| open \(448\) \| hotel-only failure \|[^\n]*\| ([+\-][\d.]+) \[[^\]]+\] \|$", t, re.M)
    anyf = re.search(r"\| haiku \| open \(448\) \| any failure \|[^\n]*\| ([+\-][\d.]+) \[[^\]]+\] \|$", t, re.M)
    return {"haiku_G1_hotel_only_change": float(hotel.group(1)), "haiku_G1_any_change": float(anyf.group(1))}


def test1_hotel_only():
    t = R2.read_text(encoding="utf-8")
    row = re.search(r"^\| wrong_values \| natural \(213\) \| ([\-−][\d.]+) \| \[([^\]]+)\] \| ([\-−][\d.]+) \| \[([^\]]+)\] \|$",
                    t, re.M)
    return {"registered": row.group(1), "registered_ci": row.group(2), "hotel_only": row.group(3),
            "hotel_only_ci": row.group(4), "row": row.group(0)}


def compute():
    res = {"post_hoc": True, "chapter2": ch2(), "verifier_run": verifier_run(), "schema": schema(),
           "steer_first_run": steer(), "test1_hotel_only": test1_hotel_only()}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "loyal_values_a.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    c, v, st, t1 = res["chapter2"], res["verifier_run"], res["steer_first_run"], res["test1_hotel_only"]
    md = [
        "## the paper, final 8: new numbers (post hoc descriptions; no model call)", "",
        f"- Chapter 2 (author's blind check): {c['labelled']} of {c['items']} replies labelled; groups "
        f"{c['group_sizes']}; the author judged {c['person_tell']} of {c['total']} as telling the traveller something; "
        f"the word rule agreed on {c['rule_agrees']} of {c['rule_n']} ({c['rule_pct']}%), kappa {c['rule_kappa']}; "
        f"{c['rule_disagreements']} disagreements, of which {c['rule_missed_hotels_only_statements']} are rule 'no tell' "
        f"where the author saw a hotels-only statement ({', '.join(c['missed_items'])}).",
        f"- Verifier run of the open-weight models: {v['original_form_answers_per_model']} original-form answers per model "
        f"(2 x ({v['sizes']['no_type']} + {v['sizes']['hotel']})); cut at the output limit: {v['original_form_answers_cut']}.",
        f"- Constructed texts: size values {res['schema']['size_values']}, glosses {res['schema']['size_glosses']}.",
        f"- First service run, Haiku, rewrite G1, 448 no-type requests: exclusion change {st['haiku_G1_any_change']:+.1f} "
        f"(either type), of which hotel-only {st['haiku_G1_hotel_only_change']:+.1f}.",
        f"- Test 1, hotel-only score: {t1['hotel_only']} [{t1['hotel_only_ci']}] (registered score {t1['registered']} "
        f"[{t1['registered_ci']}]).",
    ]
    (OUT / "loyal_values_a.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


def check(md_path):
    res = json.loads((OUT / "loyal_values_a.json").read_text())
    flat = re.sub(r"\s+", " ", open(md_path, encoding="utf-8").read())
    fails = 0

    def ok(name, cond):
        nonlocal fails
        print(("ok   " if cond else "FAIL ") + name)
        fails += 0 if cond else 1

    def has(*ps):
        return all(p in flat for p in ps)

    c = res["chapter2"]
    ok("chapter 2: 30 replies, 22 of 30 (73%), kappa -0.06, 29 of 30, 7 of the 8",
       (c["labelled"], c["rule_agrees"], c["rule_pct"], c["rule_kappa"], c["person_tell"],
        c["rule_disagreements"], c["rule_missed_hotels_only_statements"]) == (30, 22, 73, -0.06, 29, 8, 7)
       and has("the author labelled 30 replies", "agreed with the author on 22 of the 30 replies (73%; Cohen's kappa, a measure of agreement that adjusts for chance, was −0.06)",
               "29 of the 30 replies told the traveller something", "In 7 of the 8 disagreements",
               "the rule missed 7 statements that the search was for hotels only", "agent replies on 30 texts"))
    g = list(c["group_sizes"].values())
    ok("chapter 2 groups 12, 8, 10", g == [12, 8, 10]
       and has("Twelve were Claude replies", "8 were Sol and Astra replies", "10 were Claude replies on hotel briefs"))
    v = res["verifier_run"]
    ok("verifier run: 2,080 per model; Qwen 118, Gemma 13 cut",
       v["original_form_answers_per_model"] == 2080 and v["original_form_answers_cut"] == {"deepseek": 0, "qwen": 118,
                                                                                            "gemma": 13}
       and has("Qwen 118 and Gemma 13 of 2,080 each"))
    sch = res["schema"]
    blocks = sch["blocks"]
    ok("schema: size small/large, 50 employees",
       sch["size_values"] == ["small", "large"] and sch["size_glosses"] == ["fewer than 50 employees",
                                                                            "50 employees or more"]
       and has("add `size` (`small` or `large`)", "define them as fewer than 50 employees or 50 or more employees"))
    ren = all(x in blocks["retail"]["b_renamed"] for x in ("work_mode", "office_region", "industry")) and \
        "headcount" in blocks["large"]["b_renamed"]
    val = ("on_premises" in blocks["onsite"]["e_value_renamed"] and "upper_district" in blocks["north"]["e_value_renamed"]
           and "consumer_sales" in blocks["retail"]["e_value_renamed"] and "enterprise" in blocks["large"]["e_value_renamed"])
    ok("schema: renamed names and value labels", ren and val and has(
        "`site` to `office_region`, `sector` to `industry` and `size` to `headcount`",
        "`on_site` to `on_premises`, `north` to `upper_district`, `retail` to `consumer_sales` and `large` to `enterprise`"))
    ok("schema: on-site overlaps the field site; the renamed schema has on_site",
       "site (" in blocks["onsite"]["a_legacy"] and "on_site" in blocks["onsite"]["b_renamed"]
       and has("part of the field name `site` (the renamed schema has the value `on_site`)"))
    st = res["steer_first_run"]
    ok("G1: 12.9 of 18.5 points", (st["haiku_G1_hotel_only_change"], st["haiku_G1_any_change"]) == (12.9, 18.5)
       and has("12.9 of the 18.5 points that G1 added to Haiku's exclusion came from hotel-only searches"))
    t1 = res["test1_hotel_only"]
    ok("Test 1 hotel-only −11.6 [−14.5, −8.9]",
       t1["hotel_only"].replace("−", "-") == "-11.6" and has("−11.6 points [−14.5, −8.9] in Test 1"))
    # Reused values in new places: they must equal the stored table values in the same Markdown.
    ok("disclosure range 36.5% (Sonnet) to 91.8% (Luna) equals Table D1",
       has("| Sonnet | 22.2% | 10.7% | 96 | 13.5% | 50.0% | 36.5% |", "| Luna | 18.8% | 9.5% | 85 | 8.2% | 0.0% | 91.8% |",
           "36.5% (Sonnet) to 91.8% (Luna) of the trials with a second step",
           "36.5% (Sonnet) to 91.8% (Luna) of trials with a second step"))
    ok("asks 2.5% to 6.4% equals Table B5 column 'Agent asks'",
       has("| 4.5% | 10.7%", "| 6.4% | 3.1%", "| 2.5% | 11.9%", "agents asked the traveller in only 2.5% to 6.4% of their "
                                                              "answers to all 554 first requests"))
    ok("Table 2 row 6: Sonnet +3.8 and +8.7 equal Table F2 'either'",
       has("| no type (448) | either | 10.3% | 14.1% | +3.8 [+2.0, +5.6] | 19.0% | +8.7 [+6.0, +11.4] |",
           "Sonnet's +3.8 with H1 and +8.7 with G1"))
    ok("18 per 100 equals the ratio 0.18 against the words",
       has("0.18 [0.14, 0.23] against the words", "the rename lost about 18 correct filters for every 100 extra filters"))
    ok("Haiku baseline 2.5% (Table F3) and 3.1% (Table B5)",
       has("| Original tool | 6.5% | | 1.1% | | 2.5% | |", "| Haiku | 6.4% | 8.3% | 2.2% | 6.4% | 3.1% [1.7, 4.8] |",
           "Haiku's original-tool exclusion is 2.5% in Figure 2 and Table F3, but 3.1% in Table B5"))
    print(f"{fails} failures")
    return fails


if __name__ == "__main__":
    if sys.argv[1] == "compute":
        compute()
    else:
        sys.exit(1 if check(sys.argv[2]) else 0)
