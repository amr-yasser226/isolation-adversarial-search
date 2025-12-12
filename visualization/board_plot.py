from __future__ import annotations
import os
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

def save_board_image(board, filename: str, title: str | None = None) -> None:
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)

    # Map: "."=0, "A"=1, "B"=2, "X"=3
    mapping = {".": 0, "A": 1, "B": 2, "X": 3}
    data = [[mapping[c] for c in row] for row in board.grid]

    cmap = ListedColormap(["#f7f7f7", "#1f77b4", "#d62728", "#2f2f2f"])

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.imshow(data, cmap=cmap, vmin=0, vmax=3)

    ax.set_xticks(range(board.cols))
    ax.set_yticks(range(board.rows))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xticks([x - 0.5 for x in range(1, board.cols)], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, board.rows)], minor=True)
    ax.grid(which="minor", color="#999999", linewidth=1)
    ax.tick_params(which="both", bottom=False, left=False)

    # overlay symbols
    for r in range(board.rows):
        for c in range(board.cols):
            s = board.grid[r][c]
            if s != ".":
                ax.text(c, r, s, ha="center", va="center", color="white", fontsize=14, fontweight="bold")

    if title:
        ax.set_title(title)

    plt.tight_layout()
    plt.savefig(filename, dpi=200)
    plt.close(fig)