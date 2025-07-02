import chess
import chess.polyglot

# === Config ===
BOOK_PATH = "engines/sfbook.bin"
SAN_MOVES = "e4 e5 Nf3 Nc6 Bb5"

# === Convert SAN to FEN ===
board = chess.Board()
for san in SAN_MOVES.split():
    try:
        board.push_san(san)
    except Exception as e:
        print(f"Invalid move '{san}': {e}")
        exit(1)

print("FEN:", board.fen())
print()

# === Query Polyglot book ===
try:
    with chess.polyglot.open_reader(BOOK_PATH) as reader:
        entries = list(reader.find_all(board))
        if not entries:
            print("No book moves found.")
        else:
            print("Recommended moves from book:")
            for entry in entries:
                move = board.san(entry.move)
                print(f"- {move} (weight {entry.weight}, learn {entry.learn})")
except FileNotFoundError:
    print(f"Book file not found: {BOOK_PATH}")
except Exception as e:
    print("Error reading book:", e)
