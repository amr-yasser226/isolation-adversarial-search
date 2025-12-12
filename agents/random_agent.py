from __future__ import annotations
import random
import time
from agents.base import Agent

class RandomAgent(Agent):
    def __init__(self, seed: int = 0):
        self.name = f"Random(seed={seed})"
        self.rng = random.Random(seed)

    def choose_move(self, state):
        t0 = time.perf_counter()
        moves = state.legal_moves()
        mv = self.rng.choice(moves)
        return {"move": mv, "value": 0.0, "depth": 0, "time_s": time.perf_counter() - t0, "nodes": 1, "cutoffs": 0}