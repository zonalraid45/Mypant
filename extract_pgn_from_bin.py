# extract_all_pgn_from_bin.py

import chess
import chess.pgn
from chess.polyglot import open_reader
import threading
import time

book_path   = "engines/Optical.bin"
output_pgn  = "engines/Optical.pgn"

MAX_DEPTH     = 100
LOG_INTERVAL  = 100
MAX_BRANCHES  = 15

games_written = 0
lines         = []

# Background logger
def keep_alive_logger():
    while True:
        print(f"⏳ Still working... {games_written} PGN lines written", flush=True)
        time.sleep(30)

threading.Thread(target=keep_alive_logger, daemon=True).start()

# Build all possible lines up to MAX_DEPTH
def build_lines(book_path, max_depth=MAX_DEPTH):
    def dfs(board, moves_so_far, depth):
        if depth >= max_depth:
            lines.append(moves_so_far[:])
            return

        with open_reader(book_path) as reader:
            entries = list(reader.find_all(board))

        if not entries:
            lines.append(moves_so_far[:])
            return

        for entry in entries[:MAX_BRANCHES]:
            move = entry.move
            board.push(move)
            dfs(board, moves_so_far + [move], depth + 1)
            board.pop()

    dfs(chess.Board(), [], 0)

# Write PGN from lines
def write_pgn(lines, output_file):
    global games_written
    with open(output_file, "w", encoding="utf-8") as f:
        for line in lines:
            board = chess.Board()
            game  = chess.pgn.Game()
            game.headers["Event"] = "All lines from Optical.bin"
            node = game

            for move in line:
                node = node.add_variation(move)
                board.push(move)

            print(game, file=f, end="\n\n")
            games_written += 1

            if games_written % LOG_INTERVAL == 0:
                print(f"📝 Written {games_written} PGN games", flush=True)

# Run
print("🚀 Starting full PGN extraction from Optical.bin...", flush=True)
build_lines(book_path)
print(f"🔍 Found {len(lines)} full-length lines", flush=True)
write_pgn(lines, output_pgn)
print(f"✅ Done! Extracted {games_written} PGN games to {output_pgn}", flush=True)
