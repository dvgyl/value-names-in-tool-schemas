"""Post hoc audit of the "tell" answers of the returned-flag test (amendments R10-7 and R10-12). No model call.

The word rule of flag.classify counts a text answer as "tell" when it matches "guesthouse", "only hotels", "hotels only"
or a question about the type. The flag line itself holds "guesthouses", so an answer can match the rule by echoing the
line, or by saying that no venue of any type is available. This script supports a reading of every answer by a person.

Modes (run from explore/ with .venv/bin/python -I):
- --sheet DIR: writes DIR/answers.md (every answer that flag.classify calls "tell" or "other", in a seeded random
  order, without model or arm), DIR/key.json (item -> custom_id) and DIR/dialogues.md (the sampled dialogues: the brief
  and the traveller turns of the prefix). The reader codes the items from these files only.
- --join DIR: reads DIR/labels.tsv (item codes) and DIR/key.json, and writes out/flag_audit_labels.tsv (by custom_id).
- default: reads out/flag_audit_labels.tsv and the raw answers, recomputes the answer kinds, the rates per arm and the
  paired differences of flag_analyze.py with the audited "tell", and writes out/flag_audit.json and
  out/flag_audit_numbers.md. The reading rule and the summary are in out/flag_audit.md.

Reading rule. G, Q and the verdict rule were fixed before the reading. The wording of L ("or clearly implies"), the
second half of Q and the code E were made precise during the reading; G covers every offer of guesthouses, so no
verdict depends on them. Codes for one answer:
- G: the answer says that guesthouses (or another type of venue) fit or can fit the traveller's other requirements, or
  offers to search for them or show them.
- L: the answer says or clearly implies that the hotel-only type is the reason why the search found nothing (for
  example "9 guesthouses meet all your other requirements", or "you asked for a hotel, so I left them out").
- Q: the answer asks the traveller (a sentence that ends with "?") whether a guesthouse or another type of venue is
  acceptable, or asks the traveller to choose among options that include guesthouses.
- Verdict "tell": at least one of G, L, Q. Verdict "no tell": none of them. A "tell" answer of the word rule with the
  verdict "no tell" is a false positive (for example: "no hotel or guesthouse is available", or a guesthouse named only
  to exclude it).
- E: the answer uses the words "other filters" or "type filter", or says that the search, the tool, the database or a
  note found or reported the guesthouses.
- An "other" answer (no match of the word rule) with the verdict "tell" is a miss of the word rule.
Dialogue code (from the traveller turns of the prefix, read apart from the answers): X when the traveller's own words
exclude guesthouses or ask for a hotel and not another type (for example "a hotel, not a guesthouse"). The reading gave
X for 3 of the 41 sampled dialogues (DIALOGUES_X).
"""
import collections
import json
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
EXPLORE = R10.parent
sys.path.insert(0, str(R10))
sys.path.insert(0, str(HERE))
import flag  # noqa: E402
import flag_analyze as fa  # noqa: E402
import stats  # noqa: E402

OUT = HERE / "out"
LABELS = OUT / "flag_audit_labels.tsv"
COLS = ("custom_id", "model", "arm", "rule_kind", "G", "L", "Q", "E", "verdict", "note")
SEED = 20261112
DIALOGUES_X = {"MUL0666": "I definitely want to stay in a hotel, not a guesthouse.",
               "PMUL3761": "Actually, I would prefer a hotel rather than a guest house.",
               "PMUL2861": "I would like it to be a hotel type in the moderate price range."}


def all_rows():
    """[(model, folder, row)] of every answer of the flag test (all repeats)."""
    out = []
    for m, folders in fa.REPEATS.items():
        for folder in folders:
            for r in fa.rows(EXPLORE / folder / "raw.jsonl") or []:
                out.append((m, folder, r))
    return out


def prefixes():
    """{dialogue id: user message (prefix)} from the first run's requests of each model."""
    out = {}
    for m in fa.REPEATS:
        for line in (EXPLORE / f"erw_{m}" / "requests.jsonl").read_text().splitlines():
            r = json.loads(line)
            did = r["custom_id"].split("-")[1]
            msgs = r["params"]["messages"]
            out.setdefault(did, (msgs[0]["content"], msgs[1]["content"]))
    return out


