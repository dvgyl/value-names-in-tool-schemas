"""Stored answers for the release-test simulation (amendment R10-26 of PROTOCOL.md).

No model call, no paid call, no network call. The loaders are the frozen loaders of the study folder
(r10/analysis/rtest_v.py, rtest_vr.py, rtest_vr2.py); they refuse folders whose names start with "em", sealed
files, key files and .env files. This script edits no frozen script and no frozen output.

Commands (run from any folder; the stored answers are read in place):
    python3 -I stored.py fit        # base distributions -> out/fit.json, out/fit.md
    python3 -I stored.py fidelity   # rules.py on the stored comparisons of the paper -> out/fidelity.json, .md
    python3 -I stored.py tails      # stored comparisons at 99.5%: seeds, 20,000 draws, index -> out/tails_stored.*

fit: for each profile (Haiku tool calls, DeepSeek forms, Sol tool calls) and each request set (open, specific),
the per-request counts (hotel values k of valid answers m) pooled over every stored source of the unchanged tool or
form, and a beta-binomial maximum-likelihood fit of Beta(a, b) for the per-request hotel probability.
"""
import collections
import importlib.util
import json
import math
import pathlib
import random
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
ROOT = HERE.parents[1]  # explore/ of the repository
EXPLORE = ROOT
AN = EXPLORE / "r10" / "analysis"
PAPER = ROOT / "manuscript.md"  # repository copy: the manuscript is not in this repository, so this check cannot run here (the command fidelity)
sys.path.insert(0, str(HERE))
import rules  # noqa: E402


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)  # no main() runs on import
    return m


V = module("rs_v", AN / "rtest_v.py")      # stored tool calls (AA sources), sets, stats
VR = module("rs_vr", AN / "rtest_vr.py")   # R10-20 loader and parser (independent check)
VR2 = module("rs_vr2", AN / "rtest_vr2.py")  # R10-22 loader and parser (independent check)

SEED, DRAWS = 20261112, 2000


def refuse(folder):
    assert not str(folder).startswith("em"), f"refused: {folder}"


def sets_r10_6():
    data, g = V.runs.context()
    return V.ra.request_sets(data, g)


# ------------------------------------------------------------------------------------------------ sources

def vr_folder_cell(folder, cell):
    """{dialogue.json: [scores]} of one cell of an R10-20-style run, with the R10-20 parser (rtest_vr.read_row)."""
    refuse(folder)
    rows = VR.jsonl(VR.EXPLORE / folder / "raw.jsonl")
    reads = collections.defaultdict(list)
    for r in rows:
        _, d, c, _ = r["custom_id"].split("-")
        if c == cell:
            reads[(d + ".json", c)].append(VR.read_row(r, c))
    return {d: VR.valid_scores(reads, d, cell) for (d, _c) in reads}


def fit_sources():
    """Profile -> list of (label, {dialogue.json: [scores]}) of the unchanged tool or form."""
    out = {}
    out["haiku"] = [(f"{lab} ({'all' if rd is None else 'read ' + str(rd)})", V.tool_reads(folders, cell, rd))
                    for lab, folders, cell, _one, rd in V.AA["haiku"]]
    out["deepseek"] = [("erk_deepseek p0", vr_folder_cell("erk_deepseek", "p0")),
                       ("erk_deepseek prep", vr_folder_cell("erk_deepseek", "prep")),
                       ("erk3_deepseek p0", vr_folder_cell("erk3_deepseek", "p0"))]
    out["sol"] = ([(f"{lab} (read {rd})", V.tool_reads(folders, cell, rd)) for lab, folders, cell, _one, rd in V.AA["sol"]]
                  + [("erk_sol t0", vr_folder_cell("erk_sol", "t0")), ("erk_sol trep", vr_folder_cell("erk_sol", "trep")),
                     ("erk2_sol t0", vr_folder_cell("erk2_sol", "t0"))])
    return out


# ------------------------------------------------------------------------------------------------ fit

def bb_loglik(counts, a, b):
    """counts: {(k, m): number of requests}. Beta-binomial log likelihood without the binomial coefficient."""
    if a <= 0 or b <= 0:
        return -math.inf
    lg = math.lgamma
    base = lg(a + b) - lg(a) - lg(b)
    return sum(c * (lg(k + a) + lg(m - k + b) - lg(m + a + b) + base) for (k, m), c in counts.items())


