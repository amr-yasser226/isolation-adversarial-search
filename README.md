# isolation-adversarial-search (Minimax, Alpha-Beta & MCTS)

Implementation of the game **Isolation** with adversarial search agents, designed for clear experimentation and reproducible results.  
Includes **Minimax**, **Alpha-Beta pruning**, **Monte Carlo Tree Search (MCTS)**, **iterative deepening** (time-bounded search), optional **move ordering**, an interactive **Pygame GUI**, and a LaTeX report with generated figures.

## What's in this repo

- **Game engine** for Isolation (state transitions, legal moves, terminal detection)
- **Agents**
  - `MinimaxAgent` (depth-limited or iterative deepening with time budget)
  - `AlphaBetaAgent` (depth-limited or iterative deepening; optional move ordering)
  - `MCTSAgent` (Monte Carlo Tree Search with UCB1 selection)
  - `RandomAgent` (baseline)
- **Instrumentation**
  - nodes expanded
  - runtime per move
  - Alpha-Beta cutoff count
  - **depth reached** per move (iterative deepening)
  - **simulations count** (MCTS)
- **Experiments (Setups A–E)** + plots saved to `figures/`
- **Pygame GUI** for interactive play (Human vs AI, AI vs AI)
- **Visualizations**
  - bar charts for nodes/time/wins
  - pruned-tree diagram for Alpha-Beta
  - board snapshots and demo move-by-move screenshots
- **LaTeX report** output as `report.pdf` in the repository root

---

## Project Structure

```text
.
├── agents/                  Agents: minimax, alphabeta, mcts, random
│   ├── alphabeta_agent.py   Alpha-Beta agent wrapper
│   ├── minimax_agent.py     Minimax agent wrapper
│   ├── mcts_agent.py        MCTS agent wrapper
│   ├── random_agent.py      Random baseline agent
│   └── utils.py             Shared utilities
├── experiments/             Experiment runners (Setups A–E) + benchmark
├── figures/                 Generated plots + board snapshots (tracked here)
│   ├── demo/                Demo game move-by-move images
│   ├── setupA_*.png         Setup A figures
│   ├── setupB_*.png         Setup B figures
│   ├── setupC_*.png         Setup C figures
│   ├── setupD_*.png         Setup D figures
│   └── setupE_*.png         Setup E figures (MCTS comparison)
├── game/                    Isolation engine: board, state, match loop, moves
├── gui/                     Pygame GUI for interactive play
│   └── game_gui.py          Main GUI application
├── report/                  LaTeX source for the report (main.tex)
├── search/                  Minimax/AlphaBeta/MCTS core + evaluation + stats
│   ├── alphabeta.py         Alpha-Beta with pruning
│   ├── minimax.py           Standard minimax
│   ├── mcts.py              Monte Carlo Tree Search
│   ├── evaluation.py        Heuristic evaluation functions
│   └── stats.py             Search statistics tracking
├── tests/                   Pytest suite
├── main.py                  Demo runner (saves images under figures/demo/)
├── requirements.txt         Python dependencies
└── report.pdf               Built report (when generated locally)
```

## Requirements

* Python 3.10+
* Recommended: virtual environment
* For building the PDF report: a LaTeX distribution (e.g., TeX Live) + latexmk

---

## Setup

From the repository root:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run tests:
```bash
python -m pytest -q
```

---

## How to Run

### 1) Interactive GUI (Recommended)
Play games interactively with the Pygame GUI:
```bash
python -m gui.game_gui
```

Features:
- Select agents for Player A and Player B (Human, Minimax, AlphaBeta, MCTS, Random)
- Click on highlighted cells to make moves (when playing as Human)
- Watch AI vs AI games
- Real-time display of nodes, depth, time per move
- Move history panel

### 2) Run experiment setups (A–E)
This prints metrics and writes plots into `figures/`.
```bash
python -m experiments.run_setups
```

### 3) Generate all figures + snapshots
Runs Setups A–E, generates plots, and creates board snapshot sequences used in the report.
```bash
python -m visualization.auto_generate_figures
```

