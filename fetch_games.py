# scripts/fetch_games.py
import requests
import time

USERNAME = "Nikitosikbot_v2"
MAX_GAMES = 1000
OUTPUT_FILE = "raw_games.pgn"

headers = {"Accept": "application/x-ndjson"}
params = {
    "max": MAX_GAMES,
    "perfType": "ultraBullet,bullet,blitz,rapid,classical",
    "rated": True
}

url = f"https://lichess.org/api/games/user/{USERNAME}"

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    with requests.get(url, headers=headers, params=params, stream=True) as r:
        for line in r.iter_lines():
            if line:
                game_json = eval(line)
                f.write(game_json["pgn"] + "\n\n")
            time.sleep(0.1)
