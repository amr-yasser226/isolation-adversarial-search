from __future__ import annotations

import sys
import threading
import time
from typing import Optional, Tuple, List

import pygame

from game.state import GameState
from agents.base import Agent
from agents.random_agent import RandomAgent
from agents.minimax_agent import MinimaxAgent
from agents.alphabeta_agent import AlphaBetaAgent
from agents.mcts_agent import MCTSAgent

# Window dimensions
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700

# Board dimensions
BOARD_SIZE = 6
CELL_SIZE = 80
BOARD_MARGIN = 50
BOARD_WIDTH = CELL_SIZE * BOARD_SIZE
BOARD_HEIGHT = CELL_SIZE * BOARD_SIZE

# Panel dimensions
PANEL_X = BOARD_MARGIN + BOARD_WIDTH + 30
PANEL_WIDTH = WINDOW_WIDTH - PANEL_X - 20

# Colors
COLOR_BG = (30, 30, 40)
COLOR_BOARD_LIGHT = (240, 240, 235)
COLOR_BOARD_DARK = (200, 200, 195)
COLOR_BLOCKED = (60, 60, 70)
COLOR_PLAYER_A = (52, 152, 219)  # Blue
COLOR_PLAYER_B = (231, 76, 60)   # Red
COLOR_HIGHLIGHT = (46, 204, 113, 150)  # Green with alpha
COLOR_LAST_MOVE = (241, 196, 15)  # Yellow
COLOR_TEXT = (255, 255, 255)
COLOR_TEXT_DIM = (150, 150, 160)
COLOR_BUTTON = (70, 130, 180)
COLOR_BUTTON_HOVER = (100, 160, 210)
COLOR_BUTTON_DISABLED = (80, 80, 90)
COLOR_PANEL_BG = (40, 40, 50)

# Fonts (initialized later)
FONT_LARGE = None
FONT_MEDIUM = None
FONT_SMALL = None


# ============================================================================
# Agent Factory
# ============================================================================

AGENT_CONFIGS = {
    "Human": None,
    "Random": lambda: RandomAgent(seed=int(time.time() * 1000) % 10000),
    "Minimax (d=2)": lambda: MinimaxAgent(depth=2),
    "Minimax (d=3)": lambda: MinimaxAgent(depth=3),
    "AlphaBeta (d=3)": lambda: AlphaBetaAgent(depth=3, use_ordering=True),
    "AlphaBeta (d=4)": lambda: AlphaBetaAgent(depth=4, use_ordering=True),
    "MCTS (0.5s)": lambda: MCTSAgent(time_budget_s=0.5),
    "MCTS (1.0s)": lambda: MCTSAgent(time_budget_s=1.0),
}

AGENT_NAMES = list(AGENT_CONFIGS.keys())


# ============================================================================
# Button Class
# ============================================================================

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 callback=None, enabled: bool = True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.enabled = enabled
        self.hovered = False

    def draw(self, screen):
        if not self.enabled:
            color = COLOR_BUTTON_DISABLED
        elif self.hovered:
            color = COLOR_BUTTON_HOVER
        else:
            color = COLOR_BUTTON
        
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, COLOR_TEXT_DIM, self.rect, width=1, border_radius=5)
        
        text_color = COLOR_TEXT if self.enabled else COLOR_TEXT_DIM
        text_surf = FONT_SMALL.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.enabled and self.rect.collidepoint(event.pos) and self.callback:
                self.callback()
                return True
        return False


# ============================================================================
# Dropdown Class
# ============================================================================

