# isolation-adversarial-search (Minimax & Alpha-Beta)

Implementation of the game **Isolation** with adversarial search agents, designed for clear experimentation and reproducible results.  
Includes **Minimax**, **Alpha-Beta pruning**, **iterative deepening** (time-bounded search), optional **move ordering**, and a LaTeX report with generated figures.

## What’s in this repo

- **Game engine** for Isolation (state transitions, legal moves, terminal detection)
- **Agents**
  - `MinimaxAgent` (depth-limited or iterative deepening with time budget)
  - `AlphaBetaAgent` (depth-limited or iterative deepening; optional move ordering)
  - `RandomAgent` (baseline)
- **Instrumentation**
  - nodes expanded
  - runtime per move
  - Alpha-Beta cutoff count
  - **depth reached** per move (iterative deepening)
- **Experiments (Setups A–D)** + plots saved to `figures/`
- **Visualizations**
  - bar charts for nodes/time/wins
  - pruned-tree diagram for Alpha-Beta
  - board snapshots and demo move-by-move screenshots
- **LaTeX report** output as `report.pdf` in the repository root

---

## Project Structure

```text
.
├── agents/                  Agents: minimax, alphabeta, random
├── experiments/             Experiment runners (Setups A–D) + benchmark
├── figures/                 Generated plots + board snapshots (tracked here)
│   ├── demo/                Demo game move-by-move images
│   ├── ab_vs_random_*.png   Snapshot sequence: AlphaBeta vs Random
│   └── ab_selfplay_*.png    Snapshot sequence: AlphaBeta self-play
├── game/                    Isolation engine: board, state, match loop, moves
├── report/                  LaTeX source for the report (main.tex)
├── search/                  Minimax/AlphaBeta core + evaluation + stats
├── tests/                   Pytest suite
├── main.py                  Demo runner (saves images under figures/demo/)
├── requirements.txt         Python dependencies
└── report.pdf               Built report (when generated locally)
```

Requirements

* Python 3.10+
* Recommended: virtual environment
* For building the PDF report: a LaTeX distribution (e.g., TeX Live) + latexmk


Setup
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

How to Run
1) Run experiment setups (A–D)
This prints metrics and writes plots into figures/.
```bash
python -m experiments.run_setups
```
2) Generate all figures + snapshots (recommended)
Runs Setups A–D, generates plots, and creates board snapshot sequences used in the report.
```bash
python -m visualization.auto_generate_figures
```
3) Run a demo game (move-by-move screenshots)
Saves images under figures/demo/.
```bash
python -m main
```
4) Quick benchmark (single position)
```bash
python -m experiments.run_experiments
```

Experimental Setups (A–D)

* Setup A — Same depth comparison
Minimax vs Alpha-Beta on the same mid-game states at the same fixed depth.
Metrics: time and nodes expanded.

* Setup B — Same time budget per move (Iterative Deepening)
Both algorithms get the same per-move time budget; depth increases until time runs out.
Metrics: win rate vs random baseline and depth reached per move (required for time-bounded search).

* Setup C — Fixed depth vs Random
Gameplay evaluation at a fixed depth vs a random opponent.
Metrics: wins, avg nodes/move, avg time/move.

* Setup D — Move ordering impact on pruning
Alpha-Beta with and without move ordering at the same depth.
Metrics: nodes expanded, cutoff count, plus a pruned-tree visualization.



Generated Outputs
After running python -m visualization.auto_generate_figures, you should see:
Plots (core experiment figures)

* figures/setupA_nodes.png, figures/setupA_time.png
* figures/setupB_depth.png
* figures/setupC_wins.png, figures/setupC_nodes.png, figures/setupC_time.png
* figures/setupD_nodes.png, figures/setupD_cutoffs.png
* figures/setupD_pruned_tree.png, figures/setupD_initial_board.png

Snapshot sequences (used in the report)

* figures/ab_vs_random_00.png … figures/ab_vs_random_10.png
* figures/ab_selfplay_00.png … figures/ab_selfplay_10.png

Demo screenshots

* figures/demo/move_00.png … (depends on game length)


Build the PDF Report (report.pdf in repo root)
The LaTeX source is report/main.tex. Build and output the PDF into the repository root:
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

Isolation Rules (as implemented)

* The piece moves like a chess queen: any number of squares in 8 directions, stopping before blocked/occupied squares.
* After moving, the square you left becomes blocked permanently.
* If a player has no legal moves on their turn, they lose.
* Initial placement: if a player has not placed yet, they may place on any empty cell.


Reproducibility Notes

* Experiments are designed to be deterministic when seeded.
* Runtime measurements depend on machine load; for consistent timing results, run on an idle system.