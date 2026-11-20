import json, dataclasses
from courier_planner import generate_graph, generate_parcels
for name, nodes, m, cap in [("sample_small", 10, 12, 40), ("sample_large", 200, 300, 150)]:
    g = generate_graph(nodes, seed=7); p = generate_parcels(m, nodes, seed=7)
    json.dump({"capacity": cap, "graph": {str(u): v for u, v in g.items()},
               "parcels": [dataclasses.asdict(x) for x in p]}, open(f"data/{name}.json", "w"))
