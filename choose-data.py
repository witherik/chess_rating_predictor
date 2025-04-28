import chess.pgn
import numpy as np
import torch
from parameters import parameters


pgn_file_path, time_control = parameters()
pgn = open(pgn_file_path)

write_path = pgn_file_path + "_" + time_control + ".data"

offset = 0
data = open(write_path, "a")
data.close()
data = open(write_path, "r")
line = None
for line in data:
    pass
if line:
    _, _, offset = line.split()
    offset = int(offset)
data.close()

pgn.seek(offset)
total_games = 0

print("Starting at offset:", offset)


fen_dict = {
    "p": -1.0, "n": -2.5, "b": -3.0, "r": -5.0, "q": -9.0, "k": -18.0,
    "P": 1.0, "N": 2.5, "B": -3.0, "R": 5.0, "Q": 9.0, "K": 18.0
}


def board_to_tensor(fen: str):
    final_board = np.zeros((8, 8))
    split_board = fen.split('/')
    split_board[7] = split_board[7].split(' ')[0]
    for index, row in enumerate(split_board):
        print(row)
        if row[0] == '8':
            continue
        else:
            offset = 0
            for c in row:
                if c.isnumeric():
                    offset += int(c)
                else:
                    final_board[index][offset] = fen_dict[c]

    return torch.from_numpy(final_board)


def generate_tensors(mygame):
    white_moves = []
    white_evals = []
    black_moves = []
    black_evals = []
    white_to_move = True
    while mygame.next():
        mygame = mygame.next()
        if mygame.eval() != None:
            score = mygame.eval().white().score()
            board_to_tensor(mygame.board().fen())

        white_to_move = not white_to_move
    return


while True:
    offset = pgn.tell()
    headers = chess.pgn.read_headers(pgn)

    if headers is None:
        break

    if time_control == headers.get("TimeControl", "?"):
        pgn.seek(offset)
        mygame = chess.pgn.read_game(pgn)
        evaluation = mygame.next().eval()
        if evaluation != None:
            generate_tensors(mygame)
            # print(mygame)
