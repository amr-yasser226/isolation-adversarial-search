from __future__ import annotations
import math

def terminal_utility(state, root_player: int) -> float:
    if not state.is_terminal():
        return 0.0
    w = state.winner()
    if w is None:
        return 0.0
    return math.inf if w == root_player else -math.inf

def mobility_heuristic(state, root_player: int) -> float:
    """Simple, standard Isolation heuristic."""
    if state.is_terminal():
        return terminal_utility(state, root_player)
    my_moves = len(state.legal_moves_for(root_player))
    opp_moves = len(state.legal_moves_for(-root_player))
    return float(my_moves - opp_moves)