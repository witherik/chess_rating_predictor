import chess.pgn
import numpy as np
import parameters
import prepeare_data
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

bin_size = 5000


def generate_bins():
    ranges = [(800, 1339), (1340, 1429), (1430, 1492), (1493, 1541), (1542, 1593),
              (1594, 1647), (1648, 1706), (1706, 1773), (1774, 1870), (1871, 2341)]
    counts = [0]*10
    bins = [[] for _ in range(10)]

    for w_deltas, w_rating, b_deltas, b_rating in prepeare_data.games_as_eval_deltas(parameters.file_path):
        w_blunders = 0
        b_blunders = 0
        w_first_mistake = len(w_deltas)
        b_first_mistake = len(b_deltas)
        w_first_blunder = len(w_deltas)
        b_first_blunder = len(b_deltas)
        for move, delta in enumerate(w_deltas):
            if delta >= 300:
                if w_blunders == 0:
                    w_first_blunder = move
                w_blunders += 1
            if 100 < delta and delta < 300:
                w_first_mistake = min(w_first_mistake, move)
        for move, delta in enumerate(b_deltas):
            if delta >= 300:
                if b_blunders == 0:
                    b_first_blunder = move
                b_blunders += 1
            if 100 < delta and delta < 300:
                b_first_mistake = min(b_first_mistake, move)
        for i, r in enumerate(ranges):
            if counts[i] >= bin_size:
                continue
            if w_rating >= r[0] and w_rating <= r[1]:
                bins[i].append([w_rating, w_first_blunder,
                                w_first_mistake, w_blunders, len(w_deltas)])
                counts[i] += 1
            if counts[i] >= bin_size:
                continue
            if b_rating >= r[0] and b_rating <= r[1]:
                bins[i].append([b_rating, b_first_blunder,
                                b_first_mistake, b_blunders, len(b_deltas)])
                counts[i] += 1
        if min(counts) % 100 == 0:
            print(counts)
        if min(counts) >= bin_size:
            break
    with open('bins.pkl', 'wb') as filehandle:
        pickle.dump(bins, filehandle)
    return bins


# bins = generate_bins()
with open('bins.pkl', 'rb') as filehandle:
    bins = pickle.load(filehandle)

first_blunder = np.zeros((bin_size, 10))
first_mistake = np.zeros((bin_size, 10))
total_blunder = np.zeros((bin_size, 10))
game_len = np.zeros((bin_size, 10))
for i, l in enumerate(bins):

    out = [sum(row[i] for row in l) for i in range(len(l[0]))]
    print(
        f"Avg First Blunder {out[1]/bin_size}, Avg First Mistake {out[2]/bin_size}, Avg Total Blunder {out[3]/bin_size}, Avg Game Len {out[4]/bin_size}")

    first_blunder[:, i] = [row[1] for row in l]
    first_mistake[:, i] = [row[2] for row in l]
    total_blunder[:, i] = [row[3] for row in l]
    game_len[:, i] = [row[4] for row in l]
# print(sum(box[:, 0]/bin_size))

first_blunder_data = pd.DataFrame(data=first_blunder, columns=[
    'Bin 1', 'Bin 2', 'Bin 3', 'Bin 4', 'Bin 5', 'Bin 6', 'Bin 7', 'Bin 8', 'Bin 9', '10'])
first_mistake_data = pd.DataFrame(data=first_mistake, columns=[
    'Bin 1', 'Bin 2', 'Bin 3', 'Bin 4', 'Bin 5', 'Bin 6', 'Bin 7', 'Bin 8', 'Bin 9', '10'])
total_blunder_data = pd.DataFrame(data=total_blunder, columns=[
    'Bin 1', 'Bin 2', 'Bin 3', 'Bin 4', 'Bin 5', 'Bin 6', 'Bin 7', 'Bin 8', 'Bin 9', '10'])
game_len_data = pd.DataFrame(data=game_len, columns=[
    'Bin 1', 'Bin 2', 'Bin 3', 'Bin 4', 'Bin 5', 'Bin 6', 'Bin 7', 'Bin 8', 'Bin 9', '10'])
# Create a boxplot
sns.boxplot(data=first_blunder_data)
plt.title('First Blunder')
plt.show()

sns.boxplot(data=first_mistake_data,)
plt.title('First Mistake')
plt.show()

sns.boxplot(data=total_blunder_data)
plt.title('Total Blunder')
plt.show()
sns.boxplot(data=game_len_data)
plt.title('Game Len')
plt.show()
