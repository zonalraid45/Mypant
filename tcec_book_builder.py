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
games = []
for filename in z.namelist():
    if filename.endswith(".pgn"):
        content = z.read(filename).decode("utf-8")
        raw_games = content.strip().split("\n\n[Event")
        raw_games = ["[Event" + g if not g.startswith("[Event") else g for g in raw_games if g.strip()]
        for pg in raw_games:
            game = chess.pgn.read_game(io.StringIO(pg))
            if not game:
                continue
            board = game.board()
            for move in game.mainline_moves():
                board.push(move)
            is_mate = board.is_checkmate()

            white = game.headers.get("White", "").lower()
            black = game.headers.get("Black", "").lower()
            result = game.headers.get("Result", "")

            # Stockfish won by checkmate
            if is_mate and (("stockfish" in white and result == "1-0") or ("stockfish" in black and result == "0-1")):
                games.append(pg)

print(f"✅ Found {len(games)} Stockfish checkmate wins")

random.shuffle(games)
trimmed = []
for pg in games:
    game = chess.pgn.read_game(io.StringIO(pg))
    if not game:
        continue
    board = game.board()
    new_game = chess.pgn.Game()
    node = new_game
    for i, move in enumerate(game.mainline_moves()):
        if i >= MAX_HALF_MOVES:
            break
        board.push(move)
        node = node.add_variation(move)
    new_game.headers.update(game.headers)
    trimmed.append(str(new_game))

with open(OUTPUT_PGN, "w", encoding="utf-8") as f:
    for game in trimmed:
        f.write(game + "\n\n")

print(f"📘 Written {len(trimmed)} trimmed Stockfish wins to {OUTPUT_PGN}")
