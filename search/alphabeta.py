from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Callable, Optional, Tuple, Any, List, Set

from search.stats import SearchStats, SearchContext, SearchLimitReached

EvalFn = Callable[[Any, int], float]

@dataclass
class SearchTrace:
    edges: List[tuple] = field(default_factory=list)         # explored edges (parent_id, child_id)
    pruned_edges: Set[tuple] = field(default_factory=set)    # edges cut by pruning

def _order_moves(state, moves, eval_fn: EvalFn, root_player: int) -> list:
    # Heuristic ordering for better pruning: sort by eval of child states.
    maximizing = (state.active_player == root_player)
    scored = []
    for m in moves:
        child = state.apply_move(m)
        scored.append((eval_fn(child, root_player), m))
    scored.sort(reverse=maximizing, key=lambda x: x[0])
    return [m for _, m in scored]

def alphabeta(
    state,
    depth: int,
    alpha: float,
    beta: float,
    eval_fn: EvalFn,
    root_player: int,
    stats: Optional[SearchStats] = None,
    ctx: Optional[SearchContext] = None,
    tt: Optional[dict] = None,
    use_ordering: bool = True,
    trace: Optional[SearchTrace] = None,
    node_id: str = "R",
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
    if use_ordering:
        moves = _order_moves(state, moves, eval_fn, root_player)

    if maximizing:
        value = float("-inf")
        for i, m in enumerate(moves):
            child_id = f"{node_id}.{i}"
            if trace is not None:
                trace.edges.append((node_id, child_id))

            v, _ = alphabeta(
                state.apply_move(m), depth - 1, alpha, beta, eval_fn, root_player,
                stats=stats, ctx=ctx, tt=tt, use_ordering=use_ordering, trace=trace, node_id=child_id
            )
            if v > value or best_move is None:
                value, best_move = v, m
            alpha = max(alpha, value)
            if alpha >= beta:
                stats.cutoffs += 1
                if trace is not None:
                    # mark remaining siblings as pruned
                    for j in range(i + 1, len(moves)):
                        trace.pruned_edges.add((node_id, f"{node_id}.{j}"))
                break
    else:
        value = float("inf")
        for i, m in enumerate(moves):
            child_id = f"{node_id}.{i}"
            if trace is not None:
                trace.edges.append((node_id, child_id))

            v, _ = alphabeta(
                state.apply_move(m), depth - 1, alpha, beta, eval_fn, root_player,
                stats=stats, ctx=ctx, tt=tt, use_ordering=use_ordering, trace=trace, node_id=child_id
            )
            if v < value or best_move is None:
                value, best_move = v, m
            beta = min(beta, value)
            if beta <= alpha:
                stats.cutoffs += 1
                if trace is not None:
                    for j in range(i + 1, len(moves)):
                        trace.pruned_edges.add((node_id, f"{node_id}.{j}"))
                break

    out = (value, best_move)
    if tt is not None and key is not None:
        tt[key] = out
    return out

def iterative_deepening_alphabeta(state, max_depth: int, eval_fn: EvalFn, time_budget_s: float, use_ordering: bool = True, use_tt: bool = False) -> dict:
    root = state.active_player
    t0 = time.perf_counter()
    deadline = t0 + time_budget_s

    best = {"move": None, "value": float("-inf"), "depth": 0, "time_s": 0.0, "nodes": 0, "cutoffs": 0}
    tt = {} if use_tt else None

    for d in range(1, max_depth + 1):
        stats = SearchStats()
        ctx = SearchContext(time_deadline=deadline)
        try:
            val, mv = alphabeta(
                state, d, float("-inf"), float("inf"), eval_fn, root,
                stats=stats, ctx=ctx, tt=tt, use_ordering=use_ordering
            )
            best = {"move": mv, "value": val, "depth": d, "time_s": time.perf_counter() - t0, "nodes": stats.nodes, "cutoffs": stats.cutoffs}
        except SearchLimitReached:
            break

    return best