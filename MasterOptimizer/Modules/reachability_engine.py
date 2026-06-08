import numpy as np
import pandas as pd
from collections import deque


def calculate_reachability(
    nodes_df,
    master_x,
    master_y,
    master_range=70,
    node_range=120
):
    """
    Calculate:
    - Reachable nodes
    - Hop count
    - Parent node
    """

    nodes = nodes_df.copy().reset_index(drop=True)

    nodes["reachable"] = False
    nodes["hop_count"] = -1
    nodes["parent_node"] = None

    # --------------------------------------------------
    # Step 1: Nodes directly reachable from master
    # --------------------------------------------------

    master_distance = np.sqrt(
        (nodes["x"] - master_x) ** 2 +
        (nodes["y"] - master_y) ** 2
    )

    first_hop = nodes.index[
        master_distance <= master_range
    ].tolist()

    queue = deque()

    for idx in first_hop:
        nodes.loc[idx, "reachable"] = True
        nodes.loc[idx, "hop_count"] = 1
        nodes.loc[idx, "parent_node"] = "MASTER"

        queue.append(idx)

    # --------------------------------------------------
    # Step 2: BFS Mesh Expansion
    # --------------------------------------------------

    coords = nodes[["x", "y"]].values

    while queue:

        current = queue.popleft()

        current_x = coords[current][0]
        current_y = coords[current][1]

        current_hop = nodes.loc[current, "hop_count"]

        dx = coords[:, 0] - current_x
        dy = coords[:, 1] - current_y

        distances = np.sqrt(dx**2 + dy**2)

        neighbors = np.where(
            distances <= node_range
        )[0]

        for nb in neighbors:

            if nb == current:
                continue

            if nodes.loc[nb, "reachable"]:
                continue

            nodes.loc[nb, "reachable"] = True
            nodes.loc[nb, "hop_count"] = current_hop + 1
            nodes.loc[nb, "parent_node"] = current

            queue.append(nb)

    return nodes