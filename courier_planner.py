"""
Mini-Courier Planner  -  DAA Capstone (ETCCDA302)
Integrates: Merge Sort -> 0/1 Knapsack (DP) -> Dijkstra -> Nearest-Neighbour TSP
Run:  python courier_planner.py            (demo on data/sample_small.json)
      python courier_planner.py --bench    (runtime study + chart)
"""
import heapq, json, random, time, sys, itertools
from dataclasses import dataclass

# ------------------------------------------------------------------ DATA MODEL
@dataclass
class Parcel:
    pid: int
    weight: int        # kg  (knapsack weight)
    priority: int      # 1..100 (knapsack value; higher = more important)
    deadline: int      # hours from now (smaller = more urgent)
    dest: int          # graph node of delivery point

def generate_graph(n, extra_edges_factor=2, seed=1):
    """Connected weighted undirected graph as adjacency list {u: [(v, w), ...]}.
    Node 0 is the depot. A random spanning chain guarantees connectivity."""
    rnd = random.Random(seed)
    adj = {i: [] for i in range(n)}
    def add(u, v, w):
        adj[u].append((v, w)); adj[v].append((u, w))
    for i in range(1, n):
        add(i, rnd.randrange(i), rnd.randint(1, 20))
    for _ in range(n * extra_edges_factor):
        u, v = rnd.randrange(n), rnd.randrange(n)
        if u != v:
            add(u, v, rnd.randint(1, 20))
    return adj

def generate_parcels(m, n_nodes, seed=2):
    rnd = random.Random(seed)
    return [Parcel(i + 1, rnd.randint(1, 15), rnd.randint(1, 100),
                   rnd.randint(1, 48), rnd.randint(1, n_nodes - 1)) for i in range(m)]

# ------------------------------------------------------------------ PHASE 2a: SORTING
def merge_sort(arr, key):
    """Stable O(n log n) merge sort. Sorts by key (tuple)."""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    L, R = merge_sort(arr[:mid], key), merge_sort(arr[mid:], key)
    out, i, j = [], 0, 0
    while i < len(L) and j < len(R):
        if key(L[i]) <= key(R[j]):
            out.append(L[i]); i += 1
        else:
            out.append(R[j]); j += 1
    return out + L[i:] + R[j:]

def insertion_sort(arr, key):
    """O(n^2) baseline used only for the runtime comparison."""
    a = arr[:]
    for i in range(1, len(a)):
        x, j = a[i], i - 1
        while j >= 0 and key(a[j]) > key(x):
            a[j + 1] = a[j]; j -= 1
        a[j + 1] = x
    return a

def prioritise(parcels):
    """Earliest deadline first; ties -> higher priority first."""
    return merge_sort(parcels, key=lambda p: (p.deadline, -p.priority))

def quick_sort(arr, key):
    """Randomised quick sort, average O(n log n); extra baseline for comparison."""
    if len(arr) <= 1:
        return arr
    piv = key(random.choice(arr))
    return (quick_sort([x for x in arr if key(x) < piv], key) +
            [x for x in arr if key(x) == piv] +
            quick_sort([x for x in arr if key(x) > piv], key))

# ------------------------------------------------------------------ PHASE 2b: 0/1 KNAPSACK
def knapsack(parcels, capacity):
    """Bottom-up DP. dp[i][w] = best total priority using first i parcels with capacity w.
    Time O(n*W), space O(n*W) (kept so we can backtrack the chosen set)."""
    n = len(parcels)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        wt, val = parcels[i - 1].weight, parcels[i - 1].priority
        for w in range(capacity + 1):
            dp[i][w] = dp[i - 1][w]                       # skip parcel i
            if wt <= w:                                   # or take it
                dp[i][w] = max(dp[i][w], dp[i - 1][w - wt] + val)
    chosen, w = [], capacity                              # backtrack
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            chosen.append(parcels[i - 1]); w -= parcels[i - 1].weight
    chosen.reverse()
    return dp[n][capacity], chosen, dp

