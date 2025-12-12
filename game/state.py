from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple

from game.board import Board
from game.moves import queen_moves

Pos = Tuple[int, int]

@dataclass
class GameState:
    board: Board
    p1_pos: Optional[Pos] = None
    p2_pos: Optional[Pos] = None
    active_player: int = 1  # 1 => A, -1 => B

    @staticmethod
    def new(rows: int = 6, cols: int = 6) -> "GameState":
        return GameState(Board(rows, cols))

    def clone(self) -> "GameState":
        return GameState(
            board=self.board.clone(),
            p1_pos=self.p1_pos,
            p2_pos=self.p2_pos,
            active_player=self.active_player,
        )

    def key(self) -> tuple:
        """Hashable key for caching (TT)."""
        return (self.active_player, self.p1_pos, self.p2_pos, self.board.key())

    def player_pos(self, player: int) -> Optional[Pos]:
        return self.p1_pos if player == 1 else self.p2_pos

    def set_player_pos(self, player: int, pos: Pos) -> None:
        if player == 1:
            self.p1_pos = pos
        else:
            self.p2_pos = pos

    def legal_moves_for(self, player: int) -> List[Pos]:
        pos = self.player_pos(player)
        if pos is None:
            return [(r, c) for r in range(self.board.rows) for c in range(self.board.cols) if self.board.is_free(r, c)]
        return queen_moves(self.board, pos[0], pos[1])

    def legal_moves(self) -> List[Pos]:
        return self.legal_moves_for(self.active_player)

    def apply_move(self, move: Pos) -> "GameState":
        if move not in self.legal_moves():
            raise ValueError(f"Illegal move {move} for player {self.active_player}")

        ns = self.clone()
        old = ns.player_pos(ns.active_player)

        # Leaving a cell blocks it (Isolation rule)
        if old is not None:
            ns.board.block_cell(old[0], old[1])

        symbol = "A" if ns.active_player == 1 else "B"
        ns.board.place_player(move[0], move[1], symbol)
        ns.set_player_pos(ns.active_player, move)

        ns.active_player *= -1
        return ns

    def is_terminal(self) -> bool:
        return len(self.legal_moves()) == 0

    def winner(self) -> Optional[int]:
        """Return 1 or -1 if terminal, else None."""
        if not self.is_terminal():
            return None
        return -self.active_player  # player-to-move has no moves => loses

    def __str__(self) -> str:
        return str(self.board)