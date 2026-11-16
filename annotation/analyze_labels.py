"""Compare the author's labels from the game "Guesthouse or Not" (version 3) with the hidden key (key2.json).

The script reads the labels and the private key. It reports, in plain words, how often the person agrees with:
- chapter 1: the word rule (clear rule and strict rule), the corpus annotation (label group) and the brief;
- chapter 2: the word rule of the returned-flag test and the AI reading of the flag audit (Opus 5.5);
- chapter 3: the model readings of the 9 service rewrites and of the Appendix F.6 texts (Opus 5.5).
For each comparison it gives the counts, the agreement, Cohen's kappa (with a 95% bootstrap interval over items when
there are 20 items or more) and the list of disagreements.

The labels were in labels_local.jsonl, one line for each answer in the order of the answers. A line with "op"
"delete" removes the earlier answer with the same id. The key (the word rule, the label, the brief and the readings
of each item) was in key2.json; the labeller did not see it. The labels and the key are private, so they are not in
this repository (README, section 8). The items, as the labeller saw them, are in game_items.json.
Usage (from the repository folder; needs labels_local.jsonl and key2.json):
   python3 -I annotation/analyze_labels.py --local --out annotation/labels_report.md
The analysis and its self-test (--selftest) need the key, so they cannot run from this repository.
"""
import argparse
import collections
import json
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
KEY = HERE / "key2.json"
LOCAL = HERE / "labels_local.jsonl"
SEED = 20261113
WANT = {"hotel_only": "Only a hotel", "guesthouse_ok": "A guesthouse is fine too", "unclear": "Not clear from the words",
        "too_little": "Not enough text to tell"}
PICKS = {"guesthouse": "says guesthouses fit or offers them", "limit": "says the search was hotels only",
         "ask": "asks about the type"}


# ---------------------------------------------------------------------------------------------------- reading
def load_labels(path):
    """{doc id: data} of every document in the export, any of the accepted forms."""
    path = pathlib.Path(path)
    out = {}

    def add(doc_id, obj):
        if isinstance(obj, dict) and isinstance(obj.get("data"), dict) and "id" in obj:
            out[str(obj["id"])] = obj["data"]
        elif isinstance(obj, dict) and doc_id:
            out[doc_id] = obj

    if path.is_dir():
        for f in sorted(path.rglob("*.json")):
            add(f.stem, json.loads(f.read_text()))
        return out
    text = path.read_text()
    try:
        if path.suffix == ".jsonl":
            raise json.JSONDecodeError("JSON lines", text, 0)
        obj = json.loads(text)
        if isinstance(obj, list):
            for o in obj:
                add(None, o)
        elif isinstance(obj, dict) and all(isinstance(v, dict) for v in obj.values()):
            for k, v in obj.items():
                add(k, v)
        return out
    except json.JSONDecodeError:
        pass
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("{"):
            row = json.loads(line)
            if isinstance(row, dict) and row.get("op") == "delete" and "id" in row:
                out.pop(str(row["id"]), None)  # labels_local.jsonl: the operator removed (undid) the answer
            else:
                add(None, row)
    return out


# ---------------------------------------------------------------------------------------------------- statistics
def kappa(pairs):
    """Cohen's kappa of [(a, b)]; None when there are no pairs or one side uses one category only (then kappa says
    nothing)."""
    n = len(pairs)
    if not n or len({a for a, _ in pairs}) < 2 or len({b for _, b in pairs}) < 2:
        return None
    po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return None if pe >= 1 else (po - pe) / (1 - pe)


def boot_ci(pairs, draws=2000):
    if len(pairs) < 20:
        return None
    rng = random.Random(SEED)
    vals = []
    for _ in range(draws):
        k = kappa([pairs[rng.randrange(len(pairs))] for _ in pairs])
        if k is not None:
            vals.append(k)
    if len(vals) < draws * 0.9:
        return None
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]


def agreement_line(name, pairs):
    """One plain sentence: agreement count, share and kappa."""
    n = len(pairs)
    if not n:
        return f"- {name}: no items."
    same = sum(a == b for a, b in pairs)
    k, ci = kappa(pairs), boot_ci(pairs)
    ks = "kappa cannot be computed (one side uses one category only)" if k is None else f"Cohen's kappa {k:.2f}"
    if k is not None and ci:
        ks += f" [95% interval {ci[0]:.2f} to {ci[1]:.2f}]"
    return f"- {name}: the person agrees on {same} of {n} items ({100 * same / n:.0f}%); {ks}."


