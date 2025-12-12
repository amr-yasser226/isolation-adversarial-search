from __future__ import annotations
import os

from game.state import GameState
from agents.alphabeta_agent import AlphaBetaAgent
from agents.random_agent import RandomAgent
from visualization.board_plot import save_board_image

def play_game(out_dir: str = "figures/demo", plies: int = 30) -> None:
    os.makedirs(out_dir, exist_ok=True)

    # Demo matchup (change as you like)
    agent_a = AlphaBetaAgent(depth=3, use_ordering=True)
    agent_b = RandomAgent(seed=0)

    state = GameState.new()
    save_board_image(state.board, f"{out_dir}/move_00.png", title="Initial State")

    for ply in range(1, plies + 1):
        if state.is_terminal():
            break

        agent = agent_a if state.active_player == 1 else agent_b
        info = agent.choose_move(state)

        mover = state.active_player  # who is about to move
        state = state.apply_move(info["move"])

        title = (
            f"Ply {ply} | Player {'A' if mover == 1 else 'B'} -> {info['move']} | "
            f"depth={info['depth']} nodes={info['nodes']}"
        )
        save_board_image(state.board, f"{out_dir}/move_{ply:02d}.png", title=title)

    w = state.winner()
    if w is None:
        print("No winner (max plies reached).")
    else:
        print("Winner:", "A" if w == 1 else "B")

if __name__ == "__main__":
    play_game()