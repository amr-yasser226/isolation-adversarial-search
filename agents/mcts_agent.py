from agents.base import Agent
from search.mcts import mcts


class MCTSAgent(Agent):
    
    def __init__(
        self,
        time_budget_s: float = 0.5,
        exploration_c: float = 1.41,
        seed: int | None = None,
    ):
        self.time_budget_s = time_budget_s
        self.exploration_c = exploration_c
        self.seed = seed
        self.name = f"MCTS(t={time_budget_s}s, c={exploration_c})"

    def choose_move(self, state) -> dict:
        info = mcts(
            state,
            time_budget_s=self.time_budget_s,
            exploration_c=self.exploration_c,
            seed=self.seed,
        )
        info.setdefault("cutoffs", 0)
        info.setdefault("depth", 0)
        
        return info
