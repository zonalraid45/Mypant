import requests
import zipfile
import io
import chess.pgn
import random
import os

# Download and extract TCEC PGNs
TCEC_ZIP_URL = "https://github.com/TCEC-Chess/tcecgames/releases/download/S27-final/TCEC-everything-compact.zip"
OUTPUT_PGN = "tcec_polyglot_book.pgn"
MAX_HALF_MOVES = 80

print(f"⬇️ Downloading {TCEC_ZIP_URL}...")
resp = requests.get(TCEC_ZIP_URL)
resp.raise_for_status()

z = zipfile.ZipFile(io.BytesIO(resp.content))
print(f"📦 Extracted {len(z.namelist())} files from ZIP")

# Filter only PGNs containing Stockfish wins by checkmate
raw_games = []
for filename in z.namelist():
    if not filename.endswith(".pgn"):
        continue
    content = z.read(filename).decode("utf-8")
    entries = content.strip().split("\n\n[Event")
    entries = ["[Event" + e if not e.startswith("[Event") else e for e in entries if e.strip()]
    raw_games.extend(entries)

print(f"🔍 Loaded {len(raw_games)} total games from all PGNs")

def sanitize_game(game: chess.pgn.Game, max_half_moves: int) -> str | None:
    board = game.board()
    new_game = chess.pgn.Game()
    node = new_game

    for i, move in enumerate(game.mainline_moves()):
        if i >= max_half_moves:
            break
        try:
            if not board.is_legal(move):
                return None  # illegal move, skip game
            board.push(move)
        except Exception:
            return None  # malformed move, skip game
        node = node.add_variation(move)

    new_game.headers.update(game.headers)
    return str(new_game)

# Filter Stockfish wins by checkmate (excluding Fischer Random Chess)
final_games = []
for pg in raw_games:
    try:
        game = chess.pgn.read_game(io.StringIO(pg))
        if not game:
            continue

        variant = game.headers.get("Variant", "Standard")
        if variant.lower() != "standard":
            continue

        board = game.board()
        for move in game.mainline_moves():
            if not board.is_legal(move):
                raise ValueError("Illegal move found")
            board.push(move)

        is_mate = board.is_checkmate()
        white = game.headers.get("White", "").lower()
        black = game.headers.get("Black", "").lower()
        result = game.headers.get("Result", "")

        if is_mate and (("stockfish" in white and result == "1-0") or ("stockfish" in black and result == "0-1")):
            trimmed = sanitize_game(game, MAX_HALF_MOVES)
            if trimmed:
                final_games.append(trimmed)
    except Exception as e:
        continue  # skip broken games

print(f"✅ Found {len(final_games)} valid Stockfish checkmate wins")

with open(OUTPUT_PGN, "w", encoding="utf-8") as f:
    for game in final_games:
        f.write(game + "\n\n")

print(f"📘 Written {len(final_games)} trimmed Stockfish wins to {OUTPUT_PGN}")

