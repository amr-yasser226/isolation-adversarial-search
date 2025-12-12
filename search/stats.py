from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

class SearchLimitReached(Exception):
    pass

@dataclass
class SearchStats:
    nodes: int = 0
    cutoffs: int = 0

@dataclass
class SearchContext:
    time_deadline: Optional[float] = None  # perf_counter timestamp
    node_budget: Optional[int] = None

    def check(self, stats: SearchStats, now: float) -> None:
        if self.time_deadline is not None and now >= self.time_deadline:
            raise SearchLimitReached()
        if self.node_budget is not None and stats.nodes >= self.node_budget:
            raise SearchLimitReached()