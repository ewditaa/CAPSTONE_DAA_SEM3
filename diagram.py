import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
fig, ax = plt.subplots(figsize=(11, 3.6)); ax.axis("off"); ax.set_xlim(0, 11); ax.set_ylim(0, 3.6)
boxes = [("Input\nparcels + graph\n(JSON)", "#e8e8e8"), ("Phase 2a\nMerge Sort\ndeadline, priority", "#cfe8ff"),
         ("Phase 2b\n0/1 Knapsack DP\npick parcels", "#d5f5d5"), ("Phase 3a\nDijkstra\nshortest paths", "#ffe6c7"),
         ("Phase 3b\nNearest-Neighbour\nTSP route", "#f9d0d0")]
for i, (t, c) in enumerate(boxes):
    x = 0.2 + i * 2.15
    ax.add_patch(FancyBboxPatch((x, 1.2), 1.8, 1.4, boxstyle="round,pad=0.05", fc=c, ec="k"))
    ax.text(x + 0.9, 1.9, t, ha="center", va="center", fontsize=9)
    if i < 4: ax.annotate("", xy=(x + 2.1, 1.9), xytext=(x + 1.85, 1.9), arrowprops=dict(arrowstyle="->"))
ax.text(5.5, 0.6, "Output: loaded parcel list  +  ordered delivery route  +  total distance   |   Phase 4: runtime measured at every step",
        ha="center", fontsize=9)
ax.set_title("Mini-Courier Planner - design / data flow", fontsize=11)
plt.savefig("output/design_diagram.png", dpi=150, bbox_inches="tight")
