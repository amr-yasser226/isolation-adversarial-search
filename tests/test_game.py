import pytest
from game.state import GameState

def test_initial_legal_moves_are_all_cells():
    s = GameState.new(rows=6, cols=6)
    assert len(s.legal_moves()) == 36

def test_first_move_places_player_and_switches_turn():
    s = GameState.new(rows=3, cols=3)
    s2 = s.apply_move((1, 1))
    assert s2.active_player == -1
    assert s2.p1_pos == (1, 1)
    assert s2.board.grid[1][1] == "A"

def test_moving_blocks_old_position():
    s = GameState.new(rows=3, cols=3)
    s = s.apply_move((0, 0))  # A places
    s = s.apply_move((2, 2))  # B places
    assert s.active_player == 1

    s2 = s.apply_move((0, 1))  # A moves
    assert s2.board.grid[0][0] == "X"
    assert s2.board.grid[0][1] == "A"

def test_illegal_move_raises():
    s = GameState.new(rows=3, cols=3)
    s = s.apply_move((1, 1))  # A places
    with pytest.raises(ValueError):
        # B cannot place on occupied cell
        s.apply_move((1, 1))

def test_terminal_on_1x1_board_after_first_placement():
    s = GameState.new(rows=1, cols=1)
    s = s.apply_move((0, 0))  # A places
    assert s.is_terminal()
    assert s.winner() == 1