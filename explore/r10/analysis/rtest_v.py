"""Verbatim extract of the independent check script workshops/proposals-verified/verify.py: the names that the post hoc scripts
rtest_c1.py, rtest_levels.py and rtest_symmetric.py use (AA, boot_three_point, gold, mean, na, ra, runs, sign_p, stats, tool_reads), with every module-level name that they need,
and the paths of the study folder. The checks of that script are not here. No model call, no network call.
"""
import ast
import collections
import functools
import csv
import datetime
import hashlib
import itertools
import json
import math
import pathlib
import random
import re
import statistics
import sys
HERE = pathlib.Path(__file__).resolve().parent  # explore/r10/analysis
EXPLORE = HERE.parents[1]
for sub in ("lib", "forms", "pmain", "r9", "r9/natural", "r9/additions", "r9/free", "r10", "r10/analysis"):
    sys.path.insert(0, str(EXPLORE / sub))
import b_analyze as B
import briefsearch as bs
import clear_rule as cr
import gold
import natural
import natural_analyze as na
import release
import release_analyze as ra
import runs
import stats
import steer
import steer2
import tools
CUT = {"max_tokens", "length", "incomplete", "max_output_tokens"}
_ROWS = {}


def raw_rows(folder, name="raw.jsonl"):
    assert not folder.startswith("em"), f"refused: {folder}"
    key = (folder, name)
    if key not in _ROWS:
        path = EXPLORE / folder / name
        _ROWS[key] = [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else None
    return _ROWS[key]


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def sign_p(up, down):
    """Two-sided exact binomial (sign) test, ties dropped."""
    n, k = up + down, min(up, down)
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def parse_tool(row, cell):
    if cell in ("t0", "trep", "tord"):
        return tools.parse_call(row, "t0")
    if cell == "t1":
        return tools.parse_call(row, "t1")
    if cell == "tedit":
        return release.parse_call(row, "tedit")
    if cell in ("th", "tg"):
        return steer.parse_call(row, cell)
    return steer2.parse_call(row, cell)


def score_tool(row, cell):
    """1 / 0 for a valid read (search whose type holds hotel / valid answer without a hotel search), None if invalid."""
    if row.get("type") != "succeeded" or row.get("stop") in CUT:
        return None
    kind, val = parse_tool(row, cell)
    if kind == "none":
        return 0
    if kind != "search":
        return None
    return int(na.hotel(val.get("type")))


def tool_reads(folders, cell, read):
    """{dialogue.json: [score, ...]} of the valid reads, in read order; read None = every read."""
    out = collections.defaultdict(list)
    for f in folders:
        for row in raw_rows(f):
            _, d, c, n = row["custom_id"].split("-")
            if c != cell or (read is not None and int(n) != read):
                continue
            s = score_tool(row, c)
            if s is not None:
                out[d + ".json"].append((int(n), s))
    return {d: [s for _, s in sorted(v)] for d, v in out.items()}
AA = {
    "sonnet": [("era1 read 1", ("era1_sonnet",), "t0", 1, 1), ("era1 read 2", ("era1_sonnet",), "t0", 2, 2),
               ("fill read 3", ("erx_a1_sonnet", "erx_a2_sonnet"), "t0", 3, 3), ("erp", ("erp_sonnet",), "t0", 1, 1)],
    "haiku": [("era1 read 1", ("era1_haiku",), "t0", 1, 1), ("era1 read 2", ("era1_haiku",), "t0", 2, 2),
              ("erm", ("erm_haiku",), "t0", 1, 1), ("ers", ("ers_haiku",), "t0", 1, 1),
              ("erc", ("erc_haiku",), "t0", 1, None), ("erc2", ("erc2_haiku",), "trep", 1, None)],
    "sol": [("era1 read 1", ("era1_sol",), "t0", 1, 1), ("era1 read 2", ("era1_sol",), "t0", 2, 2),
            ("fill read 3", ("erx_a3_sol",), "t0", 3, 3), ("erp", ("erp_sol",), "t0", 1, 1)],
    "opus": [("era1 read 1", ("era1_opus",), "t0", 1, 1), ("fill read 2", ("erx_a2_opus",), "t0", 2, 2)],
    "luna": [("era1 read 1", ("era1_luna",), "t0", 1, 1), ("era1 read 2", ("era1_luna",), "t0", 2, 2)],
}


def boot_three_point(n, up, down, draws, rng, level):
    """Percentile bootstrap of the mean of n values in {-100, 0, +100} (up, down counts), with the index rule of
    stats.percentile. Resampling counts come from binomial draws: the same distribution as resampling units."""
    pu, pd = up / n, down / n
    vals = []
    for _ in range(draws):
        U = rng.binomialvariate(n, pu) if pu > 0 else 0
        rest = n - U
        q = min(1.0, pd / (1 - pu)) if pu < 1 else 0.0
        D = rng.binomialvariate(rest, q) if rest and q > 0 else 0
        vals.append(100 * (U - D) / n)
    vals.sort()
    a = (1 - level) / 2
    return stats.percentile(vals, a), stats.percentile(vals, 1 - a)
