# =============================
# tcec_book_builder.py
# =============================
import requests
import zipfile
import io
import chess.pgn
import random
import os

# Configuration
TCEC_ZIP_URL = "https://github.com/TCEC-Chess/tcecgames/releases/download/S27-final/TCEC-everything-compact.zip"
OUTPUT_PGN = "tcec_polyglot_book.pgn"
MAX_HALF_MOVES = 80

# Download and extract PGN zip
print(f"⬇️ Downloading {TCEC_ZIP_URL}...")
resp = requests.get(TCEC_ZIP_URL)
resp.raise_for_status()

z = zipfile.ZipFile(io.BytesIO(resp.content))
print(f"📦 Extracted {len(z.namelist())} files from ZIP")

# Collect raw PGN entries
raw_games = []
for filename in z.namelist():
    if not filename.endswith(".pgn"):
        continue
    content = z.read(filename).decode("utf-8", errors="ignore")
    entries = content.strip().split("\n\n[Event")
    entries = ["[Event" + e if not e.startswith("[Event") else e for e in entries if e.strip()]
    raw_games.extend(entries)

print(f"🔍 Loaded {len(raw_games)} total games")

# Helper: sanitize game and truncate to max_half_moves
def sanitize_game(game: chess.pgn.Game, max_half_moves: int) -> str | None:
    board = game.board()
    new_game = chess.pgn.Game()
    node = new_game

    for i, move in enumerate(game.mainline_moves()):
        if i >= max_half_moves:
            break
        if not board.is_legal(move):
            return None
        try:
            board.push(move)
        except Exception:
            return None
        node = node.add_variation(move)

    new_game.headers.update(game.headers)
    return str(new_game)

# Final game list
final_games = []

for idx, pg in enumerate(raw_games):
    try:
        game = chess.pgn.read_game(io.StringIO(pg))
        if not game:
            continue

        variant = game.headers.get("Variant", "Standard").lower()
        if variant != "standard":
            continue

        board = game.board()
        legal = True
        for move in game.mainline_moves():
            if not board.is_legal(move):
                legal = False
                break
            board.push(move)

        if not legal or not board.is_checkmate():
            continue

        result = game.headers.get("Result", "")
        white = game.headers.get("White", "").lower()
        black = game.headers.get("Black", "").lower()

        if (result == "1-0" and "stockfish" in white) or (result == "0-1" and "stockfish" in black):
            trimmed = sanitize_game(game, MAX_HALF_MOVES)
            if trimmed:
                final_games.append(trimmed)

    except Exception:
        continue  # quietly skip malformed games

# Write valid PGNs to file
print(f"✅ Found {len(final_games)} valid Stockfish checkmate wins")
with open(OUTPUT_PGN, "w", encoding="utf-8") as f:
    for game in final_games:
        f.write(game + "\n\n")
print(f"📘 Written {len(final_games)} trimmed Stockfish wins to {OUTPUT_PGN}")


