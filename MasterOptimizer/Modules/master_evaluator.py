import numpy as np

from Modules.mesh_engine import count_neighbors
from Modules.reachability_engine import calculate_reachability
from Modules.cluster_engine import detect_clusters
from Modules.master_health import calculate_master_health


def evaluate_master_location(
    nodes_df,
    master_x,
    master_y
):

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

        return {
            "health_score": 0,
            "coverage_nodes": 0,
            "reachable_nodes": 0,
            "cluster_count": 0
        }

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

    return {
        "health_score": health_score,
        "coverage_nodes": len(nodes_in_radius),
        "reachable_nodes": len(reachable_nodes),
        "cluster_count": cluster_count,
        "avg_hop": avg_hop
    }