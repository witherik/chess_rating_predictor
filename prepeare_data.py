import numpy as np
import parameters
from read_games import read_games
import torch


def get_evals(game, max_centipawn=100000):
    evals = []
    while game.next():
        evaluation = game.eval()
        if evaluation != None:
            score = evaluation.white().score()
            if (evaluation.is_mate()):
                if evaluation.white().mate() > 0:
                    score = max_centipawn
                else:
                    score = -max_centipawn
            score = min(max_centipawn, score)
            score = max(-max_centipawn, score)
            evals.append(score)
        game = game.next()
    return evals


def get_scaled_deltas(evals, moves_bound=50, max_centipawn=1000, max_delta=300):
    last_cp = +30
    white_to_move = True
    w_deltas = [0] * moves_bound
    b_deltas = [0] * moves_bound
    for i in range(min(moves_bound*2, len(evals)-1)):
        delta = evals[i] - last_cp
        if white_to_move:
            delta = -delta

        delta = max(0, delta)

        avg = abs((evals[i] + last_cp)/2)
        weight = 1 - (avg**2/((max_centipawn*1.25) ** 2))
        delta *= weight

        delta = min(max_delta, delta)
        delta = int(delta)
        if white_to_move:
            w_deltas[i//2] = delta
        else:
            b_deltas[i//2] = delta
        last_cp = evals[i]
        white_to_move = not white_to_move
    return w_deltas, b_deltas


def get_deltas(evals):
    last_cp = +28
    white_to_move = True
    w_deltas = []
    b_deltas = []
    for i in range(len(evals)):
        delta = evals[i] - last_cp
        if white_to_move:
            delta = -delta

        delta = max(0, delta)
        delta = int(delta)
        if white_to_move:
            w_deltas.append(delta)
        else:
            b_deltas.append(delta)
        last_cp = evals[i]
        white_to_move = not white_to_move
    return w_deltas, b_deltas


def get_eval_pairs(evals):
    w_eval_pairs = np.zeros((50, 2))
    b_eval_pairs = np.zeros((50, 2))
    evals.insert(0, 28)
    white_to_move = True
    move = 0
    for i in range(1, min(50, len(evals))):
        if white_to_move:
            w_eval_pairs[move][0] = evals[i-1]
            w_eval_pairs[move][1] = evals[i]
        else:
            b_eval_pairs[move][0] = -evals[i-1]
            b_eval_pairs[move][1] = -evals[i]
            move += 1
        white_to_move = not white_to_move
    return w_eval_pairs, b_eval_pairs


def games_as_eval_pairs(file_path):
    for game in read_games(file_path):
        if game.next() is None:
            continue
        evaluation = game.next().eval()

        if evaluation is not None:
            game_evals = get_evals(game, max_centipawn=1000)
            get_eval_pairs(game_evals)
            print(game)


def games_as_eval_scaled_deltas(file_path):
    for game in read_games(file_path):
        headers = game.headers
        if game.next() is None or parameters.time_control != headers.get("TimeControl", "?"):
            continue
        evaluation = game.next().eval()
        white_rating = int(headers.get("WhiteElo"))
        black_rating = int(headers.get("BlackElo"))
        white_rating_diff = headers.get("WhiteRatingDiff")
        black_rating_diff = headers.get("BlackRatingDiff")
        if white_rating_diff is None or black_rating_diff is None:
            continue
        white_rating_diff = abs(int(white_rating_diff))
        black_rating_diff = abs(int(black_rating_diff))
        if min(white_rating_diff, black_rating_diff) <= 0 or max(white_rating_diff, black_rating_diff) > 30:
            continue
        if evaluation is not None:
            game_evals = get_evals(game, max_centipawn=1000)
            w_delta, b_delta = get_scaled_deltas(
                game_evals, parameters.moves_bound, parameters.max_centipawn, parameters.max_delta)
            yield w_delta, white_rating, b_delta, black_rating


def games_as_eval_deltas(file_path):
    for game in read_games(file_path):
        headers = game.headers
        if game.next() is None or parameters.time_control != headers.get("TimeControl", "?"):
            continue
        evaluation = game.next().eval()
        white_rating = int(headers.get("WhiteElo"))
        black_rating = int(headers.get("BlackElo"))
        white_rating_diff = headers.get("WhiteRatingDiff")
        black_rating_diff = headers.get("BlackRatingDiff")
        if white_rating_diff is None or black_rating_diff is None:
            continue
        white_rating_diff = abs(int(white_rating_diff))
        black_rating_diff = abs(int(black_rating_diff))
        if min(white_rating_diff, black_rating_diff) <= 0 or max(white_rating_diff, black_rating_diff) > 30:
            continue
        if evaluation is not None:
            game_evals = get_evals(game, max_centipawn=1000)
            w_delta, b_delta = get_deltas(game_evals)
            yield w_delta, white_rating, b_delta, black_rating


if __name__ == '__main__':
    for w_delta, _, b_delta, _ in games_as_eval_scaled_deltas(parameters.file_path):
        print(w_delta)
