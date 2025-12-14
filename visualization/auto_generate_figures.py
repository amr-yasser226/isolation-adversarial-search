from __future__ import annotations

import os

from game.state import GameState
from agents.random_agent import RandomAgent
from agents.alphabeta_agent import AlphaBetaAgent
from visualization.board_plot import save_board_image

from experiments.run_setups import setup_A, setup_B, setup_C, setup_D, setup_E


def generate_game_snapshots(agent_a, agent_b, plies: int, out_dir: str, prefix: str) -> None:
    os.makedirs(out_dir, exist_ok=True)

    s = GameState.new()
    save_board_image(s.board, f"{out_dir}/{prefix}_00.png", title="Initial State")

    for ply in range(1, plies + 1):
        if s.is_terminal():
            break

        agent = agent_a if s.active_player == 1 else agent_b
        info = agent.choose_move(s)

        mover = s.active_player
        s = s.apply_move(info["move"])

        title = (
            f"Ply {ply} | Player {'A' if mover == 1 else 'B'} moved to {info['move']} | "
            f"depth={info['depth']} nodes={info['nodes']}"
        )
        save_board_image(s.board, f"{out_dir}/{prefix}_{ply:02d}.png", title=title)


def auto_generate(out_dir: str = "figures") -> None:
    os.makedirs(out_dir, exist_ok=True)

    # Run all experiment setups (A/B/C/D/E) and generate charts + a pruned-tree figure.
    setup_A(depth=3, n_states=12, plies=6, seed=0, out_dir=out_dir)
    setup_B(time_budget_s=0.05, max_depth=8, games=10, seed=0, out_dir=out_dir)  # saves setupB_depth.png
    setup_C(depth=3, games=20, seed=0, out_dir=out_dir)
    setup_D(depth=4, out_dir=out_dir)
    setup_E(time_budget_s=0.2, games=10, seed=0, out_dir=out_dir)  # MCTS comparison

    # Extra: board snapshots for the report
    ab = AlphaBetaAgent(depth=3, use_ordering=True)
    rnd = RandomAgent(seed=0)

    generate_game_snapshots(ab, rnd, plies=10, out_dir=out_dir, prefix="ab_vs_random")
    generate_game_snapshots(ab, ab, plies=10, out_dir=out_dir, prefix="ab_selfplay")


if __name__ == "__main__":
    auto_generate()