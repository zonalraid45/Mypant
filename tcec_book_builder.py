import requests
import zipfile
import io
import chess
import chess.pgn
import os

TCEC_ZIP_URL = "https://github.com/TCEC-Chess/tcecgames/releases/download/S27-final/TCEC-everything-compact.zip"
OUTPUT_PGN = "tcec_polyglot_book_cleaned.pgn"
MAX_HALF_MOVES = 80
SKIP_INDEXES = {960}  # skip game with illegal "Ne3" move

def download_tcec_zip():
    print(f"⬇️ Downloading {TCEC_ZIP_URL}...")
    resp = requests.get(TCEC_ZIP_URL)
    resp.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(resp.content))

def extract_pgn_games(z):
    raw_games = []
    for name in z.namelist():
        if name.endswith(".pgn"):
            data = z.read(name).decode("utf-8", errors="ignore")
            entries = data.strip().split("\n\n[Event")
            entries = ["[Event" + e if not e.startswith("[Event") else e for e in entries if e.strip()]
            raw_games.extend(entries)
    print(f"📦 Loaded {len(raw_games)} raw games")
    return raw_games

def is_stockfish(name: str) -> bool:
    name = name.lower()
    return "stockfish" in name or name.startswith("sf")

def safe_game_from_san(game: chess.pgn.Game, max_half_moves: int) -> str | None:
    try:
        board = chess.Board()
        new_game = chess.pgn.Game()
        new_game.headers.update(game.headers)
        node = new_game

        moves = list(game.mainline_moves())
        if len(moves) > max_half_moves:
            moves = moves[:max_half_moves]

        for move in moves:
            san = board.san(move)
            try:
                parsed = board.parse_san(san)
            except:
                return None
            if not board.is_legal(parsed):
                return None
            board.push(parsed)
            node = node.add_variation(parsed)

        return str(new_game)

    except Exception:
        return None

def filter_valid_games(raw_games):
    final = []
    for idx, raw in enumerate(raw_games):
        if idx in SKIP_INDEXES:
            print(f"🚫 Skipping known bad game {idx + 1}")
            continue

        try:
            game = chess.pgn.read_game(io.StringIO(raw))
            if not game:
                continue

            if game.headers.get("Variant", "Standard").lower() != "standard":
                continue

            result = game.headers.get("Result", "")
            white = game.headers.get("White", "")
            black = game.headers.get("Black", "")

            # include any Stockfish win (no checkmate required)
            if (result == "1-0" and is_stockfish(white)) or (result == "0-1" and is_stockfish(black)):
                # Validate full legality of moves
                board = game.board()
                for move in game.mainline_moves():
                    if not board.is_legal(move):
                        raise ValueError("Illegal move")
                    board.push(move)

                # Truncate and rebuild
                cleaned = safe_game_from_san(game, MAX_HALF_MOVES)
                if cleaned:
                    final.append(cleaned)

        except Exception as e:
            print(f"⚠️ Game {idx + 1} skipped: {e}")

    print(f"✅ Final filtered game count: {len(final)}")
    return final

def validate_final_pgn(pgn_path):
    print("🔍 Validating PGN after export...")
    valid = []
    with open(pgn_path, encoding="utf-8") as f:
        entries = f.read().strip().split("\n\n")
    for idx, g in enumerate(entries):
        try:
            game = chess.pgn.read_game(io.StringIO(g))
            board = game.board()
            for move in game.mainline_moves():
                if not board.is_legal(move):
                    raise ValueError(f"Illegal move {move}")
                board.push(move)
            valid.append(g)
        except Exception as e:
            print(f"❌ Game {idx + 1} invalid: {e}")
    with open(pgn_path, "w", encoding="utf-8") as f:
        for g in valid:
            f.write(g.strip() + "\n\n")
    print(f"✅ PGN validated: {len(valid)} games remain")

def main():
    z = download_tcec_zip()
    raw_games = extract_pgn_games(z)
    final_games = filter_valid_games(raw_games)

    with open(OUTPUT_PGN, "w", encoding="utf-8") as f:
        for g in final_games:
            f.write(g.strip() + "\n\n")

    validate_final_pgn(OUTPUT_PGN)
    print(f"📘 Final PGN ready: {OUTPUT_PGN}")

if __name__ == "__main__":
    main()