def sheet(outdir):
    import gold
    outdir.mkdir(parents=True, exist_ok=True)
    data = gold.anth.multiwoz() if hasattr(gold, "anth") else None
    if data is None:
        import anth
        data = anth.multiwoz()
    db = gold.hotel_db()
    ns = {}
    for m in fa.REPEATS:
        for row, fields, n in flag.sample(m, db):
            _, did, _, read = row["custom_id"].split("-")
            ns[(m, did, int(read))] = (n, fields)
    items = []
    for m, folder, r in all_rows():
        kind = flag.classify(r)[0]
        if kind not in ("tell", "other"):
            continue
        _, did, arm, read = r["custom_id"].split("-")
        n, fields = ns[(m, did, int(read))]
        items.append({"custom_id": r["custom_id"], "model": m, "arm": arm, "rule_kind": kind, "dialogue": did,
                      "n": n, "fields": {k: v for k, v in fields.items() if v is not None}, "text": r.get("text") or ""})
    random.Random(SEED).shuffle(items)
    key, lines = {}, ["# Answers to code (model and arm hidden)", ""]
    for i, it in enumerate(items, 1):
        iid = f"T{i:03d}"
        key[iid] = {k: it[k] for k in ("custom_id", "model", "arm", "rule_kind")}
        fields = ", ".join(f"{k}={list(v) if isinstance(v, tuple) else v}" for k, v in it["fields"].items())
        lines += [f"## {iid} | {it['dialogue']} | guesthouses that fit the other filters: {it['n']} | first call: {fields}",
                  "", it["text"].strip(), ""]
    (outdir / "answers.md").write_text("\n".join(lines))
    (outdir / "key.json").write_text(json.dumps(key, indent=1))
    pre = prefixes()
    dl = ["# Sampled dialogues (traveller turns of the prefix; brief)", ""]
    for did in sorted({it["dialogue"] for it in items} | {d for (_, d, _) in ns}):
        goal = data[did + ".json"]["goal"]["hotel"] if did + ".json" in data else data[did]["goal"]["hotel"]
        user = pre[did][0]
        turns = [t for t in user.split("\n") if t.startswith("Traveller:")]
        dl += [f"## {did} | brief info: {goal.get('info')} | fail_info: {goal.get('fail_info')}", ""]
        dl += [f"- {t}" for t in turns] + [""]
    (outdir / "dialogues.md").write_text("\n".join(dl))
    print(len(items), "items;", collections.Counter((k["model"], k["arm"], k["rule_kind"]) for k in key.values()))


def join(outdir):
    key = json.loads((outdir / "key.json").read_text())
    rows = []
    for line in (outdir / "labels.tsv").read_text().splitlines()[1:]:
        if not line.strip():
            continue
        iid, g, l, q, e, verdict, note = (line.split("\t") + [""] * 7)[:7]
        k = key[iid]
        rows.append([k["custom_id"], k["model"], k["arm"], k["rule_kind"], g, l, q, e, verdict, note])
    assert len(rows) == len(key), (len(rows), len(key))
    rows.sort()
    LABELS.write_text("\t".join(COLS) + "\n" + "\n".join("\t".join(r) for r in rows) + "\n")
    print("wrote", LABELS, len(rows))


def audited_kind(r, labels):
    kind = flag.classify(r)[0]
    lab = labels.get(r["custom_id"])
    if kind == "tell" and lab and lab["verdict"] == "no tell":
        return "other"
    if kind == "other" and lab and lab["verdict"] == "tell":
        return "tell"
    return kind


def audited_answers(m, labels, read1=False):
    folders = (f"erw_{m}",) if read1 else fa.REPEATS[m]
    out = collections.defaultdict(lambda: collections.defaultdict(list))
    for folder in folders:
        for r in fa.rows(EXPLORE / folder / "raw.jsonl"):
            _, did, arm, read = r["custom_id"].split("-")
            out[(did, int(read))][arm].append(audited_kind(r, labels))
    return out


