"""Offline tests of r10/release.py (amendment R10-6): the acceptance rule, rule P, the reverse map and the requests.
No network call, no key.

Usage (from explore/): .venv/bin/python -I r10/tests/test_release.py
"""
import copy
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
R10 = HERE.parent
sys.path.insert(0, str(R10))
import release  # noqa: E402
import tools  # noqa: E402


def answer(tool, value_map):
    return {"tool": tool, "value_map": value_map}


def base():
    return copy.deepcopy(release.original())


def invalid(obj, words):
    try:
        release.accept_obj(obj)
    except release.Invalid as e:
        assert words in str(e), (words, str(e))
        return
    raise AssertionError(f"accepted, but expected Invalid with {words!r}")


def renamed():
    """type -> property_type with hotel -> full_service_hotel; pricerange -> price_range (values kept)."""
    t = base()
    props = t["input_schema"]["properties"]
    ty = props.pop("type")
    ty["anyOf"][2]["items"]["enum"] = ["guesthouse", "full_service_hotel"]
    pr = props.pop("pricerange")
    props["price_range"], props["property_type"] = pr, ty
    t["input_schema"]["required"] = list(props)
    t["description"] = "Find places to stay in Cambridge that match the traveller's stated needs."
    return answer(t, {"type": {"hotel": "full_service_hotel", "guesthouse": "guesthouse", "any": "any"},
                      "pricerange": {"cheap": "cheap"}})


def test_identity():
    params, values = release.accept_obj(answer(base(), {}))
    assert params == {p: p for p in release.original()["input_schema"]["properties"]}
    assert values["type"] == {'"any"': "any", '"guesthouse"': "guesthouse", '"hotel"': "hotel"}
    print("ok test_identity")


def test_rename():
    params, values = release.accept_obj(renamed())
    assert params["type"] == "property_type" and params["pricerange"] == "price_range", params
    assert values["type"]['"hotel"'] == "full_service_hotel"
    print("ok test_rename")


def test_rejects():
    t = base()
    t["name"] = "find_hotels"
    invalid(answer(t, {}), "tool name")
    t = base()
    t["input_schema"]["properties"]["area"]["description"] = "Part of the city."
    t["input_schema"]["properties"]["area"]["default"] = None
    invalid(answer(t, {}), "keyword 'default'")
    t = base()
    t["input_schema"]["properties"]["type"]["anyOf"].pop(1)  # "any" dropped
    invalid(answer(t, {}), "parameter type")
    t = base()
    del t["input_schema"]["properties"]["parking"]
    t["input_schema"]["required"].remove("parking")
    invalid(answer(t, {}), "parameters instead of")
    t = base()  # two options merged
    invalid(answer(t, {"stars": {"0": "1"}}), "parameter stars")
    t = base()  # parking and internet both renamed with the same values: not explicit
    props = t["input_schema"]["properties"]
    props["has_parking"], props["has_wifi"] = props.pop("parking"), props.pop("internet")
    t["input_schema"]["required"] = list(props)
    invalid(answer(t, {}), "not explicit")
    invalid({"tool": base()}, "keys")
    print("ok test_rejects")


def test_explicit_by_values():
    """parking and internet renamed, but value_map gives them different new values: the mapping is explicit."""
    t = base()
    props = t["input_schema"]["properties"]
    park, net = props.pop("parking"), props.pop("internet")
    park["anyOf"][2]["items"]["enum"] = ["parking_yes", "parking_no"]
    net["anyOf"][2]["items"]["enum"] = ["wifi_yes", "wifi_no"]
    props["has_parking"], props["has_wifi"] = park, net
    t["input_schema"]["required"] = list(props)
    params, _ = release.accept_obj(answer(t, {"parking": {"yes": "parking_yes", "no": "parking_no"},
                                              "has_wifi": {"yes": "wifi_yes", "no": "wifi_no"}}))
    assert params["parking"] == "has_parking" and params["internet"] == "has_wifi", params
    print("ok test_explicit_by_values")


