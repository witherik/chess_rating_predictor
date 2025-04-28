import chess.pgn
import numpy as np
import parameters
import prepeare_data
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

bin_size = 40


def generate_bins():
    ranges = [(400, 900), (901, 1125), (1126, 1250), (1251, 1375), (1376, 1500),
              (1501, 1600), (1601, 1700), (1701, 1850), (1851, 2000), (2001, 2800)]
    counts = [0]*10
    bins = [[] for _ in range(10)]
    datapoints = []
    labels = []
    total = 0
    for w_deltas, w_rating, b_deltas, b_rating in prepeare_data.games_as_eval_scaled_deltas(parameters.file_path):
        # print(len(w_deltas))
        for i, r in enumerate(ranges):
            if w_rating >= r[0] and w_rating <= r[1]:
                datapoints.append(w_deltas)
                labels.append(i)
                counts[i] += 1
            if b_rating >= r[0] and b_rating <= r[1]:
                datapoints.append(b_deltas)
                labels.append(i)
                counts[i] += 1
        total += 1
        if total >= 100 and total % 100 == 0:
            print(counts)
        if min(counts) >= bin_size:
            break
    with open('bins.pkl', 'wb') as filehandle:
        pickle.dump((datapoints, labels), filehandle)
    return datapoints, labels


datapoints, labels = generate_bins()
# with open('bins.pkl', 'rb') as filehandle:
#     bins = pickle.load(filehandle)
