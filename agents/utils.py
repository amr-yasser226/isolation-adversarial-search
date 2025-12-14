from __future__ import annotations

from typing import Any


def normalize_search_info(info: Any, *, default_depth: int, default_cutoffs: int = 0) -> dict:
    """
    Normalize outputs so the rest of the codebase can always rely on:
    {move, value, depth, time_s, nodes, cutoffs}
    """
    if not isinstance(info, dict):
        raise TypeError(f"Expected dict from search routine, got {type(info).__name__}")

    out = dict(info)

    # depth reached (iterative deepening) or fixed depth
    if "depth" not in out or out["depth"] is None:
        if "reached_depth" in out and out["reached_depth"] is not None:
            out["depth"] = int(out["reached_depth"])
        elif "max_depth" in out and out["max_depth"] is not None:
            out["depth"] = int(out["max_depth"])
        else:
            out["depth"] = int(default_depth)

    # time field normalization
    if "time_s" not in out and "time" in out:
        out["time_s"] = out["time"]

    # required numeric fields
    out.setdefault("time_s", 0.0)
    out.setdefault("nodes", 0)
    out.setdefault("cutoffs", default_cutoffs)

    return out
