from __future__ import annotations
from typing import List, Tuple

DIRECTIONS: List[Tuple[int, int]] = [
    (-1, 0), (1, 0),
    (0, -1), (0, 1),
    (-1, -1), (-1, 1),
    (1, -1), (1, 1),
]

def queen_moves(board, r: int, c: int) -> List[Tuple[int, int]]:
    """All reachable squares in 8 directions until blocked."""
    out: List[Tuple[int, int]] = []
    for dr, dc in DIRECTIONS:
        nr, nc = r + dr, c + dc
        while board.is_free(nr, nc):
            out.append((nr, nc))
            nr += dr
            nc += dc
    return out