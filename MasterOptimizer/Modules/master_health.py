import numpy as np

def calculate_master_health(
    nodes_in_radius,
    reachable_nodes,
    cluster_count,
    avg_hop,
    avg_redundancy
):

    coverage_score = min(
        len(nodes_in_radius) / 500,
        1
    )

    reachability_score = (
        len(reachable_nodes)
        /
        max(len(nodes_in_radius), 1)
    )

    hop_score = max(
        0,
        1 - (avg_hop / 10)
    )

    cluster_score = 1 / max(
        cluster_count,
        1
    )

    redundancy_score = min(
        avg_redundancy,
        1
    )

    health_score = (
        0.20 * coverage_score
        +
        0.35 * reachability_score
        +
        0.20 * hop_score
        +
        0.10 * cluster_score
        +
        0.15 * redundancy_score
    )

    return round(
        health_score * 100,
        1
    )