from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any

from game.state import GameState

Move = Tuple[int, int]

@dataclass
class MoveLog:
    ply: int
    player: int
    move: Move
    value: float
    depth: int
    time_s: float
    nodes: int
    cutoffs: int

@dataclass
class MatchResult:
    winner: Optional[int]
    moves: List[MoveLog] = field(default_factory=list)
    final_state: Optional[GameState] = None

def play_match(agent_a, agent_b, state: Optional[GameState] = None, max_plies: int = 200) -> MatchResult:
    s = state if state is not None else GameState.new()
    logs: List[MoveLog] = []

    for ply in range(max_plies):
        if s.is_terminal():
            break

        agent = agent_a if s.active_player == 1 else agent_b
        info = agent.choose_move(s)

        s = s.apply_move(info["move"])
        logs.append(MoveLog(
            ply=ply,
            player=-s.active_player,  # the player who just moved
            move=info["move"],
            value=info["value"],
            depth=info["depth"],
            time_s=info["time_s"],
            nodes=info["nodes"],
            cutoffs=info.get("cutoffs", 0),
        ))

    return MatchResult(winner=s.winner(), moves=logs, final_state=s)