def nelder_mead(f, x0, step=0.5, iters=2000, tol=1e-10):
    """Minimise f over R^2 (a small standard Nelder-Mead)."""
    pts = [list(x0), [x0[0] + step, x0[1]], [x0[0], x0[1] + step]]
    vals = [f(p) for p in pts]
    for _ in range(iters):
        order = sorted(range(3), key=lambda i: vals[i])
        pts, vals = [pts[i] for i in order], [vals[i] for i in order]
        if abs(vals[2] - vals[0]) < tol:
            break
        c = [(pts[0][j] + pts[1][j]) / 2 for j in range(2)]
        r = [c[j] + (c[j] - pts[2][j]) for j in range(2)]
        fr = f(r)
        if fr < vals[0]:
            e = [c[j] + 2 * (c[j] - pts[2][j]) for j in range(2)]
            fe = f(e)
            pts[2], vals[2] = (e, fe) if fe < fr else (r, fr)
        elif fr < vals[1]:
            pts[2], vals[2] = r, fr
        else:
            k = [c[j] + 0.5 * (pts[2][j] - c[j]) for j in range(2)]
            fk = f(k)
            if fk < vals[2]:
                pts[2], vals[2] = k, fk
            else:
                for i in (1, 2):
                    pts[i] = [pts[0][j] + 0.5 * (pts[i][j] - pts[0][j]) for j in range(2)]
                    vals[i] = f(pts[i])
    i = min(range(3), key=lambda i: vals[i])
    return pts[i], vals[i]


def bb_pmf(k, m, a, b):
    lg = math.lgamma
    return math.exp(lg(m + 1) - lg(k + 1) - lg(m - k + 1) + lg(k + a) + lg(m - k + b) - lg(m + a + b)
                    + lg(a + b) - lg(a) - lg(b))


def fit():
    sets = sets_r10_6()
    out = {"what": "beta-binomial maximum-likelihood fit of the per-request hotel probability of the unchanged "
                   "tool or form (amendment R10-26)", "profiles": {}}
    for prof, srcs in fit_sources().items():
        entry = {"sources": [lab for lab, _ in srcs], "sets": {}}
        for s in ("open", "specific"):
            km = []
            for d in sets[s]:
                v = [x for _, src in srcs for x in src.get(d, [])]
                if v:
                    km.append((sum(v), len(v)))
            counts = collections.Counter(km)
            (la, lb), nll = nelder_mead(lambda x: -bb_loglik(counts, math.exp(x[0]), math.exp(x[1])), [-1.0, 0.0])
            a, b = math.exp(la), math.exp(lb)
            m_mode = collections.Counter(m for _, m in km).most_common(1)[0][0]
            obs = [k for k, m in km if m == m_mode]
            n_mode = len(obs)
            pred0, predm = n_mode * bb_pmf(0, m_mode, a, b), n_mode * bb_pmf(m_mode, m_mode, a, b)
            entry["sets"][s] = {
                "requests": len(km), "answers": sum(m for _, m in km), "hotel": sum(k for k, _ in km),
                "rate": sum(k for k, _ in km) / sum(m for _, m in km), "a": a, "b": b, "mean": a / (a + b),
                "neg_loglik": nll, "modal_answers_per_request": m_mode, "requests_with_modal_answers": n_mode,
                "observed": {"all_0": sum(k == 0 for k in obs), "all_m": sum(k == m_mode for k in obs),
                             "mixed": sum(0 < k < m_mode for k in obs)},
                "predicted": {"all_0": pred0, "all_m": predm, "mixed": n_mode - pred0 - predm}}
        out["profiles"][prof] = entry
    OUT.mkdir(exist_ok=True)
    (OUT / "fit.json").write_text(json.dumps(out, indent=1))
    lines = ["# Base distributions (beta-binomial fit, unchanged tool or form)", "",
             "Per request: the hotel values k among the m valid answers, pooled over the stored sources below. "
             "Fit: Beta(a, b) for the per-request probability, by maximum likelihood (Nelder-Mead on log a, log b). "
             "Check: observed and predicted numbers of requests with no hotel value, only hotel values and a mix, "
             "among the requests with the modal number of answers.", "",
             "| Profile | Set | Requests | Answers | Rate | a | b | Mean | Modal m | All 0 obs / pred | All m obs / pred | Mixed obs / pred |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|"]
    for prof, e in out["profiles"].items():
        for s, x in e["sets"].items():
            o, p = x["observed"], x["predicted"]
            lines.append(f"| {prof} | {s} | {x['requests']} | {x['answers']} | {100 * x['rate']:.1f}% | {x['a']:.4f} | "
                         f"{x['b']:.4f} | {100 * x['mean']:.1f}% | {x['modal_answers_per_request']} | "
                         f"{o['all_0']} / {p['all_0']:.1f} | {o['all_m']} / {p['all_m']:.1f} | {o['mixed']} / {p['mixed']:.1f} |")
    lines += [""] + [f"- {prof}: {', '.join(e['sources'])}" for prof, e in out["profiles"].items()]
    (OUT / "fit.md").write_text("\n".join(lines) + "\n")
    print((OUT / "fit.md").read_text())


