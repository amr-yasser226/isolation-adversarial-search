from __future__ import annotations

import time

from game.state import GameState
from search.minimax import minimax
from search.alphabeta import alphabeta
from search.evaluation import mobility_heuristic
from search.stats import SearchStats


def benchmark(depth: int = 3) -> None:
    s = GameState.new()
    root = s.active_player

    mm_stats = SearchStats()
    t0 = time.perf_counter()
    mm_val, mm_move = minimax(s, depth, mobility_heuristic, root_player=root, stats=mm_stats)
    t1 = time.perf_counter()

    ab_stats = SearchStats()
    t2 = time.perf_counter()
    ab_val, ab_move = alphabeta(
        s,
        depth,
        float("-inf"),
        float("inf"),
        mobility_heuristic,
        root_player=root,
        stats=ab_stats,
        use_ordering=False,  # keep fair / controlled
    )
    t3 = time.perf_counter()

    print(f"Depth = {depth}")
    print(f"Minimax:   move={mm_move}, value={mm_val}, time={t1-t0:.6f}s, nodes={mm_stats.nodes}")
    print(f"AlphaBeta: move={ab_move}, value={ab_val}, time={t3-t2:.6f}s, nodes={ab_stats.nodes}, cutoffs={ab_stats.cutoffs}")


if __name__ == "__main__":
    benchmark(depth=3)