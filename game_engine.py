"""
game_engine.py
==============
Core game logic and adversarial search (Minimax + Alpha-Beta Pruning)
for a 3x3 Tic-Tac-Toe AI player.

Author: Benjamin Fadhili
Project: AI Player for Tic-Tac-Toe (Adversarial Search / Minimax)

Design notes for the report
----------------------------
- The board is a flat list of 9 cells: indices 0-8, mapped like a
  telephone keypad:
        0 | 1 | 2
        --+---+--
        3 | 4 | 5
        --+---+--
        6 | 7 | 8
- 'X' is always the maximizing player, 'O' is always the minimizing
  player in the minimax tree (this is an internal convention; the
  human can be assigned either symbol at game start).
- Scoring convention:
        +10 - depth   -> win for X (maximizer)
        -10 + depth   -> win for O (minimizer)
              0        -> draw
  Subtracting/adding `depth` makes the AI prefer to win sooner and
  lose later (it "runs toward" fast wins and "delays" unavoidable
  losses), which is the standard trick used to make minimax play
  look intelligent rather than merely optimal.
- `max_depth` implements the "difficulty level by depth limit" task.
  When the search hits max_depth before the game is over, we use a
  lightweight heuristic evaluation instead of a terminal score, so
  the AI can still make a reasonable, fast decision at lower
  difficulties (i.e. it doesn't see far enough ahead to be perfect).
"""

from __future__ import annotations
import math
import random
from typing import List, Optional, Tuple

EMPTY = " "
PLAYER_X = "X"
PLAYER_O = "O"

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # cols
    (0, 4, 8), (2, 4, 6),              # diagonals
]


class TicTacToe:
    """Represents the Tic-Tac-Toe board and game rules."""

    def __init__(self):
        self.board: List[str] = [EMPTY] * 9

    def reset(self):
        self.board = [EMPTY] * 9

    def copy(self) -> "TicTacToe":
        clone = TicTacToe()
        clone.board = self.board[:]
        return clone

    def available_moves(self) -> List[int]:
        return [i for i, cell in enumerate(self.board) if cell == EMPTY]

    def make_move(self, index: int, symbol: str) -> bool:
        if self.board[index] != EMPTY:
            return False
        self.board[index] = symbol
        return True

    def undo_move(self, index: int):
        self.board[index] = EMPTY

    def winner(self) -> Optional[str]:
        """Returns 'X', 'O', 'Draw', or None (game still in progress)."""
        for a, b, c in WIN_LINES:
            if self.board[a] != EMPTY and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        if EMPTY not in self.board:
            return "Draw"
        return None

    def is_game_over(self) -> bool:
        return self.winner() is not None

    def winning_line(self) -> Optional[Tuple[int, int, int]]:
        """Returns the coordinates of the winning line, for UI highlighting."""
        for a, b, c in WIN_LINES:
            if self.board[a] != EMPTY and self.board[a] == self.board[b] == self.board[c]:
                return (a, b, c)
        return None

    def render(self) -> str:
        b = self.board
        rows = []
        for r in range(3):
            rows.append(" {} | {} | {} ".format(*b[r * 3:r * 3 + 3]))
        return "\n---+---+---\n".join(rows)


def _heuristic(board: TicTacToe) -> int:
    """
    Lightweight static evaluation used only when a depth-limited
    search is cut off before the game naturally ends. Rewards lines
    that are still 'open' (not blocked by the opponent) and weights
    them by how many of the player's own marks are already in them.
    This is NOT used for full-depth (unbeatable) play, only to give
    lower difficulty levels a sensible short-sighted heuristic.
    """
    score = 0
    for a, b, c in WIN_LINES:
        line = [board.board[a], board.board[b], board.board[c]]
        x_count = line.count(PLAYER_X)
        o_count = line.count(PLAYER_O)
        if x_count > 0 and o_count > 0:
            continue  # blocked line, worth nothing to either side
        if x_count == 2:
            score += 5
        elif x_count == 1:
            score += 1
        if o_count == 2:
            score -= 5
        elif o_count == 1:
            score -= 1
    return score