def greedy_knapsack(parcels, capacity):
    """Greedy by priority/weight ratio. Fast but NOT always optimal -> shows why DP is used."""
    tot, w = 0, 0
    for p in sorted(parcels, key=lambda p: p.priority / p.weight, reverse=True):
        if w + p.weight <= capacity:
            w += p.weight; tot += p.priority
    return tot

def print_dp_table(parcels, dp, capacity, max_cols=41):
    """Print DP table (rows = parcels considered, cols = capacity)."""
    cols = min(capacity, max_cols - 1)
    print("\nDP table (row i = first i parcels, column = capacity 0.." + str(cols) + "):")
    print("      " + "".join(f"{w:>5}" for w in range(cols + 1)))
    for i, row in enumerate(dp):
        lab = "none" if i == 0 else f"P{parcels[i-1].pid}"
        print(f"{lab:>5} " + "".join(f"{v:>5}" for v in row[:cols + 1]))

# ------------------------------------------------------------------ PHASE 3a: DIJKSTRA
def dijkstra(adj, src):
    """Binary-heap Dijkstra. O((V+E) log V). Returns (dist, prev)."""
    dist = {u: float("inf") for u in adj}
    prev = {u: None for u in adj}
    dist[src] = 0
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue                                      # stale entry
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w; prev[v] = u
                heapq.heappush(pq, (dist[v], v))
    return dist, prev

def path_to(prev, t):
    p = []
    while t is not None:
        p.append(t); t = prev[t]
    return p[::-1]

# ------------------------------------------------------------------ PHASE 3b: NEAREST-NEIGHBOUR TSP
def nearest_neighbour_route(adj, depot, stops):
    """Greedy TSP approximation on the shortest-path metric.
    Runs Dijkstra from the depot and each stop: O(k * (V+E) log V) + O(k^2)."""
    stops = sorted(set(stops) - {depot})
    nodes = [depot] + stops
    D, P = {}, {}
    for s in nodes:
        D[s], P[s] = dijkstra(adj, s)
    route, cur, left, total = [depot], depot, set(stops), 0
    while left:
        nxt = min(left, key=lambda x: D[cur][x])
        total += D[cur][nxt]; route.append(nxt); left.remove(nxt); cur = nxt
    total += D[cur][depot]; route.append(depot)
    # expand to the full road path
    full = [depot]
    for a, b in zip(route, route[1:]):
        full += path_to(P[a], b)[1:]
    return route, total, full, D

def brute_force_tsp(D, depot, stops):
    """Exact optimum (only for <= 9 stops) to measure the approximation ratio."""
    best = float("inf")
    for perm in itertools.permutations(stops):
        c, cur = 0, depot
        for s in perm:
            c += D[cur][s]; cur = s
        best = min(best, c + D[cur][depot])
    return best

# ------------------------------------------------------------------ PIPELINE
def plan_trip(adj, parcels, capacity, depot=0, verbose=True):
    t = {}
    t0 = time.perf_counter(); ordered = prioritise(parcels);            t["sort"] = time.perf_counter() - t0
    t0 = time.perf_counter(); best, chosen, dp = knapsack(ordered, capacity); t["knapsack"] = time.perf_counter() - t0
    t0 = time.perf_counter()
    route, dist, full, D = nearest_neighbour_route(adj, depot, [p.dest for p in chosen])
    t["dijkstra+tsp"] = time.perf_counter() - t0
    if verbose:
        print("Parcels sorted by deadline (first 8):")
        for p in ordered[:8]:
            print(f"  P{p.pid:<3} deadline={p.deadline:>2}h weight={p.weight:>2}kg priority={p.priority:>3} -> node {p.dest}")
        print(f"\nTruck capacity {capacity} kg | knapsack best priority = {best}")
        print("Loaded parcels:", [f"P{p.pid}" for p in chosen],
              f"| total weight = {sum(p.weight for p in chosen)} kg")
        if len(parcels) <= 15:
            print_dp_table(ordered, dp, capacity)
        print(f"Greedy (ratio) knapsack would give {greedy_knapsack(ordered, capacity)} vs DP optimum {best}")
        _, prev0 = dijkstra(adj, depot)
        print("\nDijkstra shortest paths from depot (individual):")
        for st in route[1:-1]:
            print(f"  0 -> {st:<4} dist={D[depot][st]:<4} path: " + " -> ".join(map(str, path_to(prev0, st))))
        print("\nDelivery order (nodes):", " -> ".join(map(str, route)))
        print("Total route length    :", dist)
        print("Full road path        :", " -> ".join(map(str, full)))
    return dict(ordered=ordered, best=best, chosen=chosen, dp=dp, route=route, dist=dist, full=full, D=D, times=t)