def table(pairs, rows_name, cols_name, rows=None, cols=None):
    """A Markdown cross table of [(row value, column value)]."""
    rows = rows or sorted({a for a, _ in pairs}, key=str)
    cols = cols or sorted({b for _, b in pairs}, key=str)
    c = collections.Counter(pairs)
    out = [f"| {rows_name} \\ {cols_name} | " + " | ".join(map(str, cols)) + " | total |",
           "|---|" + "---|" * (len(cols) + 1)]
    for r in rows:
        out.append(f"| {r} | " + " | ".join(str(c[(r, k)]) for k in cols) + f" | {sum(c[(r, k)] for k in cols)} |")
    out.append("| total | " + " | ".join(str(sum(c[(r, k)] for r in rows)) for k in cols) + f" | {len(pairs)} |")
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------------- chapters
GROUP = {"s2": "hotel only", "s3": "guesthouse accepted", "s1t": "not stated"}


def three_way(choice):
    """The person's 4 answers on 3 classes: hotel only, guesthouse accepted, type not stated."""
    return {"hotel_only": "hotel only", "guesthouse_ok": "guesthouse accepted"}.get(choice, "not stated")


def chapter1(labels, key, md):
    items = {i: k for i, k in key.items() if k["chapter"] == 1}
    got = {i: labels[i] for i in items if i in labels}
    md.append("## Chapter 1: What does the traveller want?")
    md.append("")
    md.append(f"The person labelled {len(got)} of {len(items)} items: {sum(i.startswith('a') for i in got)} first "
              f"requests (part a) and {sum(i.startswith('b') for i in got)} whole dialogues (part b). The sample takes "
              "every first request in which the clear rule finds a type sentence, and it takes more rule-clear whole "
              "dialogues than the corpus has. So the shares below describe this sample, not the corpus.")
    md.append("")
    if not got:
        return
    counts = collections.Counter(v["choice"] for v in got.values())
    md.append("The person's answers: " + "; ".join(f"{WANT[k]} {counts[k]}" for k in WANT) + ".")
    md.append("")
    for part, name in (("1a", "first requests"), ("1b", "whole dialogues"), (None, "both parts")):
        sel = [i for i in got if part is None or items[i]["part"] == part]
        if not sel:
            continue
        md.append(f"### {name.capitalize()} ({len(sel)} items)")
        md.append("")
        rule_bin = [("hotel only" if items[i]["rule"] == "hotel_only" else "other",
                     "hotel only" if got[i]["choice"] == "hotel_only" else "other") for i in sel]
        strict_bin = [("hotel only" if items[i]["rule_strict"] == "hotel_only" else "other",
                       "hotel only" if got[i]["choice"] == "hotel_only" else "other") for i in sel]
        rule3 = [({"hotel_only": "hotel only", "guesthouse_only": "guesthouse accepted"}.get(items[i]["rule"],
                  "not stated" if items[i]["rule"] == "unclear" else "mixed"), three_way(got[i]["choice"])) for i in sel]
        group = [(GROUP[items[i]["label_group"]], three_way(got[i]["choice"])) for i in sel]
        brief = [(items[i]["brief"], three_way(got[i]["choice"])) for i in sel]
        md.append(agreement_line("Clear rule against the answer \"Only a hotel\" (yes or no)", rule_bin))
        md.append(agreement_line("Strict rule (exclusion or restriction only) against \"Only a hotel\"", strict_bin))
        md.append(agreement_line("Clear rule against the answer on three classes", rule3))
        rc = [p for p in rule_bin if p[0] == "hotel only"]
        hc = [p for p in rule_bin if p[1] == "hotel only"]
        if rc:
            md.append(f"- Of the {len(rc)} items that the clear rule calls hotel only, the person says \"Only a hotel\" "
                      f"for {sum(b == 'hotel only' for _, b in rc)}.")
        if hc:
            md.append(f"- Of the {len(hc)} items where the person says \"Only a hotel\", the clear rule finds "
                      f"{sum(a == 'hotel only' for a, _ in hc)}.")
        unclear = [i for i in sel if items[i]["rule"] == "unclear"]
        if unclear:
            c = collections.Counter(got[i]["choice"] for i in unclear)
            md.append(f"- Of the {len(unclear)} items that the clear rule calls unclear, the person says: "
                      + "; ".join(f"{WANT[k]} {c[k]}" for k in WANT) + ".")
        md.append("")
        md.append("Clear rule (rows) against the person (columns):")
        md.append("")
        md.append(table(rule3, "rule", "person", cols=["hotel only", "guesthouse accepted", "not stated"]))
        md.append("")
        if part == "1a":
            md.append("All first requests come from the label group S1t (the annotation sets no type), so the annotation "
                      "is compared on whole dialogues only.")
        else:
            md.append("Corpus annotation (label group; rows) against the person (columns):")
            md.append("")
            md.append(table(group, "annotation", "person", rows=sorted({a for a, _ in group}),
                            cols=["hotel only", "guesthouse accepted", "not stated"]))
            md.append("")
            md.append(agreement_line("Corpus annotation (S2 = hotel only, S3 = guesthouse accepted, S1t = not stated) "
                                     "against the person", group))
        md.append("")
        md.append("Brief (rows) against the person (columns):")
        md.append("")
        md.append(table(brief, "brief", "person", cols=["hotel only", "guesthouse accepted", "not stated"]))
        md.append("")
    md.append("### Disagreements with the clear rule")
    md.append("")
    md.append("| item | part | dialogue | clear rule | strict rule | annotation | brief | person |")
    md.append("|---|---|---|---|---|---|---|---|")
    for i in sorted(got):
        k = items[i]
        rule = "hotel only" if k["rule"] == "hotel_only" else ("guesthouse accepted" if k["rule"] == "guesthouse_only"
                                                                else k["rule"])
        if (rule if rule != "unclear" else "not stated") != three_way(got[i]["choice"]):
            md.append(f"| {i} | {k['part']} | {k['dialogue']} | {k['rule']} | {k['rule_strict']} | {k['label_group']} | "
                      f"{k['brief']} | {WANT[got[i]['choice']]} |")
    md.append("")


