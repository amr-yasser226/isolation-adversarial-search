from __future__ import annotations

import os
import random
import time
from statistics import mean

from game.state import GameState
from game.match import play_match
from agents.random_agent import RandomAgent
from agents.minimax_agent import MinimaxAgent
from agents.alphabeta_agent import AlphaBetaAgent

from search.minimax import minimax
from search.alphabeta import alphabeta, SearchTrace
from search.evaluation import mobility_heuristic
from search.stats import SearchStats

from visualization.board_plot import save_board_image
from visualization.node_chart import plot_bar_compare, save_depth_reached_plot
from visualization.game_tree import plot_pruned_tree


def generate_midgame_states(n: int, plies: int, seed: int = 0) -> list[GameState]:
    rng = random.Random(seed)
    states = []
    for _ in range(n):
        s = GameState.new()
        for _p in range(plies):
            if s.is_terminal():
                break
            mv = rng.choice(s.legal_moves())
            s = s.apply_move(mv)
        states.append(s)
    return states


# -------------------------
# Setup A: same positions, same depth
# -------------------------
def setup_A(depth: int = 3, n_states: int = 10, plies: int = 6, seed: int = 0, out_dir: str = "figures"):
    os.makedirs(out_dir, exist_ok=True)
    states = generate_midgame_states(n_states, plies, seed)

    mm_times, ab_times = [], []
    mm_nodes, ab_nodes, ab_cutoffs = [], [], []

    for s in states:
        root = s.active_player

        st = SearchStats()
        t0 = time.perf_counter()
        minimax(s, depth, mobility_heuristic, root, stats=st)
        mm_times.append(time.perf_counter() - t0)
        mm_nodes.append(st.nodes)

        st2 = SearchStats()
        t1 = time.perf_counter()
        alphabeta(s, depth, float("-inf"), float("inf"), mobility_heuristic, root, stats=st2, use_ordering=False)
        ab_times.append(time.perf_counter() - t1)
        ab_nodes.append(st2.nodes)
        ab_cutoffs.append(st2.cutoffs)

    print("[Setup A] Same depth comparison")
    print(f"Depth={depth}, states={n_states}, plies_start={plies}")
    print(f"Minimax avg time={mean(mm_times):.6f}s, avg nodes={int(mean(mm_nodes))}")
    print(f"AlphaBeta(no-order) avg time={mean(ab_times):.6f}s, avg nodes={int(mean(ab_nodes))}, avg cutoffs={int(mean(ab_cutoffs))}")

    plot_bar_compare(
        ["Minimax", "AlphaBeta"],
        [int(mean(mm_nodes)), int(mean(ab_nodes))],
        "Setup A: Avg Nodes Expanded (same depth)",
        "Nodes",
        f"{out_dir}/setupA_nodes.png",
    )
    plot_bar_compare(
        ["Minimax", "AlphaBeta"],
        [round(mean(mm_times), 6), round(mean(ab_times), 6)],
        "Setup A: Avg Time (same depth)",
        "Seconds",
        f"{out_dir}/setupA_time.png",
    )