# ------------------------------------------------------------------ PHASE 4: BENCHMARK
def benchmark():
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sizes = [100, 200, 400, 800, 1600]
    rows = []
    print(f"{'n':>6} {'merge(ms)':>10} {'insert(ms)':>11} {'knap(ms)':>10} {'dijk+tsp(ms)':>13} {'quick(ms)':>10}")
    for n in sizes:
        adj = generate_graph(max(50, n // 2), seed=n)
        parcels = generate_parcels(n, len(adj), seed=n)
        key = lambda p: (p.deadline, -p.priority)
        t0 = time.perf_counter(); merge_sort(parcels, key); ms = time.perf_counter() - t0
        t0 = time.perf_counter(); quick_sort(parcels, key); qs = time.perf_counter() - t0
        t0 = time.perf_counter(); insertion_sort(parcels, key); ins = time.perf_counter() - t0
        t0 = time.perf_counter(); _, chosen, _ = knapsack(parcels[:min(n, 200)], 100); kn = time.perf_counter() - t0
        stops = [p.dest for p in parcels[:30]]               # one truck visits ~30 stops
        t0 = time.perf_counter(); nearest_neighbour_route(adj, 0, stops); rt = time.perf_counter() - t0
        rows.append((n, ms, ins, kn, rt, qs))
        print(f"{n:>6} {ms*1e3:>10.2f} {ins*1e3:>11.2f} {kn*1e3:>10.2f} {rt*1e3:>13.2f} {qs*1e3:>10.2f}")
    ns = [r[0] for r in rows]
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(ns, [r[1]*1e3 for r in rows], "o-", label="Merge sort  O(n log n)")
    ax[0].plot(ns, [r[5]*1e3 for r in rows], "^-", label="Quick sort  O(n log n) avg")
    ax[0].plot(ns, [r[2]*1e3 for r in rows], "s-", label="Insertion sort  O(n²)")
    ax[0].set(title="Sorting runtime", xlabel="parcels (n)", ylabel="ms"); ax[0].legend()
    ax[1].plot(ns, [r[3]*1e3 for r in rows], "o-", label="Knapsack DP")
    ax[1].plot(ns, [r[4]*1e3 for r in rows], "s-", label="Dijkstra + NN-TSP (30 stops)")
    ax[1].set(title="Major pipeline steps", xlabel="parcels / graph size", ylabel="ms"); ax[1].legend()
    plt.tight_layout(); plt.savefig("output/runtime_chart.png", dpi=150)
    print("Saved output/runtime_chart.png")

    # approximation quality: NN-TSP vs exact optimum on small instances
    print("\nApproximation check (NN vs brute-force optimum, 8 stops):")
    ratios = []
    for seed in range(5):
        adj = generate_graph(40, seed=seed)
        stops = random.Random(seed).sample(range(1, 40), 8)
        _, nn, _, D = nearest_neighbour_route(adj, 0, stops)
        opt = brute_force_tsp(D, 0, sorted(set(stops)))
        ratios.append(nn / opt); print(f"  seed {seed}: NN={nn}  OPT={opt}  ratio={nn/opt:.2f}")
    print(f"  average ratio = {sum(ratios)/len(ratios):.2f}")

# ------------------------------------------------------------------ MAIN
def load(path):
    d = json.load(open(path))
    adj = {int(u): [tuple(e) for e in es] for u, es in d["graph"].items()}
    return adj, [Parcel(**p) for p in d["parcels"]], d["capacity"]

if __name__ == "__main__":
    if "--bench" in sys.argv:
        benchmark()
    else:
        path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_small.json"
        adj, parcels, cap = load(path)
        plan_trip(adj, parcels, cap)
