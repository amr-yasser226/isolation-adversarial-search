from __future__ import annotations

import time
from typing import Any

from agents.base import Agent
from search.alphabeta import alphabeta, iterative_deepening_alphabeta
from search.stats import SearchStats
from search.evaluation import mobility_heuristic


def _normalize_search_info(info: Any, *, default_depth: int, default_cutoffs: int = 0) -> dict:
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


class AlphaBetaAgent(Agent):
    def __init__(
        self,
        depth: int = 3,
        time_budget_s: float | None = None,
        use_ordering: bool = True,
        use_tt: bool = False,
    ):
        self.depth = depth
        self.time_budget_s = time_budget_s
        self.use_ordering = use_ordering
        self.use_tt = use_tt
        self.name = (
            f"AlphaBeta(d={depth}"
            + (f", t={time_budget_s}s" if time_budget_s else "")
            + f", ord={use_ordering}, tt={use_tt})"
        )

    def choose_move(self, state):
        eval_fn = mobility_heuristic

        # Iterative deepening under a time budget
        if self.time_budget_s is not None:
            info = iterative_deepening_alphabeta(
                state,
                self.depth,
                eval_fn,
                self.time_budget_s,
                use_ordering=self.use_ordering,
                use_tt=self.use_tt,
            )
            return _normalize_search_info(info, default_depth=self.depth, default_cutoffs=0)

        # Fixed depth
        root = state.active_player
        stats = SearchStats()
        t0 = time.perf_counter()
        val, mv = alphabeta(
            state,
            self.depth,
            float("-inf"),
            float("inf"),
            eval_fn,
            root,
            stats=stats,
            use_ordering=self.use_ordering,
            tt=({} if self.use_tt else None),
        )
        return {
            "move": mv,
            "value": val,
            "depth": self.depth,
            "time_s": time.perf_counter() - t0,
            "nodes": stats.nodes,
            "cutoffs": stats.cutoffs,
        }