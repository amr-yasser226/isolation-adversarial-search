from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from game.state import GameState


@dataclass
class MCTSNode:
    """A node in the MCTS tree."""
    state: GameState
    parent: Optional["MCTSNode"] = None
    move: Optional[Tuple[int, int]] = None
    children: List["MCTSNode"] = field(default_factory=list)
    wins: float = 0.0 
    visits: int = 0
    untried_moves: List[Tuple[int, int]] = field(default_factory=list)

    def __post_init__(self):
        if not self.untried_moves:
            self.untried_moves = list(self.state.legal_moves())

    def is_fully_expanded(self) -> bool:
        return len(self.untried_moves) == 0

    def is_terminal(self) -> bool:
        return self.state.is_terminal()

    def ucb1(self, exploration_c: float = 1.41) -> float:
        """
        Calculate UCB1 value for node selection.
        
        UCB1 = wins/visits + c * sqrt(ln(parent_visits) / visits)
        
        The first term (exploitation) favors nodes with high win rates.
        The second term (exploration) favors less-visited nodes.
        """
        if self.visits == 0:
            return float("inf")
        
        exploitation = self.wins / self.visits
        exploration = exploration_c * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration

    def best_child(self, exploration_c: float = 1.41) -> "MCTSNode":
        """Select the child with highest UCB1 value."""
        return max(self.children, key=lambda c: c.ucb1(exploration_c))

    def best_move_by_visits(self) -> Tuple[int, int]:
        """Return the move with most visits (most robust choice)."""
        if not self.children:
            moves = self.state.legal_moves()
            return moves[0] if moves else None
        best_child = max(self.children, key=lambda c: c.visits)
        return best_child.move


def mcts(
    state: GameState,
    time_budget_s: float,
    exploration_c: float = 1.41,
    max_iterations: Optional[int] = None,
    seed: Optional[int] = None,
) -> dict:
    if state.is_terminal():
        return {
            "move": None,
            "value": 0.0,
            "depth": 0,
            "time_s": 0.0,
            "nodes": 0,
            "simulations": 0,
            "cutoffs": 0,
        }

    rng = random.Random(seed)
    root = MCTSNode(state=state)
    root_player = state.active_player
    
    t0 = time.perf_counter()
    deadline = t0 + time_budget_s
    iterations = 0
    nodes_created = 1
    max_depth_reached = 0

    while time.perf_counter() < deadline:
        if max_iterations is not None and iterations >= max_iterations:
            break
        
        # Phase 1: Selection
        # Traverse tree using UCB1 until we find a node to expand
        node = root
        depth = 0
        
        while node.is_fully_expanded() and not node.is_terminal():
            node = node.best_child(exploration_c)
            depth += 1
        
        # Phase 2: Expansion
        # Add a new child node for an untried move
        if not node.is_terminal() and node.untried_moves:
            move = rng.choice(node.untried_moves)
            node.untried_moves.remove(move)
            
            new_state = node.state.apply_move(move)
            child = MCTSNode(state=new_state, parent=node, move=move)
            node.children.append(child)
            node = child
            nodes_created += 1
            depth += 1
        
        max_depth_reached = max(max_depth_reached, depth)
        
        # Phase 3: Simulation (Rollout)
        # Play random moves until terminal state
        sim_state = node.state
        sim_depth = 0
        while not sim_state.is_terminal():
            moves = sim_state.legal_moves()
            move = rng.choice(moves)
            sim_state = sim_state.apply_move(move)
            sim_depth += 1
        
        max_depth_reached = max(max_depth_reached, depth + sim_depth)
        
        # Determine winner from root player's perspective
        winner = sim_state.winner()
        if winner == root_player:
            result = 1.0  # Win
        elif winner == -root_player:
            result = 0.0  # Loss
        else:
            result = 0.5  # Draw (shouldn't happen in Isolation, but handle it)
        
        # Phase 4: Backpropagation
        # Update statistics from leaf to root
        while node is not None:
            node.visits += 1
            # Flip result when backing up through opponent's nodes
            if node.state.active_player == root_player:
                node.wins += result
            else:
                node.wins += (1.0 - result)
            node = node.parent
        
        iterations += 1

    best_move = root.best_move_by_visits()
    
    best_child = None
    for child in root.children:
        if child.move == best_move:
            best_child = child
            break
    
    win_rate = best_child.wins / best_child.visits if best_child and best_child.visits > 0 else 0.5

    return {
        "move": best_move,
        "value": win_rate,
        "depth": max_depth_reached,
        "time_s": time.perf_counter() - t0,
        "nodes": nodes_created,
        "simulations": iterations,
        "cutoffs": 0,
    }
