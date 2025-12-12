from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Board:
    rows: int = 6
    cols: int = 6

    def __post_init__(self) -> None:
        self.grid: List[List[str]] = [["." for _ in range(self.cols)] for _ in range(self.rows)]

    def is_free(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c] == "."

    def place_player(self, r: int, c: int, symbol: str) -> None:
        if not self.is_free(r, c):
            raise ValueError(f"Cannot place {symbol} at {(r, c)}; cell not free.")
        self.grid[r][c] = symbol

    def block_cell(self, r: int, c: int) -> None:
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise ValueError(f"Out of bounds: {(r, c)}")
        self.grid[r][c] = "X"

    def clone(self) -> "Board":
        b = Board(self.rows, self.cols)
        b.grid = [row[:] for row in self.grid]
        return b

    def key(self) -> Tuple[str, ...]:
        """Immutable representation for hashing/caching."""
        return tuple("".join(row) for row in self.grid)

    def __str__(self) -> str:
        return "\n".join(" ".join(row) for row in self.grid)