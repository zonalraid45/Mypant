import chess.pgn
import io
import random

input_file = "filtered_games.pgn"
output_file = "polyglot_book.pgn"
MAX_MOVES = 80
BOOST_ELO = 3000

with open(input_file, "r", encoding="utf-8") as f:
    all_text = f.read()

# Split into individual PGN games
games = all_text.strip().split("\n\n[Event")
games = ["[Event" + g if not g.startswith("[Event") else g for g in games if g.strip()]
random.shuffle(games)
trimmed = []

for pgn_text in games:
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    if not game:
        continue

    headers = game.headers
    result = headers.get("Result", "")
    white = headers.get("White", "")
    black = headers.get("Black", "")
    white_elo = int(headers.get("WhiteElo", "0"))
    black_elo = int(headers.get("BlackElo", "0"))

    # Reconstruct board and detect checkmate from final position
    board = game.board()
    for move in game.mainline_moves():
        board.push(move)
    is_checkmate = board.is_checkmate()

    # Rebuild trimmed game
    board = game.board()
    new_game = chess.pgn.Game()
    node = new_game
    for i, move in enumerate(game.mainline_moves()):
        if i >= MAX_MOVES:
            break
        board.push(move)
        node = node.add_variation(move)
    new_game.headers.update(headers)
    game_str = str(new_game)

    # Boost weight for wins vs 3000+ bots by checkmate
    copies = 1
    if result == "1-0" and "bot" in black.lower() and black_elo >= BOOST_ELO and is_checkmate:
        copies = random.randint(2, 3)
    elif result == "0-1" and "bot" in white.lower() and white_elo >= BOOST_ELO and is_checkmate:
        copies = random.randint(2, 3)

    for _ in range(copies):
        trimmed.append(game_str)

print(f"✅ Wrote {len(trimmed)} trimmed entries to {output_file}")

with open(output_file, "w", encoding="utf-8") as f:
    for game in trimmed:
        f.write(game + "\n\n")
