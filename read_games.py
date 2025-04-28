import chess.pgn
import numpy as np
import parameters


def read_games(file_path) -> chess.pgn.Game:
    pgn = open(file_path)
    while True:
        offset = pgn.tell()
        headers = chess.pgn.read_headers(pgn)
        if headers is None:
            break
        pgn.seek(offset)
        mygame = chess.pgn.read_game(pgn)
        yield mygame


if __name__ == '__main__':
    for game in read_games(parameters.file_path):
        print(game)
