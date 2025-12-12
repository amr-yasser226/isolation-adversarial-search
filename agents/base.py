from __future__ import annotations
from typing import Dict, Any

class Agent:
    name: str = "Agent"
    def choose_move(self, state) -> Dict[str, Any]:
        raise NotImplementedError