class Dropdown:
    def __init__(self, x: int, y: int, width: int, height: int, 
                 options: List[str], selected: int = 0, label: str = ""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.options = options
        self.selected = selected
        self.label = label
        self.expanded = False
        self.main_rect = pygame.Rect(x, y, width, height)

    def draw(self, screen):
        # Draw label
        if self.label:
            label_surf = FONT_SMALL.render(self.label, True, COLOR_TEXT_DIM)
            screen.blit(label_surf, (self.x, self.y - 20))
        
        # Draw main box
        color = COLOR_BUTTON_HOVER if self.expanded else COLOR_BUTTON
        pygame.draw.rect(screen, color, self.main_rect, border_radius=5)
        pygame.draw.rect(screen, COLOR_TEXT_DIM, self.main_rect, width=1, border_radius=5)
        
        # Draw selected text
        text_surf = FONT_SMALL.render(self.options[self.selected], True, COLOR_TEXT)
        text_rect = text_surf.get_rect(midleft=(self.x + 10, self.y + self.height // 2))
        screen.blit(text_surf, text_rect)
        
        # Draw arrow
        arrow = "▼" if not self.expanded else "▲"
        arrow_surf = FONT_SMALL.render(arrow, True, COLOR_TEXT)
        arrow_rect = arrow_surf.get_rect(midright=(self.x + self.width - 10, self.y + self.height // 2))
        screen.blit(arrow_surf, arrow_rect)
        
        # Draw expanded options
        if self.expanded:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.x, self.y + (i + 1) * self.height, 
                                         self.width, self.height)
                option_color = COLOR_BUTTON_HOVER if i == self.selected else COLOR_PANEL_BG
                pygame.draw.rect(screen, option_color, option_rect)
                pygame.draw.rect(screen, COLOR_TEXT_DIM, option_rect, width=1)
                
                text_surf = FONT_SMALL.render(option, True, COLOR_TEXT)
                text_rect = text_surf.get_rect(midleft=(self.x + 10, option_rect.centery))
                screen.blit(text_surf, text_rect)

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.main_rect.collidepoint(event.pos):
                self.expanded = not self.expanded
                return True
            elif self.expanded:
                for i in range(len(self.options)):
                    option_rect = pygame.Rect(self.x, self.y + (i + 1) * self.height,
                                             self.width, self.height)
                    if option_rect.collidepoint(event.pos):
                        self.selected = i
                        self.expanded = False
                        return True
                self.expanded = False
        return False

    def get_selected(self) -> str:
        return self.options[self.selected]


# ============================================================================
# Game GUI Class
# ============================================================================

class IsolationGUI:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Isolation - Adversarial Search")
        
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Initialize fonts
        global FONT_LARGE, FONT_MEDIUM, FONT_SMALL
        FONT_LARGE = pygame.font.Font(None, 48)
        FONT_MEDIUM = pygame.font.Font(None, 32)
        FONT_SMALL = pygame.font.Font(None, 24)
        
        # Game state
        self.state: Optional[GameState] = None
        self.agents: Tuple[Optional[Agent], Optional[Agent]] = (None, None)
        self.move_history: List[dict] = []
        self.last_move: Optional[Tuple[int, int]] = None
        self.legal_moves: List[Tuple[int, int]] = []
        self.last_info: Optional[dict] = None
        
        # UI state
        self.thinking = False
        self.thinking_thread: Optional[threading.Thread] = None
        self.pending_move: Optional[dict] = None
        self.move_lock = threading.Lock()  # Thread safety for pending_move
        self.game_over = False
        self.winner_text = ""
        self.error_message = ""
        
        # UI elements
        self.setup_ui()
        
        # Start new game
        self.new_game()

    def setup_ui(self):
        """Create UI elements."""
        panel_y = BOARD_MARGIN
        
        # Agent selection dropdowns
        self.dropdown_a = Dropdown(
            PANEL_X, panel_y + 20, 180, 30,
            AGENT_NAMES, selected=4, label="Player A (Blue)"
        )
        
        self.dropdown_b = Dropdown(
            PANEL_X, panel_y + 90, 180, 30,
            AGENT_NAMES, selected=0, label="Player B (Red)"
        )
        
        # Buttons
        self.btn_new_game = Button(
            PANEL_X, panel_y + 150, 85, 35, "New Game",
            callback=self.new_game
        )
        
        self.btn_reset = Button(
            PANEL_X + 95, panel_y + 150, 85, 35, "Reset",
            callback=self.reset_game
        )
        
        self.buttons = [self.btn_new_game, self.btn_reset]
        self.dropdowns = [self.dropdown_a, self.dropdown_b]

    def new_game(self):
        """Start a new game with selected agents."""
        # Close any expanded dropdowns
        for dd in self.dropdowns:
            dd.expanded = False
        
        # Create agents
        agent_a_name = self.dropdown_a.get_selected()
        agent_b_name = self.dropdown_b.get_selected()
        
        agent_a = AGENT_CONFIGS[agent_a_name]() if AGENT_CONFIGS[agent_a_name] else None
        agent_b = AGENT_CONFIGS[agent_b_name]() if AGENT_CONFIGS[agent_b_name] else None
        
        self.agents = (agent_a, agent_b)
        
        # Reset game state
        self.state = GameState.new(rows=BOARD_SIZE, cols=BOARD_SIZE)
        self.move_history = []
        self.last_move = None
        self.last_info = None
        self.legal_moves = self.state.legal_moves()
        self.game_over = False
        self.winner_text = ""
        self.thinking = False
        self.pending_move = None
        
        # Trigger AI move if AI plays first
        self.check_ai_turn()

    def reset_game(self):
        """Reset the current game (same agents)."""
        # Close any expanded dropdowns
        for dd in self.dropdowns:
            dd.expanded = False
        
        # Reset game state but keep same agents
        self.state = GameState.new(rows=BOARD_SIZE, cols=BOARD_SIZE)
        self.move_history = []
        self.last_move = None
        self.last_info = None
        self.legal_moves = self.state.legal_moves()
        self.game_over = False
        self.winner_text = ""
        self.error_message = ""
        self.thinking = False
        self.pending_move = None
        
        # Trigger AI move if AI plays first
        self.check_ai_turn()

    def check_ai_turn(self):
        """Check if it's an AI's turn and trigger move calculation."""
        if self.game_over or self.thinking:
            return
        
        agent = self.agents[0] if self.state.active_player == 1 else self.agents[1]
        
        if agent is not None:
            self.thinking = True
            self.thinking_thread = threading.Thread(target=self.calculate_ai_move, args=(agent,))
            self.thinking_thread.start()

    def calculate_ai_move(self, agent: Agent):
        """Calculate AI move in a separate thread."""
        try:
            info = agent.choose_move(self.state)
            with self.move_lock:
                self.pending_move = info
                self.error_message = ""
        except Exception as e:
            print(f"AI error: {e}")
            with self.move_lock:
                self.pending_move = None
                self.error_message = f"AI Error: {e}"
        self.thinking = False

    def apply_move(self, move: Tuple[int, int], info: Optional[dict] = None):
        """Apply a move and update game state."""
        if move is None or move not in self.legal_moves:
            return
        
        self.last_move = move
        self.last_info = info
        
        # Record move
        player = "A" if self.state.active_player == 1 else "B"
        self.move_history.append({
            "ply": len(self.move_history),
            "player": player,
            "move": move,
            "info": info,
        })
        
        # Apply move
        self.state = self.state.apply_move(move)
        self.legal_moves = self.state.legal_moves()
        
        # Check for game over
        if self.state.is_terminal():
            self.game_over = True
            winner = self.state.winner()
            if winner == 1:
                self.winner_text = "Player A (Blue) Wins!"
            elif winner == -1:
                self.winner_text = "Player B (Red) Wins!"
            else:
                self.winner_text = "Draw!"
        else:
            self.check_ai_turn()

    def handle_board_click(self, pos: Tuple[int, int]):
        """Handle click on game board."""
        if self.game_over or self.thinking:
            return
        
        # Check if human's turn
        agent = self.agents[0] if self.state.active_player == 1 else self.agents[1]
        if agent is not None:
            return  # AI's turn
        
        # Convert screen position to board coordinates
        x, y = pos
        col = (x - BOARD_MARGIN) // CELL_SIZE
        row = (y - BOARD_MARGIN) // CELL_SIZE
        
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            move = (row, col)
            if move in self.legal_moves:
                self.apply_move(move, {"depth": 0, "nodes": 1, "time_s": 0.0, "value": 0.0, "cutoffs": 0})

    def draw_board(self):
        """Draw the game board."""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x = BOARD_MARGIN + col * CELL_SIZE
                y = BOARD_MARGIN + row * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                
                # Determine cell color
                cell = self.state.board.grid[row][col]
                if cell == "X":
                    color = COLOR_BLOCKED
                elif (row + col) % 2 == 0:
                    color = COLOR_BOARD_LIGHT
                else:
                    color = COLOR_BOARD_DARK
                
                pygame.draw.rect(self.screen, color, rect)
                
                # Highlight legal moves for human player
                agent = self.agents[0] if self.state.active_player == 1 else self.agents[1]
                if agent is None and (row, col) in self.legal_moves and not self.game_over:
                    highlight_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    highlight_surf.fill(COLOR_HIGHLIGHT)
                    self.screen.blit(highlight_surf, (x, y))
                
                # Highlight last move
                if self.last_move == (row, col):
                    pygame.draw.rect(self.screen, COLOR_LAST_MOVE, rect, width=3)
                
                # Draw players
                if cell == "A":
                    center = (x + CELL_SIZE // 2, y + CELL_SIZE // 2)
                    pygame.draw.circle(self.screen, COLOR_PLAYER_A, center, CELL_SIZE // 3)
                    text = FONT_MEDIUM.render("A", True, COLOR_TEXT)
                    text_rect = text.get_rect(center=center)
                    self.screen.blit(text, text_rect)
                elif cell == "B":
                    center = (x + CELL_SIZE // 2, y + CELL_SIZE // 2)
                    pygame.draw.circle(self.screen, COLOR_PLAYER_B, center, CELL_SIZE // 3)
                    text = FONT_MEDIUM.render("B", True, COLOR_TEXT)
                    text_rect = text.get_rect(center=center)
                    self.screen.blit(text, text_rect)
                
                # Draw grid lines
                pygame.draw.rect(self.screen, COLOR_BG, rect, width=1)

    def draw_panel(self):
        """Draw the info panel."""
        # Panel background
        panel_rect = pygame.Rect(PANEL_X - 10, BOARD_MARGIN - 10, 
                                 PANEL_WIDTH + 20, WINDOW_HEIGHT - BOARD_MARGIN * 2 + 20)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, panel_rect, border_radius=10)
        
        # Draw buttons first (they're below dropdowns when expanded)
        for btn in self.buttons:
            btn.draw(self.screen)
        
        y = BOARD_MARGIN + 210
        
        # Current turn
        if not self.game_over:
            turn_text = "Turn: Player " + ("A (Blue)" if self.state.active_player == 1 else "B (Red)")
            text = FONT_MEDIUM.render(turn_text, True, 
                                      COLOR_PLAYER_A if self.state.active_player == 1 else COLOR_PLAYER_B)
            self.screen.blit(text, (PANEL_X, y))
            y += 35
            
            if self.thinking:
                thinking_text = FONT_SMALL.render("AI thinking...", True, COLOR_TEXT_DIM)
                self.screen.blit(thinking_text, (PANEL_X, y))
            elif self.error_message:
                error_text = FONT_SMALL.render(self.error_message, True, COLOR_PLAYER_B)
                self.screen.blit(error_text, (PANEL_X, y))
            y += 30
        else:
            text = FONT_MEDIUM.render(self.winner_text, True, COLOR_TEXT)
            self.screen.blit(text, (PANEL_X, y))
            y += 50
        
        # Last move info
        if self.last_info:
            y += 10
            header = FONT_SMALL.render("Last Move Stats:", True, COLOR_TEXT)
            self.screen.blit(header, (PANEL_X, y))
            y += 25
            
            stats = [
                f"Move: {self.last_move}",
                f"Depth: {self.last_info.get('depth', 'N/A')}",
                f"Nodes: {self.last_info.get('nodes', 'N/A')}",
                f"Time: {self.last_info.get('time_s', 0):.3f}s",
            ]
            if 'simulations' in self.last_info:
                stats.append(f"Simulations: {self.last_info['simulations']}")
            if 'cutoffs' in self.last_info and self.last_info['cutoffs'] > 0:
                stats.append(f"Cutoffs: {self.last_info['cutoffs']}")
            
            for stat in stats:
                text = FONT_SMALL.render(stat, True, COLOR_TEXT_DIM)
                self.screen.blit(text, (PANEL_X, y))
                y += 22
        
        # Move history (scrollable)
        y += 20
        header = FONT_SMALL.render(f"Move History ({len(self.move_history)} moves):", True, COLOR_TEXT)
        self.screen.blit(header, (PANEL_X, y))
        y += 25
        
        # Show last 10 moves
        visible_moves = self.move_history[-10:]
        for entry in visible_moves:
            color = COLOR_PLAYER_A if entry["player"] == "A" else COLOR_PLAYER_B
            text = FONT_SMALL.render(f"{entry['ply']+1}. {entry['player']}: {entry['move']}", True, color)
            self.screen.blit(text, (PANEL_X, y))
            y += 20
        
        # Draw dropdowns LAST so they appear on top of everything else when expanded
        # Draw non-expanded dropdowns first, then expanded one on top
        expanded_dd = None
        for dd in self.dropdowns:
            if dd.expanded:
                expanded_dd = dd
            else:
                dd.draw(self.screen)
        # Draw expanded dropdown last so it's on top
        if expanded_dd:
            expanded_dd.draw(self.screen)

    def run(self):
        """Main game loop."""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Handle dropdown events first (they overlay other elements)
                for dd in self.dropdowns:
                    dd.handle_event(event)
                
                # Handle button events
                for btn in self.buttons:
                    btn.handle_event(event)
                
                # Handle board clicks
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check if click is on board
                    if (BOARD_MARGIN <= event.pos[0] < BOARD_MARGIN + BOARD_WIDTH and
                        BOARD_MARGIN <= event.pos[1] < BOARD_MARGIN + BOARD_HEIGHT):
                        self.handle_board_click(event.pos)
            
            # Check for pending AI move (thread-safe access)
            with self.move_lock:
                if self.pending_move is not None:
                    move = self.pending_move.get("move")
                    if move is not None:
                        self.apply_move(move, self.pending_move)
                    else:
                        # AI returned None move (shouldn't happen in valid game state)
                        self.error_message = "AI returned no valid move"
                    self.pending_move = None
            
            # Draw
            self.screen.fill(COLOR_BG)
            self.draw_board()
            self.draw_panel()
            
            # Title
            title = FONT_LARGE.render("Isolation", True, COLOR_TEXT)
            self.screen.blit(title, (BOARD_MARGIN, 10))
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()


def main():
    """Entry point for the GUI."""
    gui = IsolationGUI()
    gui.run()


if __name__ == "__main__":
    main()