# -------------------------
# Setup B: same time budget per move (iterative deepening) + depth reached
# -------------------------
def setup_B(time_budget_s: float = 0.05, max_depth: int = 8, games: int = 10, seed: int = 0, out_dir: str = "figures"):
    """
    Measures:
      - win rate vs random (sanity/strength under time constraints)
      - depth reached per move (core requirement)
    """
    os.makedirs(out_dir, exist_ok=True)
    print("\n[Setup B] Same time budget per move (iterative deepening)")
    mm = MinimaxAgent(depth=max_depth, time_budget_s=time_budget_s)
    ab = AlphaBetaAgent(depth=max_depth, time_budget_s=time_budget_s, use_ordering=True, use_tt=False)
    rnd = RandomAgent(seed=seed)

    def play_game_collect(agent_a, agent_b, collect_player: int):
        """
        Plays a game without using play_match so we can reliably collect per-move
        info (depth/nodes/time) directly from choose_move().
        Returns (winner, depths, nodes, times).
        """
        s = GameState.new()
        depths, nodes, times = [], [], []

        while not s.is_terminal():
            mover = s.active_player
            agent = agent_a if mover == 1 else agent_b
            info = agent.choose_move(s)

            if mover == collect_player:
                depths.append(int(info.get("depth", 0)))
                nodes.append(int(info.get("nodes", 0)))
                times.append(float(info.get("time_s", 0.0)))

            s = s.apply_move(info["move"])

        # Terminal: active player cannot move => loses => winner is the other player
        winner = -s.active_player
        return winner, depths, nodes, times

    # Compare vs random (smart side alternates starting)
    mm_wins = 0
    ab_wins = 0
    mm_depths_all, ab_depths_all = [], []
    mm_nodes_all, ab_nodes_all = [], []
    mm_times_all, ab_times_all = [], []

    for g in range(games):
        if g % 2 == 0:
            # smart is Player 1
            mm_winner, mm_depths, mm_nodes, mm_times = play_game_collect(mm, rnd, collect_player=1)
            ab_winner, ab_depths, ab_nodes, ab_times = play_game_collect(ab, rnd, collect_player=1)
            smart_player = 1
        else:
            # smart is Player -1
            mm_winner, mm_depths, mm_nodes, mm_times = play_game_collect(rnd, mm, collect_player=-1)
            ab_winner, ab_depths, ab_nodes, ab_times = play_game_collect(rnd, ab, collect_player=-1)
            smart_player = -1

        if mm_winner == smart_player:
            mm_wins += 1
        if ab_winner == smart_player:
            ab_wins += 1

        mm_depths_all.extend(mm_depths)
        ab_depths_all.extend(ab_depths)
        mm_nodes_all.extend(mm_nodes)
        ab_nodes_all.extend(ab_nodes)
        mm_times_all.extend(mm_times)
        ab_times_all.extend(ab_times)

    def safe_mean(xs):
        return mean(xs) if xs else 0.0

    print(f"Time budget per move: {time_budget_s}s, max_depth={max_depth}")
    print(f"Minimax vs Random wins (as the 'smart' side): {mm_wins}/{games}")
    print(f"AlphaBeta vs Random wins (as the 'smart' side): {ab_wins}/{games}")
    print(f"Minimax depth reached:   avg={safe_mean(mm_depths_all):.2f}, max={max(mm_depths_all) if mm_depths_all else 0}")
    print(f"AlphaBeta depth reached: avg={safe_mean(ab_depths_all):.2f}, max={max(ab_depths_all) if ab_depths_all else 0}")

    # Optional sanity metrics (useful if you want to mention them in the report)
    print(f"Minimax time/move:   avg={safe_mean(mm_times_all):.5f}s")
    print(f"AlphaBeta time/move: avg={safe_mean(ab_times_all):.5f}s")

    # Save the required "depth reached" plot
    save_depth_reached_plot(
        mm_depths_all,
        ab_depths_all,
        out_path=f"{out_dir}/setupB_depth.png",
        title=f"Setup B: Depth reached (budget={time_budget_s}s, max_depth={max_depth})",
    )

    return {
        "minimax_depths": mm_depths_all,
        "alphabeta_depths": ab_depths_all,
        "time_budget_s": time_budget_s,
        "max_depth": max_depth,
        "games": games,
        "mm_wins": mm_wins,
        "ab_wins": ab_wins,
    }


