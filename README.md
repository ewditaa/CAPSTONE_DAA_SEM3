# Mini-Courier Planner (DAA Capstone – ETCCDA302)
Individual capstone: integrates Sorting, Dynamic Programming, Graph algorithms and Approximation in Python.

## Folder contents
| File | Purpose |
|---|---|
| `courier_planner.py` | all algorithms + pipeline + benchmark |
| `make_data.py` | creates `data/sample_small.json`, `data/sample_large.json` |
| `test_courier.py` | correctness tests |
| `run_all.py` | regenerates every file in `output/` |
| `diagram.py` | draws `output/design_diagram.png` |
| `output/` | run traces, DP table, runtime chart, test results |
| `screenshots/` | **put your own screenshots here** |

## Execution steps
```
pip install matplotlib        # only needed for charts
python make_data.py
python courier_planner.py                     # small demo (prints DP table, paths, route)
python courier_planner.py data/sample_large.json
python courier_planner.py --bench             # runtime study + chart
python test_courier.py
python run_all.py                             # saves all evidence to output/
```

## Phase 1 – Design & planning
**Problem:** a truck starts at depot (node 0). Choose which parcels fit (weight limit), maximise importance, then find a short delivery tour.

**Data design**
- Parcel: `id, weight (kg), priority (1–100), deadline (h), dest (node)`
- Graph: weighted undirected adjacency list `{u: [(v, w)]}`; node 0 = depot; weight = distance (always > 0).
- Dataset file: JSON with `capacity`, `graph`, `parcels`.

**How the algorithms work together** (see `output/design_diagram.png`)
```
parcels -> Merge Sort (deadline asc, priority desc) -> ordered list
        -> 0/1 Knapsack DP (weight = capacity use, value = priority) -> parcels for the trip
        -> Dijkstra from depot and every stop -> shortest-distance matrix
        -> Nearest-Neighbour TSP on that matrix -> delivery order + route length
```
| Step | Algorithm | Why chosen | Time / space |
|---|---|---|---|
| Sort | Merge sort | stable, worst-case O(n log n) (compared with quick & insertion sort) | O(n log n) / O(n) |
| Pack | 0/1 knapsack DP | parcels cannot be split; greedy can be non-optimal (proved in `output/greedy_vs_dp.txt`) | O(nW) / O(nW) |
| Paths | Dijkstra + min-heap | edge weights non-negative | O((V+E) log V) |
| Route | Nearest-neighbour | TSP is NP-hard; fast approximation | O(k²) + k Dijkstras |

Note: knapsack's optimal value does not depend on parcel order; sorting decides the processing/display order (most urgent first) and breaks ties for which parcel appears first.

## Phase 2 – Prioritisation & box filling
Evidence: `output/sample_run.txt` – sorted list, **full DP table**, chosen parcels (P5,P2,P10,P12,P11,P8,P4,P7 = 40 kg, priority 484).
Counter-example where greedy fails (220 vs 160): `output/greedy_vs_dp.txt`.

## Phase 3 – Route maker & graph
Evidence: `output/sample_run.txt` – individual Dijkstra paths from depot, final order 0→7→9→1→2→6→0, length 43, full road path.
Large run (200 nodes, 58 stops, length 576): `output/large_run.txt`.

## Phase 4 – Testing & optimisation
- Tests (`output/test_results.txt`): sort vs Python `sorted`, knapsack vs brute force, Dijkstra on known graph, route validity, greedy-vs-DP counter-example.
- Runtime: `output/benchmark.txt`, `output/runtime_chart.png` (n = 100…1600). Insertion sort ≈4× slower per doubling (O(n²)); merge/quick sort ≈2× (O(n log n)). Large-dataset step timings in `output/large_run.txt`.
- Approximation: nearest-neighbour averaged 1.09× optimal on 8-stop instances (max 1.19×).
- Improvements: 1-D knapsack array (O(W) space); 2-opt/Christofides to improve the tour; cache Dijkstra results; multiple trips for leftover parcels; A* if coordinates are known.

## Phase 5 – Result explanation
The system first ranks parcels by urgency, picks the best-value set that fits the truck exactly, computes true road distances, and visits the stops greedily by nearest distance. Results are optimal for packing and near-optimal for routing. Add screenshots of the commands above in `screenshots/`.
