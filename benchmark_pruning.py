"""
benchmark_pruning.py
=====================
Measures the impact of alpha-beta pruning on search speed and nodes
visited, for the report's "Analysis of pruning's impact on speed"
requirement.

It runs the AI's first move (empty board = worst case, largest tree)
and a mid-game position, with and without alpha-beta pruning, and
reports nodes visited + wall-clock time for each.

Run:
    python benchmark_pruning.py
"""

import time
from game_engine import TicTacToe, MinimaxAI, PLAYER_X, PLAYER_O


def time_move(board: TicTacToe, ai_symbol: str, use_alpha_beta: bool, max_depth=None):
    ai = MinimaxAI(ai_symbol=ai_symbol, use_alpha_beta=use_alpha_beta, max_depth=max_depth)
    start = time.perf_counter()
    move = ai.choose_move(board.copy())
    elapsed = time.perf_counter() - start
    return move, ai.nodes_visited, elapsed


def run_scenario(name: str, board: TicTacToe, ai_symbol: str, max_depth=None):
    print(f"\n=== {name} (max_depth={max_depth or 'full game'}) ===")
    _, nodes_no_ab, t_no_ab = time_move(board, ai_symbol, use_alpha_beta=False, max_depth=max_depth)
    _, nodes_ab, t_ab = time_move(board, ai_symbol, use_alpha_beta=True, max_depth=max_depth)

    reduction = (1 - nodes_ab / nodes_no_ab) * 100 if nodes_no_ab else 0
    speedup = (t_no_ab / t_ab) if t_ab > 0 else float("inf")

    print(f"  Without alpha-beta: {nodes_no_ab:>6} nodes, {t_no_ab*1000:8.2f} ms")
    print(f"  With    alpha-beta: {nodes_ab:>6} nodes, {t_ab*1000:8.2f} ms")
    print(f"  Node reduction:     {reduction:6.2f}%")
    print(f"  Speedup factor:     {speedup:6.2f}x")


def main():
    print("Alpha-Beta Pruning Impact Analysis")
    print("=" * 40)

    # Scenario 1: empty board, AI moves first (largest possible tree: 9!)
    empty_board = TicTacToe()
    run_scenario("Opening move, unbeatable (full-depth)", empty_board, PLAYER_X, max_depth=None)

    # Scenario 2: empty board, but depth-limited (Hard difficulty)
    empty_board2 = TicTacToe()
    run_scenario("Opening move, depth-limited (Hard, depth=5)", empty_board2, PLAYER_X, max_depth=5)

    # Scenario 3: mid-game position (smaller remaining tree)
    mid_board = TicTacToe()
    for idx, sym in [(0, "X"), (4, "O"), (1, "X")]:
        mid_board.make_move(idx, sym)
    run_scenario("Mid-game position (5 empty cells), unbeatable", mid_board, PLAYER_O, max_depth=None)


if __name__ == "__main__":
    main()