# ------------------------------------------------------------------------------------------------ comparisons

def boot_vals(diffs, seed=SEED, draws=DRAWS):
    """The frozen bootstrap (stats.cluster_bootstrap and rtest_final9.boot): sorted means of draws resamples."""
    n = len(diffs)
    rng = random.Random(seed)
    return sorted(sum(rng.choices(diffs, k=n)) / n for _ in range(draws))


def view(diffs, seed=SEED, draws=DRAWS):
    return {"change": sum(diffs) / len(diffs), "up": sum(x > 0 for x in diffs), "down": sum(x < 0 for x in diffs),
            "pairs": len(diffs), "vals": boot_vals(diffs, seed, draws)}


def diffs_cells(valid_scores, reads, ids, control, update):
    out = []
    for d in ids:
        a, b = valid_scores(reads, d, control), valid_scores(reads, d, update)
        if a and b:
            out.append(100 * (sum(b) / len(b) - sum(a) / len(a)))
    return out


def diffs_of(ctrl, upd, ids):
    return [100 * (sum(upd[d]) / len(upd[d]) - sum(ctrl[d]) / len(ctrl[d])) for d in ids if ctrl.get(d) and upd.get(d)]


def order_of(run):
    order = []
    for r in V.runs.requests(run):
        d = r["custom_id"].split("-")[1] + ".json"
        if not order or order[-1] != d:
            order.append(d)
    return order


R20 = {"sol": "tool", "luna": "tool", "deepseek": "form", "qwen": "form", "gemma": "form"}
UPD_NAME = {"a": "Repeat", "b": "Paraphrase 1", "c": "Full rename", "d": "Field-order edit", "e": "Paraphrase 2"}


def comparisons():
    """Every stored comparison of the paper's release tables, as per-request differences (points) per set.
    Returns a list of dicts: name, table, model, update, sets {open: diffs, specific: diffs}, level_run, level_final."""
    out = []
    data = json.loads(VR.safe(VR.MW / "data.json").read_text())
    sets20 = VR.load_sets(data, order_of("erk_luna"))
    for m, ch in R20.items():
        reads, _ = VR.load(m)
        for u in ("a", "b", "c"):
            ctrl, upd = VR.CONTROL[ch], VR.UPDATES[u][ch]
            out.append({"name": f"R10-20 {m} {u}", "table": "12", "model": m, "update": u, "channel": ch,
                        "sets": {k: diffs_cells(VR.valid_scores, reads, sets20[k], ctrl, upd) for k in ("open", "specific")},
                        "level_run": VR.LEVEL[ch], "level_final": rules.level(10)})
    sets22 = VR2.load_sets(data, order_of("erk2_luna"))
    for m, run in VR2.MODELS.items():
        reads, _ = VR2.load(run)
        for u, cell in (("d", "tord"), ("e", "tpar2")):
            out.append({"name": f"R10-22 {m} {u}", "table": "12", "model": m, "update": u, "channel": "tool",
                        "sets": {k: diffs_cells(VR2.valid_scores, reads, sets22[k], "t0", cell) for k in ("open", "specific")},
                        "level_run": rules.level(4), "level_final": rules.level(4)})
    sets = sets_r10_6()
    for read, tag in ((None, "all answers"), (1, "first answer")):
        cc = V.tool_reads(("erc_haiku",), "t0", read)
        for u, folder, cell, c_final in (("a", "erc2_haiku", "trep", 12), ("d", "erc_haiku", "tord", 6)):
            ud = V.tool_reads((folder,), cell, read)
            out.append({"name": f"R10-16 haiku {u} ({tag})", "table": "11", "model": "haiku", "update": u,
                        "answers": tag, "sets": {k: diffs_of(cc, ud, sets[k]) for k in ("open", "specific")},
                        "level_run": rules.level(4), "level_final": rules.level(c_final)})
    for m, srcs in V.AA.items():
        src = [(s_[0], V.tool_reads(s_[1], s_[2], s_[3])) for s_ in srcs]
        for i in range(len(src)):
            for j in range(i + 1, len(src)):
                (la, a), (lb, b) = src[i], src[j]
                out.append({"name": f"unchanged {m}: {la} v {lb}", "table": "29 stored", "model": m, "a": la, "b": lb,
                            "sets": {k: diffs_of(a, b, sets[k]) for k in ("open", "specific")},
                            "level_run": rules.level(4), "level_final": rules.level(10)})
    return out


