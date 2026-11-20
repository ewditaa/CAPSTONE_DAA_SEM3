import random
from courier_planner import *
def test_sort():
    ps = generate_parcels(200, 20)
    key = lambda p: (p.deadline, -p.priority)
    assert merge_sort(ps, key) == sorted(ps, key=key) == insertion_sort(ps, key)
def test_knapsack_vs_bruteforce():
    ps = generate_parcels(12, 20, seed=5)
    best, chosen, _ = knapsack(ps, 40)
    ref = max(sum(p.priority for k, p in enumerate(ps) if m >> k & 1)
              for m in range(1 << 12) if sum(p.weight for k, p in enumerate(ps) if m >> k & 1) <= 40)
    assert best == ref and sum(p.weight for p in chosen) <= 40
def test_dijkstra_known():
    adj = {0: [(1, 4), (2, 1)], 1: [(0, 4), (2, 2)], 2: [(0, 1), (1, 2)]}
    d, prev = dijkstra(adj, 0); assert d == {0: 0, 1: 3, 2: 1} and path_to(prev, 1) == [0, 2, 1]
def test_route_visits_all():
    adj = generate_graph(30); stops = [5, 9, 14, 22]
    r, total, _, _ = nearest_neighbour_route(adj, 0, stops)
    assert r[0] == r[-1] == 0 and set(r) == {0, *stops}
def test_greedy_fails_dp_wins():
    ps = [Parcel(1, 10, 60, 5, 1), Parcel(2, 20, 100, 5, 2), Parcel(3, 30, 120, 5, 3)]
    assert greedy_knapsack(ps, 50) == 160 and knapsack(ps, 50)[0] == 220
if __name__ == "__main__":
    for f in [test_sort, test_knapsack_vs_bruteforce, test_dijkstra_known, test_route_visits_all, test_greedy_fails_dp_wins]:
        f(); print("PASS", f.__name__)
