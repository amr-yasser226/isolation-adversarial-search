from __future__ import annotations

import time

from agents.base import Agent
from agents.utils import normalize_search_info
from search.minimax import minimax, iterative_deepening_minimax
from search.stats import SearchStats
from search.evaluation import mobility_heuristic


class MinimaxAgent(Agent):
    def __init__(self, depth: int = 3, time_budget_s: float | None = None):
        self.depth = depth
        self.time_budget_s = time_budget_s
        self.name = f"Minimax(d={depth}" + (f", t={time_budget_s}s)" if time_budget_s else ")")

    def choose_move(self, state):
        eval_fn = mobility_heuristic

        # Iterative deepening under a time budget
        if self.time_budget_s is not None:
            info = iterative_deepening_minimax(state, self.depth, eval_fn, self.time_budget_s)
            return normalize_search_info(info, default_depth=self.depth)

        # Fixed depth
        root = state.active_player
        stats = SearchStats()
        t0 = time.perf_counter()
        val, mv = minimax(state, self.depth, eval_fn, root, stats=stats)
        return {
            "move": mv,
            "value": val,
            "depth": self.depth,
            "time_s": time.perf_counter() - t0,
            "nodes": stats.nodes,
            "cutoffs": 0,
        }