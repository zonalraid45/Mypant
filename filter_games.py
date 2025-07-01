# scripts/filter_games.py
import chess.pgn
import io

input_file = "raw_games.pgn"
output_file = "filtered_games.pgn"

with open(input_file, "r", encoding="utf-8") as f:
    all_text = f.read()

games = all_text.strip().split("\n\n\n")
filtered = []

for pgn_text in games:
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    if not game:
        continue

    white = game.headers.get("White", "")
    black = game.headers.get("Black", "")
    result = game.headers.get("Result", "")
    white_elo = int(game.headers.get("WhiteElo", "0"))
    black_elo = int(game.headers.get("BlackElo", "0"))

    if result == "1-0" and black.endswith("bot") and black_elo >= 2950:
        filtered.append(pgn_text)
    elif result == "0-1" and white.endswith("bot") and white_elo >= 2950:
        filtered.append(pgn_text)

with open(output_file, "w", encoding="utf-8") as f:
    for game in filtered:
        f.write(game + "\n\n")
