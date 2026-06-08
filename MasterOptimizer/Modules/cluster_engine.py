import numpy as np
import pandas as pd
from collections import deque


def detect_clusters(
    nodes_df,
    communication_range=120
):
    """
    Detect connected node clusters.

    Returns:
        cluster_df
    """

    nodes = nodes_df.copy().reset_index(drop=True)

    nodes["cluster_id"] = -1

    coords = nodes[["x", "y"]].values

    cluster_id = 0

    for start_node in range(len(nodes)):

        if nodes.loc[start_node, "cluster_id"] != -1:
            continue

        queue = deque([start_node])

        nodes.loc[start_node, "cluster_id"] = cluster_id

        while queue:

            current = queue.popleft()

            current_x = coords[current][0]
            current_y = coords[current][1]

            dx = coords[:, 0] - current_x
            dy = coords[:, 1] - current_y

            distance = np.sqrt(
                dx**2 + dy**2
            )

            neighbors = np.where(
                distance <= communication_range
            )[0]

            for nb in neighbors:

                if nb == current:
                    continue

                if nodes.loc[nb, "cluster_id"] != -1:
                    continue

                nodes.loc[nb, "cluster_id"] = cluster_id

                queue.append(nb)

        cluster_id += 1

    return nodes