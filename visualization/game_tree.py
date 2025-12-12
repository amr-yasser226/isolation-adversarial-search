from __future__ import annotations
import os
import networkx as nx
import matplotlib.pyplot as plt

def plot_pruned_tree(edges, pruned_edges, filename: str, title: str = "Alpha-Beta Trace") -> None:
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)

    G = nx.DiGraph()
    G.add_edges_from(edges)

    # simple layered layout by depth from root "R"
    depths = {"R": 0}
    for u, v in edges:
        depths[v] = depths.get(u, 0) + 1

    layers = {}
    for n, d in depths.items():
        layers.setdefault(d, []).append(n)

    pos = {}
    for d in sorted(layers):
        nodes = sorted(layers[d])
        for i, n in enumerate(nodes):
            pos[n] = (i, -d)

    plt.figure(figsize=(10, 5))
    nx.draw_networkx_nodes(G, pos, node_size=900, node_color="#cfe8ff")
    nx.draw_networkx_labels(G, pos, font_size=8)

    # normal edges
    nx.draw_networkx_edges(G, pos, arrows=False, edge_color="#555555", width=1.5)

    # pruned edges (may include nodes not in G; draw as dashed red lines)
    for (u, v) in pruned_edges:
        if u in pos:
            x1, y1 = pos[u]
            x2, y2 = (pos[v] if v in pos else (x1 + 0.5, y1 - 1))
            plt.plot([x1, x2], [y1, y2], color="red", linestyle="--", linewidth=2)

    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(filename, dpi=200)
    plt.close()