class MinimaxAI:
    """
    Adversarial search agent using Minimax with optional Alpha-Beta
    pruning and an optional depth limit (difficulty control).
    """

    def __init__(self, ai_symbol: str = PLAYER_O, use_alpha_beta: bool = True,
                 max_depth: Optional[int] = None):
        self.ai_symbol = ai_symbol
        self.human_symbol = PLAYER_O if ai_symbol == PLAYER_X else PLAYER_X
        self.use_alpha_beta = use_alpha_beta
        self.max_depth = max_depth   # None = search to the end of the game (unbeatable)
        self.nodes_visited = 0       # for pruning-impact analysis (Expected Outcome #4)

    # ---- public API -----------------------------------------------------

    def choose_move(self, board: TicTacToe) -> int:
        """Returns the index of the best move for self.ai_symbol."""
        self.nodes_visited = 0
        moves = board.available_moves()
        if not moves:
            raise ValueError("No available moves")

        best_score = -math.inf
        best_moves = []

        for move in moves:
            board.make_move(move, self.ai_symbol)
            score = self._minimax(
                board,
                depth=1,
                is_maximizing=False,
                alpha=-math.inf,
                beta=math.inf,
            )
            board.undo_move(move)

            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)

        # Break ties randomly so the AI isn't robotically predictable
        # among equally-good moves.
        return random.choice(best_moves)

    # ---- internals --------------------------------------------------------

    def _terminal_score(self, board: TicTacToe, depth: int) -> Optional[int]:
        result = board.winner()
        if result == self.ai_symbol:
            return 10 - depth
        if result == self.human_symbol:
            return -10 + depth
        if result == "Draw":
            return 0
        return None  # not terminal

    def _minimax(self, board: TicTacToe, depth: int, is_maximizing: bool,
                 alpha: float, beta: float) -> int:
        self.nodes_visited += 1

        terminal = self._terminal_score(board, depth)
        if terminal is not None:
            return terminal

        if self.max_depth is not None and depth >= self.max_depth:
            # Depth-limited cutoff: use heuristic instead of exact value.
            raw = _heuristic(board)
            return raw if self.ai_symbol == PLAYER_X else -raw

        moves = board.available_moves()

        if is_maximizing:
            best = -math.inf
            symbol = self.ai_symbol
            for move in moves:
                board.make_move(move, symbol)
                val = self._minimax(board, depth + 1, False, alpha, beta)
                board.undo_move(move)
                best = max(best, val)
                if self.use_alpha_beta:
                    alpha = max(alpha, best)
                    if beta <= alpha:
                        break  # beta cutoff
            return best
        else:
            best = math.inf
            symbol = self.human_symbol
            for move in moves:
                board.make_move(move, symbol)
                val = self._minimax(board, depth + 1, True, alpha, beta)
                board.undo_move(move)
                best = min(best, val)
                if self.use_alpha_beta:
                    beta = min(beta, best)
                    if beta <= alpha:
                        break  # alpha cutoff
            return best


# Convenience difficulty presets (Key Task: "Add difficulty levels by depth limit")
DIFFICULTY_PRESETS = {
    "Easy":   {"max_depth": 1, "use_alpha_beta": True},
    "Medium": {"max_depth": 3, "use_alpha_beta": True},
    "Hard":   {"max_depth": 5, "use_alpha_beta": True},
    "Unbeatable": {"max_depth": None, "use_alpha_beta": True},
}


def make_ai(difficulty: str, ai_symbol: str = PLAYER_O) -> MinimaxAI:
    preset = DIFFICULTY_PRESETS.get(difficulty, DIFFICULTY_PRESETS["Unbeatable"])
    return MinimaxAI(ai_symbol=ai_symbol, **preset)
