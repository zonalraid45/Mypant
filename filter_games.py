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

    headers = game.headers
    white = headers.get("White", "")
    black = headers.get("Black", "")
    result = headers.get("Result", "")
    white_elo = int(headers.get("WhiteElo", "0"))
    black_elo = int(headers.get("BlackElo", "0"))

    # Win against a 2950+ rated bot
    if result == "1-0" and black.endswith("bot") and black_elo >= 2950:
        filtered.append(pgn_text)
    elif result == "0-1" and white.endswith("bot") and white_elo >= 2950:
        filtered.append(pgn_text)

with open(output_file, "w", encoding="utf-8") as f:
    for game in filtered:
        f.write(game + "\n\n")
