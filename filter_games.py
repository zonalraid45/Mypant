import chess.pgn
import io

input_file = "raw_games.pgn"
output_file = "filtered_games.pgn"

with open(input_file, "r", encoding="utf-8") as f:
    all_text = f.read()

games = all_text.strip().split("\n\n[Event")
games = ["[Event" + g if not g.startswith("[Event") else g for g in games if g.strip()]
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

    if result == "1-0" and "bot" in black.lower() and black_elo >= 2900:
        filtered.append(pgn_text)
    elif result == "0-1" and "bot" in white.lower() and white_elo >= 2900:
        filtered.append(pgn_text)

print(f"Filtered {len(filtered)} games out of {len(games)}")

with open(output_file, "w", encoding="utf-8") as f:
    for game in filtered:
        f.write(game + "\n\n")
