import pandas as pd
import numpy as np

from Modules.mesh_engine import count_neighbors
from Modules.reachability_engine import calculate_reachability
from Modules.cluster_engine import detect_clusters
from Modules.master_health import calculate_master_health


def rank_all_masters(
    nodes_df,
    masters_df
):

    results = []

    for _, master in masters_df.iterrows():

        master_id = master["master_id"]
        master_x = master["x"]
        master_y = master["y"]

        # ----------------------------------
        # Distance
        # ----------------------------------

        temp_nodes = nodes_df.copy()

        temp_nodes["distance"] = np.sqrt(
            (temp_nodes["x"] - master_x) ** 2 +
            (temp_nodes["y"] - master_y) ** 2
        )

        nodes_in_radius = temp_nodes[
            temp_nodes["distance"] <= 500
        ].copy()

        if len(nodes_in_radius) == 0:
            continue

        # ----------------------------------
        # Mesh
        # ----------------------------------

        nodes_in_radius["neighbor_count"] = (
            count_neighbors(
                nodes_in_radius,
                max_distance=120
            )
        )

        nodes_in_radius["redundancy_score"] = (
            nodes_in_radius["neighbor_count"]
            /
            max(
                nodes_in_radius["neighbor_count"].max(),
                1
            )
        )

        # ----------------------------------
        # Reachability
        # ----------------------------------

        mesh_df = calculate_reachability(
            nodes_in_radius,
            master_x,
            master_y,
            master_range=70,
            node_range=120
        )

        reachable_nodes = mesh_df[
            mesh_df["reachable"] == True
        ]

        # ----------------------------------
        # Clusters
        # ----------------------------------

        cluster_df = detect_clusters(
            nodes_in_radius,
            communication_range=120
        )

        cluster_count = (
            cluster_df["cluster_id"]
            .nunique()
        )

        # ----------------------------------
        # Health Score
        # ----------------------------------

        if len(reachable_nodes) > 0:

            avg_hop = (
                reachable_nodes["hop_count"]
                .mean()
            )

        else:

            avg_hop = 10

        avg_redundancy = (
            nodes_in_radius[
                "redundancy_score"
            ].mean()
        )

        health_score = (
            calculate_master_health(
                nodes_in_radius,
                reachable_nodes,
                cluster_count,
                avg_hop,
                avg_redundancy
            )
        )

        # ----------------------------------
        # Status
        # ----------------------------------

        if health_score >= 80:
            status = "Excellent"

        elif health_score >= 60:
            status = "Good"

        elif health_score >= 40:
            status = "Average"

        elif health_score >= 20:
            status = "Poor"

        else:
            status = "Critical"

        results.append(
            {
                "master_id": master_id,
                "health_score": health_score,
                "status": status,
                "nodes_within_500m":
                    len(nodes_in_radius),
                "reachable_nodes":
                    len(reachable_nodes),
                "cluster_count":
                    cluster_count
            }
        )

    ranking_df = pd.DataFrame(results)

    ranking_df = ranking_df.sort_values(
        "health_score",
        ascending=False
    ).reset_index(drop=True)

    ranking_df["rank"] = (
        ranking_df.index + 1
    )

    return ranking_df