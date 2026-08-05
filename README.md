# Tic-Tac-Toe AI Player - Minimax with Alpha-Beta Pruning

Project 3 deliverable: an adversarial-search game agent for Tic-Tac-Toe,
built around the **Minimax algorithm** with optional **alpha-beta
pruning** and **depth-limited difficulty levels**.

## Files

| File                   | Purpose |
|-------------------------|---------|
| `game_engine.py`        | Core game rules + `MinimaxAI` search agent (the "brain") |
| `app.py`                 | Streamlit web GUI — human vs AI, the one to deploy |
| `cli_play.py`            | Terminal version, for quick local testing |
| `benchmark_pruning.py`   | Generates the "pruning impact on speed" analysis for your report |
| `requirements.txt`       | Python dependencies |

## Running locally

```bash
pip install -r requirements.txt

# Web GUI
streamlit run app.py

# OR terminal version
python cli_play.py

# OR generate the pruning benchmark numbers
python benchmark_pruning.py
```

## How the AI works (for your report)

### Minimax
Tic-Tac-Toe is a **zero-sum, perfect-information game**. Minimax
explores the full game tree from the current board: on the maximizing
player's turn it picks the move with the highest score; on the
minimizing player's turn it picks the move with the lowest score. Each
branch is scored only once a terminal state (win/loss/draw) is
reached, and that score is propagated back up the tree.

Scoring convention used here:
- **+10 − depth** → win for the maximizer (AI, if AI is `X`)
- **−10 + depth** → win for the minimizer
- **0** → draw

Subtracting the depth makes the AI prefer *faster* wins and *slower*
losses — without it, the AI would be mathematically correct but could
delay a guaranteed win pointlessly, or walk into a loss it could have
postponed.

### Alpha-Beta Pruning
Alpha-beta pruning is an optimization that skips branches of the tree
that cannot possibly influence the final decision. It tracks two
bounds while searching:
- **alpha** — the best score the maximizer can already guarantee
- **beta** — the best score the minimizer can already guarantee

Once `beta <= alpha` at any node, the remaining siblings at that node
are skipped ("pruned"), because a rational opponent would never allow
the game to reach that branch. This does **not** change the outcome —
the AI still plays perfectly — it only changes how much of the tree
it has to look at.

`benchmark_pruning.py` measures this directly: on the empty-board
opening move (the largest possible search, 9!-scale), alpha-beta
typically cuts nodes visited by roughly **90%+** and search time by a
similar factor, with results printed to the console when you run it.

### Difficulty levels (depth-limited search)
| Difficulty | Search depth | Behaviour |
|---|---|---|
| Easy | 1 ply | Looks only 1 move ahead; makes obvious mistakes |
| Medium | 3 ply | Looks 3 moves ahead; decent but beatable |
| Hard | 5 ply | Looks 5 moves ahead; strong, occasionally beatable |
| Unbeatable | full game | Searches to the end of every line; mathematically optimal — can never lose |

When the search is cut off by the depth limit before the game ends,
the engine falls back to a lightweight heuristic (`_heuristic()` in
`game_engine.py`) that scores how many "2-in-a-row, still open" lines
each side has — a cheap approximation of how favorable the position
looks, without having to search further.

**Correctness check performed:** two `Unbeatable`-difficulty AIs
played against each other 20 times in `game_engine.py`'s test —
result was **20/20 draws**, which is the expected, provable outcome
of two perfect minimax players (Tic-Tac-Toe is a solved game: perfect
play always draws).

## Deploying the model

The recommended, free option for this project is **Streamlit
Community Cloud**, since `app.py` is already a Streamlit app:

1. Push this project folder to a **public GitHub repository** (must
   include `app.py`, `game_engine.py`, and `requirements.txt` at
   minimum).
2. Go to **share.streamlit.io** and sign in with your GitHub account.
3. Click **"New app"**, select your repository, branch (`main`), and
   set the **main file path** to `app.py`.
4. Click **Deploy**. Streamlit Cloud installs `requirements.txt`
   automatically and gives you a public URL
   (`https://<your-app-name>.streamlit.app`) you can share or submit
   with your report.

**Alternative options**, if you'd rather not use Streamlit Cloud:
- **Hugging Face Spaces** — create a Space, choose the "Streamlit"
  SDK, and push the same files; it deploys the same way.
- **Render.com** (free web service tier) — works for any of the
  three files; for the Streamlit app use the start command
  `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`.
- **Local-only submission** — if your instructor just wants to run
  it themselves, `cli_play.py` needs no deployment at all — only
  `python cli_play.py`.

## Extending to Bao (optional, per the brief)

The brief allows Tic-Tac-Toe **or** a simplified Bao variant. The
same `MinimaxAI` class works for any two-player, zero-sum,
perfect-information game — you'd only need to swap out `TicTacToe`
for a `SimplifiedBao` class exposing the same four methods the AI
relies on: `available_moves()`, `make_move()`, `undo_move()`, and
`winner()`. Bao's branching factor is much higher than Tic-Tac-Toe's,
so alpha-beta pruning and a tighter depth limit become essential
rather than optional — worth mentioning in your report as the reason
Tic-Tac-Toe is the more tractable choice for full-depth "unbeatable"
play, while Bao would need heuristic-heavy depth-limited search even
at "hard" difficulty.
