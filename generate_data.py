import chess
import chess.pgn
import chess.engine
import numpy as np
import pickle
from parameters import parameters

pgn_file_path, time_control, max_centipawn, max_delta, moves_bound, bin_size = parameters()


def get_evals(mygame):
    evals = []

    while mygame.next():
        evaluation = mygame.eval()
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
        mygame = mygame.next()
    return evals


def get_eval_pairs(evals):
    w_eval_pairs = np.zeros((50, 2))
    b_eval_pairs = np.zeros((50, 2))
    evals.insert(0, 30)
    white_to_move = True
    # print(evals)
    move = 0
    for i in range(1, min(moves_bound, len(evals))):
        if white_to_move:
            w_eval_pairs[move][0] = evals[i-1]
            w_eval_pairs[move][1] = evals[i]
        else:
            b_eval_pairs[move][0] = -evals[i-1]
            b_eval_pairs[move][1] = -evals[i]
            move += 1
        white_to_move = not white_to_move
    return w_eval_pairs, b_eval_pairs


def get_deltas(evals):
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


if __name__ == "__main__":
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
    bins = [[] for _ in range(10)]
    ranges = [(800, 1339), (1340, 1429), (1430, 1492), (1493, 1541), (1542, 1593),
              (1594, 1647), (1648, 1706), (1706, 1773), (1774, 1870), (1871, 2341)]
    counts = [0]*10
    while min(counts) < bin_size:
        offset = pgn.tell()
        headers = chess.pgn.read_headers(pgn)

        if headers is None:
            break

        if time_control == headers.get("TimeControl", "?"):
            pgn.seek(offset)
            mygame = chess.pgn.read_game(pgn)
            if mygame.next() is None:
                continue
            evaluation = mygame.next().eval()
            white_rating = int(headers.get("WhiteElo"))
            black_rating = int(headers.get("BlackElo"))
            white_rating_diff = headers.get("WhiteRatingDiff")
            black_rating_diff = headers.get("BlackRatingDiff")
            if white_rating_diff is None or black_rating_diff is None:
                continue
            white_rating_diff = abs(int(white_rating_diff))
            black_rating_diff = abs(int(black_rating_diff))
            if min(white_rating_diff, black_rating_diff) <= 0 or min(white_rating_diff, black_rating_diff) / max(white_rating_diff, black_rating_diff) < 0.25:
                continue
            if evaluation != None:
                evals = get_evals(mygame)
                deltas = get_deltas(evals)
                # moves = get_eval_pairs(evals)
                # w_moves = moves[0]
                # b_moves = moves[1]
                w_deltas = deltas[0]
                b_deltas = deltas[1]
                for i, r in enumerate(ranges):
                    if counts[i] >= bin_size:
                        continue
                    if white_rating >= r[0] and white_rating <= r[1]:
                        bins[i].append([white_rating, w_deltas])
                        counts[i] += 1
                        # print(len(w_deltas))
                    if counts[i] >= bin_size:
                        continue
                    if black_rating >= r[0] and black_rating <= r[1]:
                        bins[i].append([black_rating, b_deltas])
                        counts[i] += 1
                        # print(len(b_deltas))
                print(counts)
                # print(mygame)
                # print(w_deltas)
                # print(b_deltas)

    new_bins = []
    for b in bins:
        new_bins.append(b[:bin_size])

    with open('classified_data_2.pkl', 'wb') as filehandle:
        pickle.dump(new_bins, filehandle)
