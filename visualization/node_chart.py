from __future__ import annotations

import os
import matplotlib.pyplot as plt


def plot_bar_compare(labels, values, title: str, ylabel: str, filename: str) -> None:
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    plt.figure(figsize=(6, 4))
    plt.bar(labels, values, color=["#ff7f0e", "#2ca02c", "#1f77b4", "#d62728"][: len(labels)])
    plt.title(title)
    plt.ylabel(ylabel)
    for i, v in enumerate(values):
        plt.text(i, v, str(v), ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(filename, dpi=200)
    plt.close()


def save_depth_reached_plot(minimax_depths, alphabeta_depths, out_path: str, title: str) -> None:
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    plt.figure(figsize=(6.5, 4))
    data = [minimax_depths, alphabeta_depths]
    plt.boxplot(data, labels=["Minimax", "Alpha-Beta"], showmeans=True)
    plt.ylabel("Depth reached per move")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()