def tells(v):
    return v.get("choice") == "tell" and bool(v.get("picks"))


def chapter2(labels, key, md):
    items = {i: k for i, k in key.items() if k["chapter"] == 2}
    got = {i: labels[i] for i in items if i in labels}
    md.append("## Chapter 2: Did the agent tell the traveller?")
    md.append("")
    md.append(f"The person labelled {len(got)} of {len(items)} agent replies (both arms; Claude models, Sol and Astra; "
              "hotel briefs with a constructed empty result). The page hid the model, the arm and the flag line. A reply "
              "\"tells\" when the person ticked at least one of: " + "; ".join(PICKS.values()) + ".")
    md.append("")
    if not got:
        return
    pairs = [("tell" if items[i]["rule_tell"] else "no tell", "tell" if tells(got[i]) else "no tell") for i in got]
    md.append(agreement_line("Word rule of the flag test (tell or not) against the person", pairs))
    for grp in ("Claude, audited", "Sol/Astra", "hotel brief"):
        sub = [p for i, p in zip(got, pairs) if items[i]["group"] == grp]
        if sub:
            md.append(agreement_line(f"The same, {grp} only", sub))
    hb = [i for i in got if items[i]["group"] == "hotel brief" and items[i]["rule_kind"] == "tell"]
    if hb:
        md.append(f"- Hotel briefs: the test counts any text without a search as \"tell\". Of these {len(hb)} replies, "
                  f"the person says {sum(tells(got[i]) for i in hb)} tell the traveller about guesthouses, the hotel "
                  "limit or the type.")
    au = [i for i in got if items[i]["audit"]]
    if au:
        md.append(agreement_line("AI reading of the flag audit (Opus 5.5; verdict) against the person",
                                 [(items[i]["audit"]["verdict"], "tell" if tells(got[i]) else "no tell") for i in au]))
        for code, pick in (("G", "guesthouse"), ("L", "limit"), ("Q", "ask")):
            md.append(agreement_line(f"Code {code} of the audit against \"{PICKS[pick]}\"",
                                     [(items[i]["audit"][code] == "1", pick in (got[i].get("picks") or [])) for i in au]))
    md.append("")
    md.append("Word rule (rows) against the person (columns):")
    md.append("")
    md.append(table(pairs, "word rule", "person", rows=["tell", "no tell"], cols=["tell", "no tell"]))
    md.append("")
    md.append("### Disagreements")
    md.append("")
    md.append("| item | group | model | arm | rule kind | word rule | audit | person |")
    md.append("|---|---|---|---|---|---|---|---|")
    for i in sorted(got):
        k, v = items[i], got[i]
        person = ", ".join(v.get("picks") or []) or "none"
        audit = k["audit"]["verdict"] if k["audit"] else "-"
        if (k["rule_tell"] != tells(v)) or (k["audit"] and (k["audit"]["verdict"] == "tell") != tells(v)):
            md.append(f"| {i} | {k['group']} | {k['model']} | {k['arm']} | {k['rule_kind']} | "
                      f"{'tell' if k['rule_tell'] else 'no tell'} | {audit} | {person} |")
    md.append("")


