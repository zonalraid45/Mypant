import requests
import json
import time

USERNAME = "Nikitosikbot_v2"
MAX_GAMES = 1550
OUTPUT_FILE = "raw_games.pgn"

headers = {
    "Accept": "application/x-ndjson"
}

params = {
    "max": MAX_GAMES,
    "pgnInJson": True,
    "rated": True,
    "perfType": "bullet,blitz,rapid,classical"
}

url = f"https://lichess.org/api/games/user/{USERNAME}"

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    with requests.get(url, headers=headers, params=params, stream=True) as r:
        for line in r.iter_lines():
            if line:
                try:
                    game_json = json.loads(line.decode("utf-8"))
                    if "pgn" in game_json:
                        f.write(game_json["pgn"] + "\n\n")
                except json.JSONDecodeError as e:
                    print("Failed to parse line:", line)
            time.sleep(0.1)
