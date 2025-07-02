# =============================
# tcec_book_builder.py (Polyglot-Safe Final Version)
# =============================
import requests
import zipfile
import io
import chess.pgn
import os

# Configuration
TCEC_ZIP_URL = "https://github.com/TCEC-Chess/tcecgames/releases/download/S27-final/TCEC-everything-compact.zip"
OUTPUT_PGN = "tcec_polyglot_book_cleaned.pgn"
MAX_HALF_MOVES = 80

# Step 1: Download and extract PGNs
print(f"⬇️ Downloading {TCEC_ZIP_URL}...")
resp = requests.get(TCEC_ZIP_URL)
resp.raise_for_status()

z = zipfile.ZipFile(io.BytesIO(resp.content))
print(f"📦 Extracted {len(z.namelist())} files from ZIP")

# Step 2: Collect raw PGN entries
raw_games = []
for filename in z.namelist():
    if not filename.endswith(".pgn"):
        continue
    content = z.read(filename).decode("utf-8", errors="ignore")
    entries = content.strip().split("\n\n[Event")
    entries = ["[Event" + e if not e.startswith("[Event") else e for e in entries if e.strip()]
    raw_games.extend(entries)

print(f"🔍 Loaded {len(raw_games)} total games")

# Step 3: Strict SAN validation + truncation + move identity check
def sanitize_game(game: chess.pgn.Game, max_half_moves: int) -> str | None:
    try:
        board = game.board()
        new_game = chess.pgn.Game()
        new_game.headers.update(game.headers)
        node = new_game

        curr = game
        half_moves = 0

        while curr.variations and half_moves < max_half_moves:
            move = curr.variations[0].move
            try:
                san = board.san(move)
                parsed = board.parse_san(san)
                if move != parsed:
                    return None  # Disallow ambiguous SAN like "Ne3" parsing wrong move
                if not board.is_legal(parsed):
                    return None
            except Exception:
                return None  # Corrupt SAN

            board.push(parsed)
            node = node.add_variation(parsed)
            curr = curr.variations[0]
            half_moves += 1

        return str(new_game)

    except Exception:
        return None

# Step 4: Filter & sanitize valid Stockfish checkmate wins
def is_stockfish(name: str) -> bool:
    name = name.lower()
    return "stockfish" in name or name.startswith("sf")

final_games = []

for idx, pg in enumerate(raw_games):
    try:
        game = chess.pgn.read_game(io.StringIO(pg))
        if not game:
            continue

        if game.headers.get("Variant", "Standard").lower() != "standard":
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
        white = game.headers.get("White", "")
        black = game.headers.get("Black", "")

        if (result == "1-0" and is_stockfish(white)) or (result == "0-1" and is_stockfish(black)):
            trimmed = sanitize_game(game, MAX_HALF_MOVES)
            if trimmed:
                final_games.append(trimmed)

    except Exception as e:
        print(f"⚠️ Skipped game {idx}: {e}")
        continue

# Step 5: Write initial PGN file
with open(OUTPUT_PGN, "w", encoding="utf-8") as f:
    for game in final_games:
        f.write(game.strip() + "\n\n")

print(f"✅ Written {len(final_games)} sanitized games to {OUTPUT_PGN}")

# Step 6: Final re-validation pass to remove remaining bad games
print("🔍 Performing final validation of PGN...")
validated_games = []
with open(OUTPUT_PGN, encoding="utf-8") as f:
    raw = f.read().strip().split("\n\n")

for idx, pg in enumerate(raw):
    try:
        game = chess.pgn.read_game(io.StringIO(pg))
        board = game.board()
        for move in game.mainline_moves():
            if not board.is_legal(move):
                raise ValueError("Illegal move")
            board.push(move)
        validated_games.append(pg)
    except Exception as e:
        print(f"❌ Removing game {idx}: {e}")

# Step 7: Overwrite PGN with only valid games
with open(OUTPUT_PGN, "w", encoding="utf-8") as f:
    for game in validated_games:
        f.write(game.strip() + "\n\n")

print(f"✅ Final validated PGN contains {len(validated_games)} games")


