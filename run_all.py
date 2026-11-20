"""Runs everything and saves evidence into output/ (small run, large run + timing, tests, benchmark, diagram)."""
import io, contextlib, time, subprocess, sys
import courier_planner as cp

def capture(path, fn):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): fn()
    open(path, "w").write(buf.getvalue()); print("saved", path)

capture("output/sample_run.txt", lambda: cp.plan_trip(*cp.load("data/sample_small.json")[:1], cp.load("data/sample_small.json")[1], cp.load("data/sample_small.json")[2]))

def large():
    adj, parcels, cap = cp.load("data/sample_large.json")
    print(f"LARGE DATASET: {len(adj)} nodes, {len(parcels)} parcels, capacity {cap} kg")
    r = cp.plan_trip(adj, parcels, cap, verbose=False)
    print(f"Loaded {len(r['chosen'])} parcels, weight {sum(p.weight for p in r['chosen'])} kg, best priority {r['best']}")
    print(f"Greedy would give {cp.greedy_knapsack(r['ordered'], cap)}")
    print(f"Stops visited: {len(r['route'])-2}, route length: {r['dist']}")
    for k, v in r["times"].items(): print(f"  {k:<14} {v*1e3:8.2f} ms")
capture("output/large_run.txt", large)
capture("output/benchmark.txt", cp.benchmark)
open("output/test_results.txt", "w").write(subprocess.run([sys.executable, "test_courier.py"], capture_output=True, text=True).stdout)
print("saved output/test_results.txt")

def greedy_demo():
    ps = [cp.Parcel(1, 10, 60, 5, 1), cp.Parcel(2, 20, 100, 5, 2), cp.Parcel(3, 30, 120, 5, 3)]
    print("Counter-example, capacity 50 kg, parcels (kg,value): (10,60) (20,100) (30,120)")
    print("Greedy by value/weight ratio:", cp.greedy_knapsack(ps, 50), "| DP optimum:", cp.knapsack(ps, 50)[0])
capture("output/greedy_vs_dp.txt", greedy_demo)
