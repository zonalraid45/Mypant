# scripts/trim_games.py
import chess.pgn
import io

input_file = "filtered_games.pgn"
output_file = "polyglot_book.pgn"
MAX_MOVES = 40

with open(input_file, "r", encoding="utf-8") as f:
    all_text = f.read()

games = all_text.strip().split("\n\n\n")
trimmed = []

for pgn_text in games:
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    board = game.board()
    new_game = chess.pgn.Game()
    node = new_game

    for i, move in enumerate(game.mainline_moves()):
        if i >= MAX_MOVES:
            break
        board.push(move)
        node = node.add_variation(move)

    trimmed.append(str(new_game))

with open(output_file, "w", encoding="utf-8") as f:
    for game in trimmed:
        f.write(game + "\n\n")
