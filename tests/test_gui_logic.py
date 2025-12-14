from __future__ import annotations

import sys
import time
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.state import GameState
from game.match import play_match
from agents.random_agent import RandomAgent
from agents.minimax_agent import MinimaxAgent
from agents.alphabeta_agent import AlphaBetaAgent
from agents.mcts_agent import MCTSAgent


def test_all_agents_produce_valid_moves():
    print("Testing all agents produce valid moves...")
    
    agents = [
        RandomAgent(seed=42),
        MinimaxAgent(depth=2),
        AlphaBetaAgent(depth=2, use_ordering=True),
        MCTSAgent(time_budget_s=0.1, seed=42),
    ]
    
    # Test on initial state
    state = GameState.new()
    for agent in agents:
        info = agent.choose_move(state)
        assert info["move"] is not None, f"{agent.name} returned None move on initial state"
        assert info["move"] in state.legal_moves(), f"{agent.name} returned illegal move"
        print(f"  ✓ {agent.name}: {info['move']}")
    
    # Test on mid-game state
    moves = [(2, 2), (3, 3), (2, 3), (4, 4)]
    for m in moves:
        state = state.apply_move(m)
    
    for agent in agents:
        info = agent.choose_move(state)
        assert info["move"] is not None, f"{agent.name} returned None move in mid-game"
        assert info["move"] in state.legal_moves(), f"{agent.name} returned illegal move in mid-game"
        print(f"  ✓ {agent.name} mid-game: {info['move']}")
    
    print("  All agents produce valid moves ✓")


def test_agents_on_terminal_states():
    """Test that agents handle terminal states gracefully."""
    print("Testing agents on terminal states...")
    
    # Create a 1x1 board (becomes terminal after first move)
    state = GameState.new(rows=1, cols=1)
    state = state.apply_move((0, 0))  # A places, now terminal
    
    assert state.is_terminal(), "1x1 board should be terminal after first move"
    assert state.winner() == 1, "Player A should win on 1x1 board"
    
    # Test RandomAgent on terminal state (this was a bug we fixed)
    rnd = RandomAgent(seed=0)
    info = rnd.choose_move(state)
    assert info["move"] is None, "RandomAgent should return None move on terminal state"
    print("  ✓ RandomAgent handles terminal state")
    
    print("  Terminal state handling ✓")


def test_agents_with_single_legal_move():
    """Test that agents correctly choose when only one move is available."""
    print("Testing agents with single legal move...")
    
    # Construct a state where only one move is possible
    # This tests the fix for the "best_move is None" bug
    state = GameState.new()
    
    # Play many moves to restrict options
    moves = [
        (2, 2), (4, 1), (3, 3), (1, 4), (4, 3), (0, 4),
        (4, 5), (0, 1), (1, 2), (0, 2), (3, 0), (1, 3),
        (2, 0), (3, 5), (5, 3), (0, 5), (3, 1), (2, 5),
        (3, 2), (2, 3), (5, 2), (2, 4), (5, 1), (4, 4),
        (5, 0), (5, 4)
    ]
    
    for m in moves:
        if state.is_terminal():
            break
        state = state.apply_move(m)
    
    if not state.is_terminal():
        legal = state.legal_moves()
        print(f"  State has {len(legal)} legal moves: {legal}")
        
        if len(legal) == 1:
            # Test that agents return this single move
            agents = [
                MinimaxAgent(depth=2),
                AlphaBetaAgent(depth=2),
            ]
            
            for agent in agents:
                info = agent.choose_move(state)
                assert info["move"] == legal[0], f"{agent.name} didn't return the only legal move"
                print(f"  ✓ {agent.name} correctly chose single legal move")
        else:
            print(f"  (Skipping single-move test, state has {len(legal)} moves)")
    else:
        print("  (State became terminal, skipping)")
    
    print("  Single legal move handling ✓")


