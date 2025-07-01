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
    result = headers.get("Result", "")
    white = headers.get("White", "")
    black = headers.get("Black", "")
    white_elo = int(headers.get("WhiteElo", "0"))
    black_elo = int(headers.get("BlackElo", "0"))
    time_control = headers.get("TimeControl", "")

    # Skip games without valid time control
    if "+" not in time_control:
        continue

    try:
        base_time = int(time_control.split("+")[0])
    except ValueError:
        continue

    # Skip if time is less than 60 seconds (i.e. < 1+0)
    if base_time < 60:
        continue

    # Win against bot with ≥ 2900
    if result == "1-0" and "bot" in black.lower() and black_elo >= 2900:
        filtered.append(pgn_text)
    elif result == "0-1" and "bot" in white.lower() and white_elo >= 2900:
        filtered.append(pgn_text)

    # Draw with bot with ≥ 3180
    elif result == "1/2-1/2":
        if "bot" in black.lower() and black_elo >= 3180:
            filtered.append(pgn_text)
        elif "bot" in white.lower() and white_elo >= 3180:
            filtered.append(pgn_text)

print(f"Filtered {len(filtered)} games out of {len(games)}")

with open(output_file, "w", encoding="utf-8") as f:
    for game in filtered:
        f.write(game + "\n\n")
