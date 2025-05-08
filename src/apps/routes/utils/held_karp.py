import random
import itertools


def generate_distances(n):
    distances = [[0] * n for i in range(n)]
    for i in range(0,n):
        for j in range(i+1,n):
            distances[i][j] = distances[j][i] = random.randint(1,99)
    return distances


def held_karp(points_dict):
    print(points_dict)

    n = len(points_dict)
    dists = list(points_dict.values())
    keys = list(points_dict.keys())
    s = {}

    for k in range(1, n):
        s[(1 << k, k)] = (dists[0][k], 0)

    for subset_size in range(2, n):
        for subset in itertools.combinations(range(1, n), subset_size):

            bits = 0
            for bit in subset:
                bits |= 1 << bit

            for k in subset:
                prev = bits & ~(1 << k)

                res = []
                for m in subset:
                    if m == 0 or m == k:
                        continue
                    res.append((s[(prev, m)][0] + dists[m][k], m))
                s[(bits, k)] = min(res)

    bits = (2**n - 1) - 1

    res = []
    for k in range(1, n):
        res.append((s[(bits, k)][0] + dists[k][0], k))
    opt, parent = min(res)

    path = []
    for i in range(n - 1):
        path.append(parent)
        new_bits = bits & ~(1 << parent)
        _, parent = s[(bits, parent)]
        bits = new_bits

    path.append(0)
    path = list(reversed(path))
    print(opt, path)
    # map indexes to the keys
    order = [keys[i] for i in path]
    return opt, order