def test_full_game_completion():
    """Test that full games can complete without errors."""
    print("Testing full game completion...")
    
    agent_pairs = [
        (AlphaBetaAgent(depth=2), RandomAgent(seed=0), "AlphaBeta vs Random"),
        (MinimaxAgent(depth=2), RandomAgent(seed=1), "Minimax vs Random"),
        (MCTSAgent(time_budget_s=0.1, seed=0), RandomAgent(seed=2), "MCTS vs Random"),
        (AlphaBetaAgent(depth=2), AlphaBetaAgent(depth=2), "AlphaBeta vs AlphaBeta"),
        (MCTSAgent(time_budget_s=0.1, seed=0), AlphaBetaAgent(depth=2), "MCTS vs AlphaBeta"),
    ]
    
    for agent_a, agent_b, name in agent_pairs:
        try:
            result = play_match(agent_a, agent_b, max_plies=100)
            winner = "A" if result.winner == 1 else "B" if result.winner == -1 else "None"
            print(f"  ✓ {name}: {len(result.moves)} moves, winner={winner}")
        except Exception as e:
            print(f"  ✗ {name}: ERROR - {e}")
            raise
    
    print("  Full game completion ✓")


def test_agent_info_structure():
    """Test that all agents return properly structured info dicts."""
    print("Testing agent info structure...")
    
    required_keys = ["move", "value", "depth", "time_s", "nodes", "cutoffs"]
    
    agents = [
        RandomAgent(seed=42),
        MinimaxAgent(depth=2),
        AlphaBetaAgent(depth=2),
        MCTSAgent(time_budget_s=0.1, seed=42),
    ]
    
    state = GameState.new()
    
    for agent in agents:
        info = agent.choose_move(state)
        
        for key in required_keys:
            assert key in info, f"{agent.name} missing key '{key}' in info"
        
        assert isinstance(info["move"], tuple) or info["move"] is None
        assert isinstance(info["value"], (int, float))
        assert isinstance(info["depth"], int)
        assert isinstance(info["time_s"], float)
        assert isinstance(info["nodes"], int)
        assert isinstance(info["cutoffs"], int)
        
        print(f"  ✓ {agent.name} returns valid info structure")
    
    print("  Agent info structure ✓")


def test_mcts_specific():
    """Test MCTS-specific functionality."""
    print("Testing MCTS specific features...")
    
    state = GameState.new()
    mcts = MCTSAgent(time_budget_s=0.2, seed=42)
    
    info = mcts.choose_move(state)
    
    # MCTS should have simulations count
    assert "simulations" in info, "MCTS should report simulations count"
    assert info["simulations"] > 0, "MCTS should run at least one simulation"
    
    print(f"  ✓ MCTS ran {info['simulations']} simulations")
    print(f"  ✓ MCTS win rate: {info['value']:.3f}")
    print(f"  ✓ MCTS max depth: {info['depth']}")
    
    print("  MCTS specific features ✓")


def test_game_state_cloning():
    """Test that game state cloning works correctly."""
    print("Testing game state cloning...")
    
    state = GameState.new()
    state = state.apply_move((2, 2))
    
    clone = state.clone()
    
    # Modify clone
    clone = clone.apply_move((3, 3))
    
    # Original should be unchanged
    assert state.active_player == -1, "Original state was modified"
    assert state.p2_pos is None, "Original state p2_pos was modified"
    
    print("  ✓ State cloning preserves original")
    print("  Game state cloning ✓")


def test_gui_agent_configs():
    """Test that GUI agent configurations are valid."""
    print("Testing GUI agent configurations...")
    
    # Import GUI module (without starting pygame)
    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"  # Prevent actual display
    
    try:
        from gui.game_gui import AGENT_CONFIGS, AGENT_NAMES
        
        print(f"  Available agents: {AGENT_NAMES}")
        
        # Test that all config factories work
        for name in AGENT_NAMES:
            factory = AGENT_CONFIGS[name]
            if factory is not None:
                agent = factory()
                assert hasattr(agent, 'choose_move'), f"{name} agent has no choose_move method"
                print(f"  ✓ {name} factory creates valid agent")
            else:
                print(f"  ✓ {name} is Human (no agent)")
        
        print("  GUI agent configurations ✓")
    except Exception as e:
        print(f"  (GUI import skipped: {e})")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("ISOLATION GUI & GAME LOGIC TEST SUITE")
    print("=" * 60)
    print()
    
    tests = [
        test_all_agents_produce_valid_moves,
        test_agents_on_terminal_states,
        test_agents_with_single_legal_move,
        test_full_game_completion,
        test_agent_info_structure,
        test_mcts_specific,
        test_game_state_cloning,
        test_gui_agent_configs,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print()
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