def test_reverse_and_parse():
    obj = renamed()
    params, values = release.accept_obj(obj)
    saved = dict(release._edit)
    release._edit.clear()
    release._edit.update(obj=obj, params=params, values=values,
                         rev={p: {release.key(n): json.loads(k) for k, n in m.items()} for p, m in values.items()})
    try:
        row = {"tool_calls": [{"name": "search_hotels", "input": {
            "name": "null", "area": ["centre"], "price_range": "any", "stars": None,
            "property_type": ["full_service_hotel"], "parking": None, "internet": ["yes"]}}]}
        kind, f = release.parse_call(row, "tedit")
        assert kind == "search" and f["type"] == ("hotel",) and f["pricerange"] == "any" and f["name"] is None, f
        row["tool_calls"][0]["input"]["property_type"] = ["guesthouse", "full_service_hotel"]
        assert release.parse_call(row, "tedit")[1]["type"] == ("guesthouse", "hotel")
        assert release.parse_call({"tool_calls": [], "text": "hi"}, "tedit")[0] == "none"
        assert release.parse_call({"tool_calls": [{"name": "other", "input": {}}]}, "tedit")[0] == "invalid"
        # t0 is tools.parse_call unchanged
        t0 = {"tool_calls": [{"name": "search_hotels", "input": {"type": ["hotel"]}}]}
        assert release.parse_call(t0, "t0") == tools.parse_call(t0, "t0")
    finally:
        release._edit.clear()
        release._edit.update(saved)
    print("ok test_reverse_and_parse")


def test_request_text():
    user = release.rewrite_user()
    assert user.startswith(release.REWRITE_TEXT + "\n\n{")
    assert json.loads(user[len(release.REWRITE_TEXT) + 2:]) == release.original()
    req = release.rewrite_request()["params"]
    assert req["model"] == "claude-opus-5-5" and req["output_config"] == {"effort": "low"}
    assert "system" not in req and "tools" not in req and "thinking" not in req
    print("ok test_request_text")


def test_analysis_rule():
    """release_analyze on made-up reads (no model answer): the paper's examples, a large drop, and no change."""
    sys.path.insert(0, str(R10 / "analysis"))
    import release_analyze as ra
    assert ra.decide(-13.0, -16.0, -10.1, 5) == "flag-worthy" and ra.decide(0.9, -0.3, 2.1, 5) == "absent"
    assert ra.decide(-2.0, -6.0, 1.0, 5) == "unresolved"
    assert ra.release((0.9, -0.3, 2.1), (0.7, -2.7, 4.0), 5, 1, 1) == "pass"
    assert ra.release((0.9, -0.3, 2.1), (-2.0, -9.0, 4.0), 5, 1, 1) == "hold"
    assert abs(ra.LEVEL - 0.9875) < 1e-12
    import runs
    import gold
    data, g = runs.context()
    sets, db = ra.request_sets(data, g), gold.hotel_db()
    hotel = ("search", {"type": ("hotel",)})
    empty = ("search", {"type": None})
    drop = {}
    for d in sets["open"] + sets["specific"]:
        drop[(d, "t0")], drop[(d, "tedit")] = [hotel], [empty]
    res = ra.analyse(drop, sets, data, db)
    assert res["sets"]["open"]["change"] == -100 and res["sets"]["open"]["decision"] == "flag-worthy"
    assert res["release"] == "flag" and res["trade"]["defined"]
    same = {}
    for d in sets["open"] + sets["specific"]:
        same[(d, "t0")] = same[(d, "tedit")] = [empty]
    res = ra.analyse(same, sets, data, db)
    assert res["sets"]["specific"]["interval"] == [0, 0] and res["release"] == "pass"
    print("ok test_analysis_rule")


def main():
    test_analysis_rule()
    test_identity()
    test_rename()
    test_rejects()
    test_explicit_by_values()
    test_reverse_and_parse()
    test_request_text()
    if release.EDIT.exists():  # after the rewrite step: the frozen edit passes the rule, and the requests build
        import runs
        for name in ("erp_sonnet", "erp_sol"):
            if name in runs.RUNS:
                reqs = runs.requests(name)
                assert len(reqs) == 2 * 554 and {r["cell"] for r in reqs} == {"t0", "tedit"}
        print("ok frozen edit")


if __name__ == "__main__":
    main()
