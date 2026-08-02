"""
cli_play.py
===========
Simple command-line interface to play Human vs AI in the terminal.
Useful for quick testing of game_engine.py without launching the
Streamlit app.

Run:
    python cli_play.py
"""

from game_engine import TicTacToe, make_ai, PLAYER_X, PLAYER_O, DIFFICULTY_PRESETS


def choose_symbol() -> str:
    choice = input("Play as X (goes first) or O (goes second)? [X/O]: ").strip().upper()
    return PLAYER_X if choice != "O" else PLAYER_O


def choose_difficulty() -> str:
    options = list(DIFFICULTY_PRESETS.keys())
    print("Choose difficulty:")
    for i, name in enumerate(options, 1):
        print(f"  {i}. {name}")
    raw = input(f"Enter 1-{len(options)}: ").strip()
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(options):
            return options[idx]
    except ValueError:
        pass
    return "Unbeatable"


def main():
    print("=== Tic-Tac-Toe: Human vs Minimax AI ===\n")
    human_symbol = choose_symbol()
    ai_symbol = PLAYER_O if human_symbol == PLAYER_X else PLAYER_X
    difficulty = choose_difficulty()
    ai = make_ai(difficulty, ai_symbol=ai_symbol)

    game = TicTacToe()
    current = PLAYER_X  # X always starts, per standard rules

    print(f"\nYou are '{human_symbol}'. AI is '{ai_symbol}' playing at '{difficulty}' difficulty.")
    print("Board positions are numbered 0-8, left-to-right, top-to-bottom.\n")

    while not game.is_game_over():
        print(game.render())
        print()
        if current == human_symbol:
            valid = False
            while not valid:
                raw = input("Your move (0-8): ").strip()
                if raw.isdigit() and int(raw) in game.available_moves():
                    game.make_move(int(raw), human_symbol)
                    valid = True
                else:
                    print("Invalid move, try again.")
        else:
            move = ai.choose_move(game)
            game.make_move(move, ai_symbol)
            print(f"AI ({difficulty}) plays {move}. [nodes evaluated: {ai.nodes_visited}]")

        current = PLAYER_O if current == PLAYER_X else PLAYER_X

    print(game.render())
    result = game.winner()
    print()
    if result == "Draw":
        print("Result: It's a draw!")
    elif result == human_symbol:
        print("Result: You win! 🎉")
    else:
        print("Result: AI wins.")


if __name__ == "__main__":
    main()