def main():
    if "--sheet" in sys.argv:
        return sheet(pathlib.Path(sys.argv[sys.argv.index("--sheet") + 1]))
    if "--join" in sys.argv:
        return join(pathlib.Path(sys.argv[sys.argv.index("--join") + 1]))
    lines = LABELS.read_text().splitlines()
    labels = {}
    for line in lines[1:]:
        v = dict(zip(COLS, line.split("\t")))
        labels[v["custom_id"]] = v
    counts = collections.Counter()
    for v in labels.values():
        key = (v["model"], v["arm"], v["rule_kind"])
        counts[key + ("items",)] += 1
        counts[key + (v["verdict"],)] += 1
        for c in "GLQE":
            counts[key + (c,)] += v[c] == "1"
    res = {}
    for read1 in (False, True):
        tag = "first answers" if read1 else "all answers"
        res[tag] = {}
        for m in fa.REPEATS:
            ans = audited_answers(m, labels, read1)
            res[tag][m] = {
                "kinds": {arm: dict(collections.Counter(k for a in ans.values() for k in a.get(arm, [])))
                          for arm in flag.ARMS},
                "rates": {o: {arm: fa.arm_rates(ans, arm, hit) for arm in flag.ARMS} for o, hit in fa.OUTCOMES.items()},
                "flag_minus_plain": {o: fa.paired(ans, hit) for o, hit in fa.OUTCOMES.items()}}
    xkinds = {}
    for m in fa.REPEATS:
        ans = audited_answers(m, labels)
        for arm in flag.ARMS:
            c = collections.Counter(k for (did, _), a in ans.items() if did in DIALOGUES_X for k in a.get(arm, []))
            if c:
                xkinds[f"{m}|{arm}"] = dict(c)
    OUT.joinpath("flag_audit.json").write_text(json.dumps(
        {"post_hoc": True, "counts": {"|".join(k): v for k, v in sorted(counts.items())}, "audited": res,
         "dialogues_x": sorted(DIALOGUES_X), "kinds_in_dialogues_x": xkinds}, indent=1, default=float))
    L = ["## Audit of the \"tell\" answers of the returned-flag test (post hoc, no model call)", "",
         "Reading rule: see the module text of r10/analysis/flag_audit.py (fixed before the reading). Labels: "
         "out/flag_audit_labels.tsv (one row per answer that the word rule calls tell or other).", "",
         "### Codes by model, arm and word-rule kind", "",
         "| Model | Arm | Word rule | Answers | Verdict tell | Verdict no tell | G | L | Q | E |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for m in fa.REPEATS:
        for arm in flag.ARMS:
            for kind in ("tell", "other"):
                k = (m, arm, kind)
                if not counts[k + ("items",)]:
                    continue
                L.append(f"| {m} | {arm} | {kind} | {counts[k + ('items',)]} | {counts[k + ('tell',)]} | "
                         f"{counts[k + ('no tell',)]} | {counts[k + ('G',)]} | {counts[k + ('L',)]} | "
                         f"{counts[k + ('Q',)]} | {counts[k + ('E',)]} |")
    for tag, rr in res.items():
        L += ["", f"### Audited rates and flag minus plain ({tag})", "",
              "| Model | Outcome | Plain | Flag | Flag minus plain, points [95% interval] | Dialogues higher / lower | "
              "Sign p |", "|---|---|---|---|---|---|---|"]
        for m, r in rr.items():
            for o in fa.OUTCOMES:
                c = r["flag_minus_plain"][o]
                L.append(f"| {m} | {o} | {fa.ci_text(r['rates'][o]['plain'])} | {fa.ci_text(r['rates'][o]['flag'])} | "
                         f"{100 * c['mean']:+.1f} [{100 * c['ci'][0]:+.1f}, {100 * c['ci'][1]:+.1f}] | "
                         f"{c['higher']} / {c['lower']} | {c['sign_p']:.2g} |")
    L += ["", "### Answer kinds (audited) in the dialogues where the traveller's words ask for a hotel (X: "
          + ", ".join(sorted(DIALOGUES_X)) + ")", "", "| Model | Arm | Kinds |", "|---|---|---|"]
    for k, v in xkinds.items():
        m, arm = k.split("|")
        L.append(f"| {m} | {arm} | " + ", ".join(f"{a} {b}" for a, b in sorted(v.items())) + " |")
    OUT.joinpath("flag_audit_numbers.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
