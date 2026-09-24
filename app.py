"""
app.py
======
Streamlit web GUI for the Tic-Tac-Toe Minimax AI.

Run locally:
    streamlit run app.py

Deploy:
    See README.md -> "Deployment" section (Streamlit Community Cloud
    is the recommended free option for this app).
"""

import time
import streamlit as st

from game_engine import TicTacToe, make_ai, PLAYER_X, PLAYER_O, DIFFICULTY_PRESETS

st.set_page_config(page_title="Tic-Tac-Toe AI (Minimax)", page_icon="❌", layout="centered")

# Session state initialisation
def new_game(human_symbol: str, difficulty: str):
    st.session_state.game = TicTacToe()
    st.session_state.human_symbol = human_symbol
    st.session_state.ai_symbol = PLAYER_O if human_symbol == PLAYER_X else PLAYER_X
    st.session_state.difficulty = difficulty
    st.session_state.ai = make_ai(difficulty, ai_symbol=st.session_state.ai_symbol)
    st.session_state.current = PLAYER_X  # X always moves first
    st.session_state.last_nodes = 0
    st.session_state.last_time_ms = 0
    st.session_state.history = []  # list of (mover, move, nodes, time_ms) for the report


if "game" not in st.session_state:
    new_game(PLAYER_X, "Unbeatable")

# Sidebar: settings
with st.sidebar:
    st.header("Game Settings")
    symbol_choice = st.radio("Play as", ["X (first)", "O (second)"], index=0)
    difficulty_choice = st.select_slider(
        "Difficulty (search depth limit)",
        options=list(DIFFICULTY_PRESETS.keys()),
        value=st.session_state.difficulty,
    )
    use_alpha_beta = st.checkbox("Use alpha-beta pruning", value=True)

    if st.button("🔄 New Game", use_container_width=True):
        human_symbol = PLAYER_X if symbol_choice.startswith("X") else PLAYER_O
        new_game(human_symbol, difficulty_choice)
        st.session_state.ai.use_alpha_beta = use_alpha_beta
        st.rerun()

    st.divider()
    st.markdown("### Search Stats (last AI move)")
    st.metric("Nodes evaluated", st.session_state.last_nodes)
    st.metric("Time taken (ms)", st.session_state.last_time_ms)

    st.divider()
    st.caption(
        "**Difficulty presets** map to a minimax search depth limit:\n\n"
        + "\n".join(f"- **{k}** → depth = {v['max_depth'] or 'full game'}"
                     for k, v in DIFFICULTY_PRESETS.items())
    )

# Header
st.title("❌⭕ Tic-Tac-Toe — Minimax AI")
st.caption(
    "An adversarial-search game agent built with the Minimax algorithm "
    "(optional alpha-beta pruning) and depth-limited difficulty levels."
)

game = st.session_state.game
human_symbol = st.session_state.human_symbol
ai_symbol = st.session_state.ai_symbol

status_placeholder = st.empty()

# AI move (if it's the AI's turn and the game isn't over)
def ai_take_turn():
    ai = st.session_state.ai
    ai.use_alpha_beta = use_alpha_beta
    start = time.time()
    move = ai.choose_move(game)
    elapsed_ms = round((time.time() - start) * 1000, 2)
    game.make_move(move, ai_symbol)
    st.session_state.last_nodes = ai.nodes_visited
    st.session_state.last_time_ms = elapsed_ms
    st.session_state.history.append(("AI", move, ai.nodes_visited, elapsed_ms))
    st.session_state.current = PLAYER_O if st.session_state.current == PLAYER_X else PLAYER_X


if (not game.is_game_over()) and st.session_state.current == ai_symbol:
    with st.spinner("AI is thinking..."):
        ai_take_turn()
    st.rerun()

# Board rendering
winning_line = game.winning_line()

def cell_label(i):
    val = game.board[i]
    return val if val != " " else ""

cols_container = st.container()
for row in range(3):
    cols = cols_container.columns(3, gap="small")
    for col_i in range(3):
        idx = row * 3 + col_i
        label = cell_label(idx)
        disabled = (
            game.board[idx] != " "
            or game.is_game_over()
            or st.session_state.current != human_symbol
        )
        button_type = "primary" if winning_line and idx in winning_line else "secondary"
        if cols[col_i].button(
            label if label else " ",
            key=f"cell_{idx}",
            disabled=disabled,
            use_container_width=True,
            type=button_type,
        ):
            game.make_move(idx, human_symbol)
            st.session_state.history.append(("Human", idx, None, None))
            st.session_state.current = PLAYER_O if st.session_state.current == PLAYER_X else PLAYER_X
            st.rerun()


# Status / result

result = game.winner()
if result is None:
    turn_owner = "You" if st.session_state.current == human_symbol else "AI"
    status_placeholder.info(f"Turn: **{turn_owner}** ({st.session_state.current})")
elif result == "Draw":
    status_placeholder.warning("It's a draw!")
elif result == human_symbol:
    status_placeholder.success("You win! 🎉")
else:
    status_placeholder.error("AI wins.")


# Move history (useful for the "demo games" report requirement)

with st.expander("📜 Move history / demo log"):
    if not st.session_state.history:
        st.write("No moves yet.")
    else:
        for i, (mover, move, nodes, t) in enumerate(st.session_state.history, 1):
            if mover == "AI":
                st.write(f"{i}. AI played cell {move} — {nodes} nodes evaluated in {t} ms")
            else:
                st.write(f"{i}. Human played cell {move}")