### 4) Run a demo game (move-by-move screenshots)
Saves images under `figures/demo/`.
```bash
python -m main
```

### 5) Quick benchmark (single position)
```bash
python -m experiments.run_experiments
```

---

## Experimental Setups (A–E)

* **Setup A** — Same depth comparison  
  Minimax vs Alpha-Beta on the same mid-game states at the same fixed depth.  
  *Metrics*: time and nodes expanded.

* **Setup B** — Same time budget per move (Iterative Deepening)  
  Both algorithms get the same per-move time budget; depth increases until time runs out.  
  *Metrics*: win rate vs random baseline and depth reached per move.

* **Setup C** — Fixed depth vs Random  
  Gameplay evaluation at a fixed depth vs a random opponent.  
  *Metrics*: wins, avg nodes/move, avg time/move.

* **Setup D** — Move ordering impact on pruning  
  Alpha-Beta with and without move ordering at the same depth.  
  *Metrics*: nodes expanded, cutoff count, plus a pruned-tree visualization.

* **Setup E** — MCTS vs Alpha-Beta comparison  
  Compare Monte Carlo Tree Search against Alpha-Beta under the same time budget.  
  *Metrics*: win rate vs Random, head-to-head wins, simulations vs nodes, time per move.

---

## Algorithms

### Minimax
Standard depth-limited minimax search with alternating max/min layers. Uses a heuristic evaluation function at leaf nodes.

### Alpha-Beta Pruning
Optimization of minimax that prunes branches that cannot affect the final decision. Maintains alpha (best for MAX) and beta (best for MIN) bounds.

### Monte Carlo Tree Search (MCTS)
A simulation-based search algorithm that differs fundamentally from minimax:
- **Selection**: Navigate tree using UCB1 to balance exploration/exploitation
- **Expansion**: Add new nodes for unexplored moves
- **Simulation**: Random playout to terminal state
- **Backpropagation**: Update win statistics from leaf to root

MCTS doesn't require an evaluation function — it learns move quality through simulated games.

---

## Generated Outputs

After running `python -m visualization.auto_generate_figures`, you should see:

**Plots (core experiment figures)**
* `figures/setupA_nodes.png`, `figures/setupA_time.png`
* `figures/setupB_depth.png`
* `figures/setupC_wins.png`, `figures/setupC_nodes.png`, `figures/setupC_time.png`
* `figures/setupD_nodes.png`, `figures/setupD_cutoffs.png`
* `figures/setupD_pruned_tree.png`, `figures/setupD_initial_board.png`
* `figures/setupE_wins_vs_random.png`, `figures/setupE_head_to_head.png`, `figures/setupE_nodes.png`

**Snapshot sequences (used in the report)**
* `figures/ab_vs_random_00.png` … `figures/ab_vs_random_10.png`
* `figures/ab_selfplay_00.png` … `figures/ab_selfplay_10.png`

**Demo screenshots**
* `figures/demo/move_00.png` … (depends on game length)

---

## Build the PDF Report

The LaTeX source is `report/main.tex`. Build and output the PDF into the repository root:
```bash
cd report
latexmk -pdf -interaction=nonstopmode -halt-on-error -output-directory=.. -jobname=report main.tex
cd ..
```

Clean rebuild:
```bash
rm -f report.pdf report.aux report.log report.fls report.fdb_latexmk report.out
cd report
latexmk -pdf -interaction=nonstopmode -halt-on-error -output-directory=.. -jobname=report main.tex
cd ..
```

---

## Isolation Rules (as implemented)

* The piece moves like a chess queen: any number of squares in 8 directions, stopping before blocked/occupied squares.
* After moving, the square you left becomes blocked permanently.
* If a player has no legal moves on their turn, they lose.
* Initial placement: if a player has not placed yet, they may place on any empty cell.

---

## Reproducibility Notes

* Experiments are designed to be deterministic when seeded.
* Runtime measurements depend on machine load; for consistent timing results, run on an idle system.
* MCTS can be seeded for reproducibility, but with random simulations, results may vary slightly.