def decisions(views, lev_run, lev_final):
    d = {}
    for rule in ("original", "revised"):
        d[rule] = rules.decide_sets(views, lev_run, rule)
    d["final"] = rules.decide_sets(views, lev_final, "final")
    return d


# ------------------------------------------------------------------------------------------------ the paper's tables

def num(s):
    return float(s.replace("−", "-").replace("+", ""))


def paper_tables():
    """Parse Tables 5, 11 and 12 of the paper (the values printed in the PDF master)."""
    text = PAPER.read_text()
    lines = text.splitlines()

    def table_after(caption):
        i = next(k for k, x in enumerate(lines) if x.startswith(caption))
        rows, started = [], False
        for x in lines[i + 1:]:
            if x.startswith("|"):
                started = True
                rows.append([c.strip() for c in x.strip().strip("|").split("|")])
            elif started:
                break
        return rows[2:]  # header and rule line
    t5 = table_after("**Table 5.**")
    t11 = table_after("**Table 11.**")
    t12 = table_after("**Table 12.**")
    models5 = ["sol", "luna", "deepseek", "qwen", "gemma", "haiku"]
    upd5 = {"Repeat (unchanged)": "a", "Field-order edit": "d", "Paraphrase 1": "b", "Paraphrase 2": "e", "Full rename": "c"}
    table5 = {}
    for r in t5:
        for m, v in zip(models5, r[1:7]):
            if v != "-":
                table5[(m, upd5[r[0]])] = v
    cell = re.compile(r"([−+]\d+\.\d) \[([−+]\d+\.\d), ([−+]\d+\.\d)\]; (\d+) / (\d+), p (=|<) (\d\.\d+)")
    names = {"Sol": "sol", "Luna": "luna", "DeepSeek": "deepseek", "Qwen": "qwen", "Gemma": "gemma"}
    upd12 = {v: k for k, v in UPD_NAME.items()}
    table12 = {}
    for r in t12:
        m, u = names[r[0]], upd12[r[1]]
        sets = {}
        for k, c in (("open", r[2]), ("specific", r[3])):
            g = cell.fullmatch(c)
            assert g, c
            sets[k] = {"change": g[1], "lo": g[2], "hi": g[3], "up": int(g[4]), "down": int(g[5]), "p": g[6] + " " + g[7]}
        table12[(m, u)] = {"sets": sets, "original": r[4], "revised": r[5], "final": r[6]}
    cell11 = re.compile(r"([−+]\d+\.\d) \[([−+]\d+\.\d), ([−+]\d+\.\d)\]")
    table11 = {}
    for r in t11:
        u = {"Repeat": "a", "Field-order edit": "d"}[r[0]]
        s = r[1].split(" ")[0]
        g = cell11.fullmatch(r[4])
        fa = r[6]
        entry = {"change": g[1], "lo": g[2], "hi": g[3], "set_decision": r[5]}
        if fa.startswith("the same"):
            entry["first"] = None
        else:
            g2 = cell11.match(fa)
            entry["first"] = {"change": g2[1], "lo": g2[2], "hi": g2[3], "set_decision": fa.split(", ")[-1]}
        table11[(u, s)] = entry
    return table5, table11, table12


