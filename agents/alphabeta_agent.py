from __future__ import annotations

import time

from agents.base import Agent
from agents.utils import normalize_search_info
from search.alphabeta import alphabeta, iterative_deepening_alphabeta
from search.stats import SearchStats
from search.evaluation import mobility_heuristic


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
            return normalize_search_info(info, default_depth=self.depth, default_cutoffs=0)

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