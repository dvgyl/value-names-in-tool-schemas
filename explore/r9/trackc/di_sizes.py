"""Write pilot.json of the DeepInfra runs that read MultiWOZ dialogues (X2 natural, B1 to B4). Offline.

The sizes come from the natural answers of P (ep_di) and P2 (ep_di2, when it has rows). panel.write_sizes keeps a
DeepInfra row only as deepinfra_settings.projected gives it: a row with thinking on gives no size, and an answer that ran
to the old cap of 4,000 tokens counts at the new cap. A cell without a row keeps the planning size of its run.
ex2c_di and ex2s_di write their own pilot.json in their estimate step (ep.sizes).
Usage: python3 -I r9/trackc/di_sizes.py, then the estimate step of each run.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ep  # noqa: E402
import ep_di2  # noqa: E402
import panel  # noqa: E402
from panel import ds, oc  # noqa: E402

FOLDERS = ("ex2n_di", "eb1_di", "eb2_open", "eb3_open", "eb4_open")


def measured():
    """(cell key, estimated input, raw.jsonl row) of every natural answer of P and P2, keyed by the settings now."""
    sources = (("ep_di", ep.cells("deepinfra"), lambda m: ds.MODELS[m.id]),
               ("ep_di2", ep_di2.cells(), lambda m: ep_di2.SETTINGS[m.short]))
    out = []
    for folder, cells, settings in sources:
        got = panel.rows(folder)
        for cid, task, m, p in cells:
            if task == "nat" and cid in got:
                req = ds.request(settings(m), cid, p.user, p.system, p.schema)
                out.append(("|".join(oc.cell(req)), oc.est_in(req), got[cid]))
    return out


def main():
    rows = measured()
    for name in FOLDERS:
        cells = panel.write_sizes(name, rows, "natural answers of ep_di and ep_di2 raw.jsonl")
        print(f"{name}: measured cells {sorted(cells)}")


if __name__ == "__main__":
    main()