def fmt1(x):
    s = f"{x:+.1f}"
    return s.replace("-", "−")


def fmt_p(p):
    return "< 0.0001" if p < 0.0001 else f"= {p:.4f}"


SET_WORDS = {rules.FLAG: "meets flag rule", rules.WITHIN: "within limits", rules.UNRESOLVED: "unresolved"}


# ------------------------------------------------------------------------------------------------ fidelity

def close(a, b, tol=1e-9):
    return abs(a - b) <= tol


def fidelity():
    stored20 = json.loads((AN / "out" / "release_test.json").read_text())["models"]
    stored22 = json.loads((AN / "out" / "release_test2.json").read_text())["models"]
    control = json.loads((AN / "out" / "control.json").read_text())["updates"]
    f9 = json.loads((AN / "out" / "rtest_final9.json").read_text())
    ver = {(e["model"], e["a"], e["b"]): e for e in
           json.loads((AN / "out" / "rtest_check_values.json").read_text())["item1"]["aa"]["one_answer"]}
    f9_pairs = {(e["model"], e["a"], e["b"]): e for e in f9["B"]["unchanged_one_answer"]}
    t5, t11, t12 = paper_tables()
    checks, rows = [], []

    def check(what, ok, detail=""):
        checks.append({"check": what, "ok": bool(ok), "detail": detail})

    tallies = {"original 98.75": collections.Counter(), "revised 98.75": collections.Counter(),
               "final 99.5": collections.Counter()}
    for c in comparisons():
        views = [view(c["sets"][k]) for k in ("open", "specific")]
        dec = decisions(views, c["level_run"], c["level_final"])
        ivs_run = [rules.endpoints(v["vals"], c["level_run"], "as_run") for v in views]
        row = {"name": c["name"], "table": c["table"], "pairs": [v["pairs"] for v in views],
               "change": [v["change"] for v in views], "interval_as_run": ivs_run,
               "up_down": [(v["up"], v["down"]) for v in views],
               "sign_p": [rules.sign_p(v["up"], v["down"]) for v in views],
               "level_run": c["level_run"], "level_final": c["level_final"],
               "original": dec["original"][0], "revised": dec["revised"][0], "final": dec["final"][0]}
        rows.append(row)
        n = c["name"]
        if n.startswith("R10-20") or n.startswith("R10-22"):
            m, u = c["model"], c["update"]
            st = (stored20[m]["updates"][u] if n.startswith("R10-20") else stored22[m]["updates"][u])
            for k, v, iv in zip(("open", "specific"), views, ivs_run):
                s = st["sets"][k]
                check(f"{n} {k}: change, interval, up/down equal to the stored result",
                      close(v["change"], s["change"]) and close(iv[0], s["interval"][0]) and close(iv[1], s["interval"][1])
                      and (v["up"], v["down"]) == (s["up"], s["down"]),
                      f"{v['change']:.4f} [{iv[0]:.4f}, {iv[1]:.4f}] {v['up']}/{v['down']}")
                p = t12[(m, u)]["sets"][k]
                printed = (fmt1(v["change"]), fmt1(iv[0]), fmt1(iv[1]), v["up"], v["down"], fmt_p(rules.sign_p(v["up"], v["down"])))
                check(f"{n} {k}: values equal to Table 12 of the paper",
                      printed == (p["change"], p["lo"], p["hi"], p["up"], p["down"], p["p"]), f"{printed} vs {p}")
            check(f"{n}: original and revised decisions equal to the stored result",
                  (dec["original"][0], dec["revised"][0]) == (st["first"]["release"], st["revised"]["release"]),
                  f"{dec['original'][0]}, {dec['revised'][0]}")
            fin = f9["F"]["final_rule"]["R10-20 at 99.5%" if n.startswith("R10-20") else "R10-22 at 98.75%"][m][u]
            check(f"{n}: final decision equal to rtest_final9", dec["final"][0] == fin, f"{dec['final'][0]} vs {fin}")
            p12 = t12[(m, u)]
            check(f"{n}: three decisions equal to Table 12 of the paper",
                  (dec["original"][0], dec["revised"][0], dec["final"][0]) == (p12["original"], p12["revised"], p12["final"]),
                  f"{dec['original'][0]}/{dec['revised'][0]}/{dec['final'][0]} vs {p12['original']}/{p12['revised']}/{p12['final']}")
            check(f"{n}: original decision equal to Table 5 of the paper", dec["original"][0] == t5[(m, u)],
                  f"{dec['original'][0]} vs {t5[(m, u)]}")
        elif n.startswith("R10-16"):
            u = c["update"]
            key = {"a": "haiku trep (a)", "d": "haiku tord (b)"}[u]
            variant = "all" if c["answers"] == "all answers" else "read1"
            st = control[key][variant]
            for k, v, iv in zip(("open", "specific"), views, ivs_run):
                s = st["sets"][k]
                check(f"{n} {k}: change and interval equal to control.json",
                      close(v["change"], s["change"]) and close(iv[0], s["interval"][0]) and close(iv[1], s["interval"][1]),
                      f"{v['change']:.4f} [{iv[0]:.4f}, {iv[1]:.4f}]")
                cls = rules.decide_sets([v], c["level_run"], "original")[1][0]
                frozen_word = {"flag-worthy": rules.FLAG, "absent": rules.WITHIN, "unresolved": rules.UNRESOLVED}[s["decision"]]
                check(f"{n} {k}: set class equal to control.json", cls == frozen_word, f"{cls} vs {s['decision']}")
                p = t11[(u, k)]
                pp = p if variant == "all" else (p["first"] or p)
                printed = (fmt1(v["change"]), fmt1(iv[0]), fmt1(iv[1]))
                check(f"{n} {k}: values equal to Table 11 of the paper",
                      printed == (pp["change"], pp["lo"], pp["hi"]), f"{printed} vs {pp}")
                check(f"{n} {k}: set decision equal to Table 11 of the paper",
                      SET_WORDS[cls] == pp["set_decision"] or (pp["set_decision"] == "unresolved" and cls == rules.UNRESOLVED),
                      f"{SET_WORDS[cls]} vs {pp['set_decision']}")
            check(f"{n}: original decision equal to control.json", dec["original"][0] == st["release"],
                  f"{dec['original'][0]} vs {st['release']}")
            if variant == "all":
                check(f"{n}: original decision equal to Table 5 of the paper", dec["original"][0] == t5[("haiku", u)],
                      f"{dec['original'][0]} vs {t5[('haiku', u)]}")
                name9 = {"a": "repeat (10 answers), haiku", "d": "field order (10 answers), haiku"}[u]
                fin = f9["F"]["final_rule"]["Table 18 rows"][name9]
                check(f"{n}: final decision equal to rtest_final9 (C = {round(0.05 / (1 - c['level_final']))})",
                      dec["final"][0] == fin, f"{dec['final'][0]} vs {fin}")
        else:
            key = (c["model"], c["a"], c["b"])
            e9 = f9_pairs[key]["98.75"]
            e95 = f9_pairs[key]["99.5"]
            check(f"{n}: original and revised decisions at 98.75% equal to rtest_final9",
                  (dec["original"][0], dec["revised"][0]) == (e9["first_as_run"], e9["revised_as_run"]),
                  f"{dec['original'][0]}, {dec['revised'][0]}")
            check(f"{n}: original decision equal to the independent check (rtest_check_values.json)",
                  dec["original"][0] == ver[key]["decision"], f"{dec['original'][0]} vs {ver[key]['decision']}")
            check(f"{n}: final decision at 99.5% equal to rtest_final9", dec["final"][0] == e95["final"],
                  f"{dec['final'][0]} vs {e95['final']}")
            tallies["original 98.75"][dec["original"][0]] += 1
            tallies["revised 98.75"][dec["revised"][0]] += 1
            tallies["final 99.5"][dec["final"][0]] += 1
    exp = {"original 98.75": {"flag": 2, "pass": 2, "hold": 25}, "revised 98.75": {"pass": 2, "hold": 27},
           "final 99.5": {"hold": 29}}
    for k, v in exp.items():
        check(f"29 stored comparisons, {k}: tally {v} (paper, Section 7 and Appendix H)", dict(tallies[k]) == v,
              json.dumps(dict(tallies[k])))
    n_ok = sum(c["ok"] for c in checks)
    out = {"what": "rules.py and the frozen bootstrap on the stored comparisons of the paper (amendment R10-26)",
           "checks_passed": n_ok, "checks": len(checks), "all_pass": n_ok == len(checks),
           "tallies_29": {k: dict(v) for k, v in tallies.items()}, "check_list": checks, "rows": rows}
    OUT.mkdir(exist_ok=True)
    (OUT / "fidelity.json").write_text(json.dumps(out, indent=1))
    lines = ["# Fidelity check: the simulation's rule code on the stored comparisons (R10-26)", "",
             f"Result: **{n_ok} of {len(checks)} checks pass**" + (" (all)." if n_ok == len(checks) else "."), "",
             "The rule code of the simulation (`rules.py`) with the frozen bootstrap (random.choices over requests, "
             "seed 20261112, 2,000 draws), on the stored per-request answers read by the frozen loaders. Compared "
             "with the stored results in `r10/analysis/out/` (release_test.json, "
             "release_test2.json, control.json, rtest_final9.json, rtest_check_values.json) and with Tables 5, 11 "
             "and 12 of the paper (parsed from the master text).", "",
             "## 29 stored unchanged-tool comparisons (one answer per request)", "",
             "| Rule and level | Flag | Pass | Hold |", "|---|---:|---:|---:|"]
    for k, v in tallies.items():
        lines.append(f"| {k}% | {v.get('flag', 0)} | {v.get('pass', 0)} | {v.get('hold', 0)} |")
    lines += ["", "## Decisions of Tables 11 and 12", "",
              "| Comparison | Open: change [interval as run]; up / down | Specific | Original | Revised | Final (level) |",
              "|---|---|---|---|---|---|"]
    for r in rows:
        if r["table"] == "29 stored":
            continue
        cells = [f"{fmt1(ch)} [{fmt1(iv[0])}, {fmt1(iv[1])}]; {ud[0]} / {ud[1]}"
                 for ch, iv, ud in zip(r["change"], r["interval_as_run"], r["up_down"])]
        lines.append(f"| {r['name']} | {cells[0]} | {cells[1]} | {r['original']} | {r['revised']} | "
                     f"{r['final']} ({100 * r['level_final']:.2f}%) |")
    fails = [c for c in checks if not c["ok"]]
    lines += ["", "## Failed checks", ""] + ([f"- {c['check']}: {c['detail']}" for c in fails] or ["None."])
    (OUT / "fidelity.md").write_text("\n".join(lines) + "\n")
    print((OUT / "fidelity.md").read_text())
    return out


