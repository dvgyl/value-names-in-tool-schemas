"""The loaders of the independent check script (workshops/proposals-verified/verify.py) that the post hoc
scripts repair_refs.py, repair_rule.py and repair_limits.py use: the import block, raw_rows and gots, copied
verbatim with the paths of the study folder. The checks of verify.py are not here.
No model call, no network call. raw_rows refuses a folder whose name starts with "em".
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
import b_analyze as B  # noqa: E402
import briefsearch as bs  # noqa: E402
import clear_rule as cr  # noqa: E402
import gold  # noqa: E402
import natural  # noqa: E402
import natural_analyze as na  # noqa: E402
import release  # noqa: E402
import release_analyze as ra  # noqa: E402
import runs  # noqa: E402
import stats  # noqa: E402
import steer  # noqa: E402
import steer2  # noqa: E402
import tools  # noqa: E402

_ROWS = {}


def raw_rows(folder, name="raw.jsonl"):
    assert not folder.startswith("em"), f"refused: {folder}"
    key = (folder, name)
    if key not in _ROWS:
        path = EXPLORE / folder / name
        _ROWS[key] = [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else None
    return _ROWS[key]



def gots(data, group_of):
    out = {}
    for m in B.SOURCES:
        got, missing = B.load(m, data, group_of)
        assert not missing, missing
        out[m] = got
    for m in ("deepseek", "qwen", "gemma"):
        got = {}
        for row in raw_rows(f"ery_{m}"):
            d, arm, read = B.split(row["custom_id"])
            got[(d, arm, read)] = B.parse_row(row, arm, None)
        out[m] = got
    return out