def chapter3(labels, key, md):
    rw = {i: k for i, k in key.items() if k["chapter"] == 3 and k["part"] == "3a"}
    md.append("## Chapter 3: Check the model's readings")
    md.append("")
    md.append("### The 9 service rewrites")
    md.append("")
    rows, done = [], 0
    for q, field, conv in (("interest", "model_interest", lambda x: "yes" if x else "no"),
                           ("claim", "model_claim", lambda x: "yes" if x else "no"),
                           ("steer", "model_steer", lambda x: x or "none")):
        pairs, unsure = [], 0
        for i, k in sorted(rw.items()):
            v = labels.get(f"{i}-{q}")
            if not v:
                continue
            done += 1
            if v["choice"] == "unsure":
                unsure += 1
                continue
            pairs.append((conv(k[field]), v["choice"]))
        name = {"interest": "States the company's interest", "claim": "Claims a fact about venues that the data "
                "cannot show", "steer": "The type to search first when the traveller names none"}[q]
        md.append(agreement_line(f"{name} (model reading against the person)", pairs)
                  + (f" The person answered \"Not sure\" for {unsure}." if unsure else ""))
    md.append("")
    md.append("| text | rewrite | interest: model / person | claim: model / person | steer: model / person |")
    md.append("|---|---|---|---|---|")
    for i, k in sorted(rw.items(), key=lambda x: int(x[0][1:])):
        cell = []
        for q, field in (("interest", "model_interest"), ("claim", "model_claim"), ("steer", "model_steer")):
            m = k[field] if q == "steer" else ("yes" if k[field] else "no")
            p = labels.get(f"{i}-{q}", {}).get("choice", "-")
            cell.append(f"{m or 'none'} / {p}")
        rows.append(f"| {i} | {k['rewrite']} | " + " | ".join(cell) + " |")
    md.extend(rows)
    md.append("")
    md.append("The steer type of H1 and G1 comes from the quotes in Appendix F.2; the reading of R10-14 has no steer "
              "field.")
    md.append("")
    f6 = {i: k for i, k in key.items() if k["chapter"] == 3 and k["part"] == "3b"}
    got = {i: labels[i] for i in f6 if i in labels}
    md.append("### The agent texts of Appendix F.6")
    md.append("")
    real = [i for i in got if f6[i]["kind"] == "F.6 text"]
    ctrl = [i for i in got if f6[i]["kind"] == "control"]
    if real:
        c = collections.Counter(got[i]["choice"] for i in real)
        md.append(f"- The model reading says that each F.6 text gives the traveller's word \"hotel\" as the reason. Of "
                  f"the {len(real)} sampled texts, the person agrees for {c['word']} ({100 * c['word'] / len(real):.0f}%)"
                  f"; another reason {c['other']}; no clear reason {c['unclear']}. Kappa does not apply, because the "
                  "model reading has one value only.")
    if ctrl:
        c = collections.Counter(got[i]["choice"] for i in ctrl)
        md.append(f"- Control texts (a guesthouse search with a reason from the tool, not part of F.6): the person says "
                  f"\"another reason\" for {c['other']} of {len(ctrl)}.")
    dis = [i for i in real if got[i]["choice"] != "word"] + [i for i in ctrl if got[i]["choice"] != "other"]
    if dis:
        md.append("")
        md.append("| item | kind | dialogue | person |")
        md.append("|---|---|---|---|")
        for i in sorted(dis):
            md.append(f"| {i} | {f6[i]['kind']} | {f6[i]['dialogue']} | {got[i]['choice']} |")
    md.append("")