# ------------------------------------------------------------------------------------------------ tails (stored)

def tails():
    seeds = [SEED + k for k in range(20)]
    res = []
    for c in comparisons():
        diffs = [c["sets"][k] for k in ("open", "specific")]
        base = {}
        levels = {"run": c["level_run"], "final": c["level_final"], "99.5": rules.level(10)}
        per = {f"{lv}|{rule}": collections.Counter() for lv in levels for rule in ("original", "revised", "final", "orig_sym")}
        end_spread = {}
        cache = {}
        for sd in seeds + ["20000"]:
            draws = TAIL_DRAWS if sd == "20000" else DRAWS
            seed = SEED if sd == "20000" else sd
            views = [view(d, seed, draws) for d in diffs]
            cache[sd] = views
            for lv, lev in levels.items():
                for rule in ("original", "revised", "final"):
                    dcs = rules.decide_sets(views, lev, rule)[0]
                    if sd == SEED:
                        base[f"{lv}|{rule}"] = dcs
                    if sd == "20000":
                        base[f"{lv}|{rule}|20000"] = dcs
                    else:
                        per[f"{lv}|{rule}"][dcs] += 1
                dcs = rules.model_decision([rules.set_class(v["change"], *rules.endpoints(v["vals"], lev, "symmetric"))
                                            for v in views])
                if sd == SEED:
                    base[f"{lv}|orig_sym"] = dcs
                if sd != "20000":
                    per[f"{lv}|orig_sym"][dcs] += 1
        for si, k in enumerate(("open", "specific")):
            for lv, lev in levels.items():
                los = [rules.endpoints(cache[sd][si]["vals"], lev, "as_run")[0] for sd in seeds]
                his = [rules.endpoints(cache[sd][si]["vals"], lev, "as_run")[1] for sd in seeds]
                end_spread[f"{k}|{lv}"] = {"low_range": [min(los), max(los)], "high_range": [min(his), max(his)]}
        changed = {key: dict(v) for key, v in per.items() if len(v) > 1}
        changed_20000 = {key: (base[key], base[key + "|20000"]) for key in [f"{lv}|{r}" for lv in levels
                         for r in ("original", "revised", "final")] if base[key] != base[key + "|20000"]}
        changed_index = {lv: (base[f"{lv}|original"], base[f"{lv}|orig_sym"]) for lv in levels
                         if base[f"{lv}|original"] != base[f"{lv}|orig_sym"]}
        res.append({"name": c["name"], "table": c["table"], "levels": levels, "base": base,
                    "decisions_over_20_seeds": {k: dict(v) for k, v in per.items()}, "changed_by_seed": changed,
                    "changed_by_20000": changed_20000, "changed_by_index": changed_index, "end_spread": end_spread})
        print(c["name"], "seed:", changed or "-", "20000:", changed_20000 or "-", "index:", changed_index or "-", flush=True)
    out = {"what": "stored comparisons: 20 seeds with 2,000 draws, 20,000 draws, both index rules (R10-26)",
           "seeds": seeds, "rows": res}
    (OUT / "tails_stored.json").write_text(json.dumps(out, indent=1))
    lines = ["# Tails of the percentile interval on the stored comparisons (R10-26)", "",
             "Frozen bootstrap (random.choices over requests). Levels: the level as run (Tables 11 and 12: 98.75% or "
             "99.17%), the final rule's level, and 99.5%. Seeds 20261112 to 20261131 with 2,000 draws; 20,000 draws "
             "with seed 20261112. Original and revised rules: as-run index; final rule: symmetric index; "
             "orig_sym: the original rule with the symmetric index.", "",
             f"Comparisons: {len(res)}. Comparisons with a decision that changes with the seed (any rule, any level): "
             f"{sum(bool(r['changed_by_seed']) for r in res)}; with 20,000 draws: {sum(bool(r['changed_by_20000']) for r in res)}; "
             f"with the index: {sum(bool(r['changed_by_index']) for r in res)}.", "",
             "| Comparison | Level: rule | Decision (seed 20261112) | Decisions over 20 seeds | 20,000 draws |",
             "|---|---|---|---|---|"]
    for r in res:
        keys = sorted(set(r["changed_by_seed"]) | set(r["changed_by_20000"]))
        for key in keys:
            lv, rule = key.split("|")
            lines.append(f"| {r['name']} | {lv} ({100 * r['levels'][lv]:.2f}%): {rule} | {r['base'][key]} | "
                         f"{json.dumps(r['decisions_over_20_seeds'][key])} | "
                         f"{r['base'].get(key + '|20000', '-')} |")
    lines += ["", "Decisions that change with the index rule (seed 20261112, 2,000 draws; original rule):", ""]
    lines += [f"- {r['name']}: {json.dumps(r['changed_by_index'])}" for r in res if r["changed_by_index"]] or ["- none"]
    lines += ["", "Range of the as-run interval ends over the 20 seeds, Table 11 and 12 comparisons at 99.5% (points):", "",
              "| Comparison | Open low | Open high | Specific low | Specific high |", "|---|---|---|---|---|"]
    for r in res:
        if r["table"] == "29 stored":
            continue
        e = r["end_spread"]
        f2 = lambda x: f"{x[0]:+.2f} to {x[1]:+.2f}"  # noqa: E731
        lines.append(f"| {r['name']} | {f2(e['open|99.5']['low_range'])} | {f2(e['open|99.5']['high_range'])} | "
                     f"{f2(e['specific|99.5']['low_range'])} | {f2(e['specific|99.5']['high_range'])} |")
    (OUT / "tails_stored.md").write_text("\n".join(lines) + "\n")
    print((OUT / "tails_stored.md").read_text())


TAIL_DRAWS = 20000

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "fit":
        fit()
    elif cmd == "fidelity":
        fidelity()
    elif cmd == "tails":
        tails()
    else:
        sys.exit("Usage: python3 -I stored.py fit | fidelity | tails")
