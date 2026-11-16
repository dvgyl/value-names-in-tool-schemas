"""The human baseline at the first request (exploratory, post hoc: a reviewer asked for it on 2026-11-12).

MultiWOZ was collected with a person in the agent's role. On the 554 prefixes of the tool-call study (all turns up to
the first traveller turn that says "hotel"), this script reads that person's next reply: its text and its dialogue
acts (dialogue_acts.json). No model answer is read. Outputs: r10/analysis/out/human.json and human.md.

Classes of the reply (one reply can be in more than one class):
- asks_type: a Hotel-Request act on the slot Type, or a question in the text that names both kinds ("hotel or
  guesthouse", "guesthouse or hotel").
- mentions_guesthouse: the text says "guesthouse" or "guest house", or an act holds Type = guesthouse, or an act
  names a venue whose type in hotel_db.json is guesthouse.
- names_hotels_only: the reply names one or more venues, and every named venue is a hotel in hotel_db.json.
- asks_other: a Hotel-Request act on another slot (area, price, stars, parking, internet), and not asks_type.
- none_of_these: none of the four.
Also reported: the dialogue-state annotation after the reply (metadata hotel semi type), as a second view of what the
person in the agent's role took as the requirement.
Usage (from explore/): .venv/bin/python -I r10/analysis/human_baseline.py
"""
import collections
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
EXPLORE = R10.parent
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free"):
    sys.path.insert(0, str(EXPLORE / sub))
sys.path.insert(0, str(R10))
sys.path.insert(0, str(HERE))
import anth  # noqa: E402
import briefsearch as bs  # noqa: E402
import gold  # noqa: E402
import runs  # noqa: E402
import stats  # noqa: E402
import zforms  # noqa: E402
import zruns  # noqa: E402

OUT = HERE / "out"
GUEST = re.compile(r"guest ?houses?", re.I)
BOTH_Q = re.compile(r"hotel or (?:a )?guest ?house|guest ?house or (?:a )?hotel", re.I)
CLASSES = ("asks_type", "mentions_guesthouse", "names_hotels_only", "asks_other", "none_of_these")


def classify(d, acts_d, by_key):
    i = zforms.prefix_end(d)
    reply = d["log"][i + 1] if i + 1 < len(d["log"]) else None
    if reply is None:
        return None, None
    a = acts_d.get(str((i + 2) // 2), {}) if isinstance(acts_d, dict) else {}
    a = a if isinstance(a, dict) else {}
    text = reply.get("text", "")
    names, types, req = [], [], []
    for act, slots in a.items():
        dom, kind = act.split("-")[0], act.split("-")[-1]
        for slot, value in slots:
            if dom in ("Hotel", "Booking") and slot == "Name" and value not in ("?", "none"):
                names.append(value)
            if dom == "Hotel" and slot == "Type":
                types.append(value.lower())
            if dom == "Hotel" and kind == "Request":
                req.append(slot)
    venues = [by_key.get(zruns._key(n)) for n in names]
    vtypes = [v["type"] for v in venues if v]
    c = set()
    if "Type" in req or BOTH_Q.search(text):
        c.add("asks_type")
    if GUEST.search(text) or any("guest" in t for t in types) or "guesthouse" in vtypes:
        c.add("mentions_guesthouse")
    if vtypes and all(t == "hotel" for t in vtypes) and len(vtypes) == len(names):
        c.add("names_hotels_only")
    if req and "asks_type" not in c:
        c.add("asks_other")
    if not c:
        c.add("none_of_these")
    state = ((reply.get("metadata") or {}).get("hotel", {}).get("semi", {}) or {}).get("type", "")
    return c, (state or "not set").lower()


def main():
    data, g = runs.context()
    db = gold.hotel_db()
    by_key = {zruns._key(h["name"]): h for h in zforms.HOTELS}
    acts = json.loads((anth.DATA / "dialogue_acts.json").read_text())
    ids = list(g["booked"])
    sub = bs.brief_subsets(data, ids, db)
    res = {}
    for label, group in (("all 554 prefixes", ids), (f"brief sets no type ({len(sub['no_type'])})", sub["no_type"]),
                         (f"no type, no venue name ({len(sub['no_name'])})", sub["no_name"])):
        per = {k: [] for k in CLASSES}
        state = collections.Counter()
        n = 0
        for d in group:
            c, st = classify(data[d], acts.get(d.removesuffix(".json"), {}), by_key)
            if c is None:
                continue
            n += 1
            for k in CLASSES:
                per[k].append((int(k in c), 1))
            state[st] += 1
        row = {"replies": n, "state_after_reply": dict(state)}
        for k in CLASSES:
            pt, lo, hi = stats.cluster_bootstrap({"all": per[k]}, lambda gg: sum(r[0] for r in gg["all"]) / len(gg["all"]))
            row[k] = {"k": sum(r[0] for r in per[k]), "share": pt, "ci": [lo, hi]}
        res[label] = row
    OUT.mkdir(exist_ok=True)
    (OUT / "human.json").write_text(json.dumps({"exploratory": True, "post_hoc": True, "groups": res}, indent=1))
    L = ["## The human baseline at the first request (exploratory, post hoc)", "",
         "The reply of the person in the agent's role, right after the first traveller turn that says \"hotel\".", "",
         "| Group | Replies | Asks about the type | Mentions or offers a guesthouse | Names hotels only | Asks about "
         "another slot | None of these |", "|---|---|---|---|---|---|---|"]
    for label, r in res.items():
        L.append(f"| {label} | {r['replies']} | " + " | ".join(
            f"{r[k]['k']} ({100 * r[k]['share']:.1f}% [{100 * r[k]['ci'][0]:.1f}, {100 * r[k]['ci'][1]:.1f}])"
            for k in CLASSES) + " |")
    L += ["", "Dialogue-state annotation of `type` after the reply:", ""]
    for label, r in res.items():
        L.append(f"- {label}: {json.dumps(r['state_after_reply'])}")
    (OUT / "human.md").write_text("\n".join(L) + "\n")
    print((OUT / "human.md").read_text())


if __name__ == "__main__":
    main()
