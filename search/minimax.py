from __future__ import annotations
import time
from typing import Callable, Optional, Tuple, Dict, Any

from search.stats import SearchStats, SearchContext, SearchLimitReached

EvalFn = Callable[[Any, int], float]

def minimax(
    state,
    depth: int,
    eval_fn: EvalFn,
    root_player: int,
    stats: Optional[SearchStats] = None,
    ctx: Optional[SearchContext] = None,
    tt: Optional[dict] = None,
) -> Tuple[float, Optional[tuple]]:
    if stats is None:
        stats = SearchStats()

    stats.nodes += 1
    if ctx is not None:
        ctx.check(stats, time.perf_counter())

    if depth == 0 or state.is_terminal():
        return eval_fn(state, root_player), None

    key = None
    if tt is not None:
        key = (state.key(), depth, root_player)
        if key in tt:
            return tt[key]

    maximizing = (state.active_player == root_player)
    best_move = None

    moves = state.legal_moves()
    if maximizing:
        best_val = float("-inf")
        for m in moves:
            v, _ = minimax(state.apply_move(m), depth - 1, eval_fn, root_player, stats, ctx, tt)
            if v > best_val:
                best_val, best_move = v, m
    else:
        best_val = float("inf")
        for m in moves:
            v, _ = minimax(state.apply_move(m), depth - 1, eval_fn, root_player, stats, ctx, tt)
            if v < best_val:
                best_val, best_move = v, m

    out = (best_val, best_move)
    if tt is not None and key is not None:
        tt[key] = out
    return out

def iterative_deepening_minimax(state, max_depth: int, eval_fn: EvalFn, time_budget_s: float) -> dict:
    root = state.active_player
    stats_total = SearchStats()
    t0 = time.perf_counter()
    deadline = t0 + time_budget_s

    best = {"move": None, "value": float("-inf"), "depth": 0, "time_s": 0.0, "nodes": 0, "cutoffs": 0}

    for d in range(1, max_depth + 1):
        stats = SearchStats()
        ctx = SearchContext(time_deadline=deadline)
        try:
            val, mv = minimax(state, d, eval_fn, root, stats=stats, ctx=ctx, tt=None)
            best = {"move": mv, "value": val, "depth": d, "time_s": time.perf_counter() - t0, "nodes": stats.nodes, "cutoffs": 0}
        except SearchLimitReached:
            break

    return best