# -------------------------
# Setup C: fixed depth vs random (visual + win-rate + efficiency)
# -------------------------
def setup_C(depth: int = 3, games: int = 20, seed: int = 0, out_dir: str = "figures"):
    os.makedirs(out_dir, exist_ok=True)
    rnd = RandomAgent(seed=seed)
    mm = MinimaxAgent(depth=depth)
    ab = AlphaBetaAgent(depth=depth, use_ordering=True)

    def run(agent, name: str):
        wins = 0
        avg_nodes = []
        avg_time = []
        for g in range(games):
            if g % 2 == 0:
                res = play_match(agent, rnd)
                smart_player = 1
            else:
                res = play_match(rnd, agent)
                smart_player = -1

            if res.winner == smart_player:
                wins += 1

            agent_logs = [m for m in res.moves if m.player == smart_player]
            if agent_logs:
                avg_nodes.append(mean([m.nodes for m in agent_logs]))
                avg_time.append(mean([m.time_s for m in agent_logs]))

        print(f"{name}: wins={wins}/{games}, avg_nodes/move={mean(avg_nodes):.1f}, avg_time/move={mean(avg_time):.5f}s")
        return wins, mean(avg_nodes), mean(avg_time)

    print("\n[Setup C] Fixed depth vs Random")
    mm_w, mm_n, mm_t = run(mm, "Minimax")
    ab_w, ab_n, ab_t = run(ab, "AlphaBeta")

    plot_bar_compare(
        ["Minimax", "AlphaBeta"],
        [mm_w, ab_w],
        f"Setup C: Wins vs Random (depth={depth})",
        "Wins",
        f"{out_dir}/setupC_wins.png",
    )
    plot_bar_compare(
        ["Minimax", "AlphaBeta"],
        [int(mm_n), int(ab_n)],
        f"Setup C: Avg Nodes/Move (depth={depth})",
        "Nodes",
        f"{out_dir}/setupC_nodes.png",
    )
    plot_bar_compare(
        ["Minimax", "AlphaBeta"],
        [round(mm_t, 6), round(ab_t, 6)],
        f"Setup C: Avg Time/Move (depth={depth})",
        "Seconds",
        f"{out_dir}/setupC_time.png",
    )


# -------------------------
# Setup D: pruning effectiveness depends on move ordering (+ make a pruned tree figure)
# -------------------------
def setup_D(depth: int = 4, out_dir: str = "figures"):
    os.makedirs(out_dir, exist_ok=True)
    s = GameState.new()
    root = s.active_player

    st_no = SearchStats()
    alphabeta(s, depth, float("-inf"), float("inf"), mobility_heuristic, root, stats=st_no, use_ordering=False)

    st_yes = SearchStats()
    alphabeta(s, depth, float("-inf"), float("inf"), mobility_heuristic, root, stats=st_yes, use_ordering=True)

    print("\n[Setup D] Alpha-Beta pruning sensitivity to move ordering")
    print(f"Depth={depth}")
    print(f"AB no-order: nodes={st_no.nodes}, cutoffs={st_no.cutoffs}")
    print(f"AB ordered:  nodes={st_yes.nodes}, cutoffs={st_yes.cutoffs}")

    plot_bar_compare(
        ["AB no-order", "AB ordered"],
        [st_no.nodes, st_yes.nodes],
        f"Setup D: Nodes Expanded (depth={depth})",
        "Nodes",
        f"{out_dir}/setupD_nodes.png",
    )
    plot_bar_compare(
        ["AB no-order", "AB ordered"],
        [st_no.cutoffs, st_yes.cutoffs],
        f"Setup D: Cutoffs (depth={depth})",
        "Cutoffs",
        f"{out_dir}/setupD_cutoffs.png",
    )

    trace = SearchTrace()
    st_trace = SearchStats()
    alphabeta(
        s,
        depth=3,
        alpha=float("-inf"),
        beta=float("inf"),
        eval_fn=mobility_heuristic,
        root_player=root,
        stats=st_trace,
        use_ordering=True,
        trace=trace,
    )

    plot_pruned_tree(
        trace.edges,
        trace.pruned_edges,
        f"{out_dir}/setupD_pruned_tree.png",
        title="Alpha-Beta Partial Tree (d=3) with Pruned Branches",
    )

    save_board_image(s.board, f"{out_dir}/setupD_initial_board.png", title="Initial State")


def main():
    setup_A(depth=3, n_states=12, plies=6, seed=0, out_dir="figures")
    setup_B(time_budget_s=0.05, max_depth=8, games=10, seed=0, out_dir="figures")
    setup_C(depth=3, games=20, seed=0, out_dir="figures")
    setup_D(depth=4, out_dir="figures")


if __name__ == "__main__":
    main()