def effort(labels, md):
    vals = [v for v in labels.values() if v.get("at")]
    if not vals:
        return
    ms = sum(min(v.get("ms") or 0, 300000) for v in vals)
    days = sorted({v["at"][:10] for v in vals})
    by = collections.Counter(v.get("chapter") for v in vals)
    md.append("## Effort")
    md.append("")
    md.append(f"- {len(vals)} answers on {len(days)} day(s) ({days[0]} to {days[-1]}); reading time about "
              f"{ms / 60000:.0f} minutes (each answer counts at most 5 minutes).")
    md.append("- Answers per chapter: " + "; ".join(f"chapter {c} {by[c]}" for c in sorted(by)) + ".")
    md.append("")


def report(all_labels, key):
    labels = {i: v for i, v in all_labels.items() if isinstance(v, dict) and v.get("v") == 3}
    old = len(all_labels) - len(labels)
    unknown = sorted(i for i in labels if i not in key and i.rsplit("-", 1)[0] not in key)
    md = ["# Labels of the game \"Guesthouse or Not\" against the hidden key", "",
          f"Labels of version 3: {len(labels)}. Other documents (the first game version or unknown): {old}.", ""]
    if unknown:
        md += [f"Documents with an id that the key does not know: {', '.join(unknown[:10])}.", ""]
    chapter1(labels, key, md)
    chapter2(labels, key, md)
    chapter3(labels, key, md)
    effort(labels, md)
    return "\n".join(md)


def synthetic(key):
    """Labels made from the key with seeded noise, for the self-test only."""
    rng = random.Random(SEED)
    out = {}
    for i, k in key.items():
        base = {"item": i, "chapter": k["chapter"], "part": k["part"], "ms": rng.randrange(3000, 60000),
                "at": f"2026-11-{rng.randrange(13, 15)}T10:{rng.randrange(10, 59)}:00Z", "v": 3}
        if k["chapter"] == 1:
            c = {"hotel_only": "hotel_only", "guesthouse_only": "guesthouse_ok"}.get(k["rule"], "unclear")
            if rng.random() < 0.25:
                c = rng.choice(list(WANT))
            out[i] = {**base, "q": "want", "choice": c}
        elif k["chapter"] == 2:
            t = k["rule_tell"] if rng.random() > 0.2 else not k["rule_tell"]
            out[i] = {**base, "q": "tell", "choice": "tell" if t else "none",
                      "picks": rng.sample(list(PICKS), rng.randrange(1, 3)) if t else []}
        elif k["part"] == "3a":
            for q, f in (("interest", "model_interest"), ("claim", "model_claim"), ("steer", "model_steer")):
                m = (k[f] or "none") if q == "steer" else ("yes" if k[f] else "no")
                out[f"{i}-{q}"] = {**base, "q": q, "choice": m if rng.random() > 0.15 else "unsure"}
        else:
            c = "word" if k["kind"] == "F.6 text" else "other"
            out[i] = {**base, "q": "reason", "choice": c if rng.random() > 0.15 else "unclear"}
    out["p001"] = {"at": "2026-11-12T15:40:51.182Z", "choice": "cant_tell", "level": 1, "ms": 43249}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("labels", nargs="?", help="the export: a folder of JSON files, a JSON file or a JSON-lines file")
    ap.add_argument("--key", default=str(KEY))
    ap.add_argument("--out", help="also write the report to this Markdown file")
    ap.add_argument("--local", action="store_true", help=f"also read {LOCAL.name} (the local-network game)")
    ap.add_argument("--selftest", action="store_true", help="run on synthetic labels made from the key")
    a = ap.parse_args()
    key = json.loads(pathlib.Path(a.key).read_text())["items"]
    if a.selftest:
        text = "SELF-TEST: synthetic labels, not real data.\n\n" + report(synthetic(key), key)
        assert "kappa" in text and "Chapter 3" in text
        print(text)
        return
    if not a.labels and not a.local:
        ap.error("give the labels export, --local, or --selftest")
    labels = load_labels(a.labels) if a.labels else {}
    if a.local:
        labels.update(load_labels(LOCAL) if LOCAL.exists() else {})
    text = report(labels, key)
    print(text)
    if a.out:
        pathlib.Path(a.out).write_text(text + "\n")
        print(f"\nwritten: {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
