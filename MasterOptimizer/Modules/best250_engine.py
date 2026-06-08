import numpy as np

from Modules.mesh_engine import count_neighbors
from Modules.reachability_engine import (
    calculate_reachability
)


# =====================================================
# SYMMETRY SCORE
# =====================================================

def calculate_symmetry_score(
    selected_nodes,
    master_x,
    master_y
):
    """
    Rectangular symmetry score based on
    final selected Best250 nodes.
    """

    if len(selected_nodes) < 10:
        return 0.0, 0.0, 0.0

    min_x = selected_nodes["x"].min()
    max_x = selected_nodes["x"].max()

    min_y = selected_nodes["y"].min()
    max_y = selected_nodes["y"].max()

    left_gap = master_x - min_x
    right_gap = max_x - master_x

    bottom_gap = master_y - min_y
    top_gap = max_y - master_y

    x_den = max(left_gap, right_gap)
    y_den = max(top_gap, bottom_gap)

    x_balance = (
        min(left_gap, right_gap) / x_den
        if x_den > 0 else 0
    )

    y_balance = (
        min(top_gap, bottom_gap) / y_den
        if y_den > 0 else 0
    )

    rectangle_balance = (
        x_balance + y_balance
    ) / 2

    nodes_above = (
        selected_nodes["y"] > master_y
    ).sum()

    nodes_below = (
        selected_nodes["y"] < master_y
    ).sum()

    max_rows = max(
        nodes_above,
        nodes_below
    )

    if max_rows == 0:
        row_balance = 0

    else:
        row_balance = (
            min(
                nodes_above,
                nodes_below
            )
            /
            max_rows
        )

    symmetry_score = (
        0.7 * rectangle_balance
        +
        0.3 * row_balance
    )

    return (
        symmetry_score,
        rectangle_balance,
        row_balance
    )


# =====================================================
# BEST 250
# =====================================================

def calculate_best250(
    nodes_df,
    master_x,
    master_y
):

    nodes_df = nodes_df.copy()

    # ==========================================
    # DISTANCE FROM MASTER
    # ==========================================

    nodes_df["distance"] = np.sqrt(
        (nodes_df["x"] - master_x) ** 2 +
        (nodes_df["y"] - master_y) ** 2
    )

    candidate_nodes = nodes_df[
        nodes_df["distance"] <= 500
    ].copy()

    if len(candidate_nodes) == 0:
        return candidate_nodes

    # ==========================================
    # REACHABILITY
    # ==========================================

    mesh_df = calculate_reachability(
        candidate_nodes,
        master_x,
        master_y,
        master_range=70,
        node_range=120
    )

    # ==========================================
    # NEIGHBOR COUNT
    # ==========================================

    candidate_nodes["neighbor_count"] = (
        count_neighbors(
            candidate_nodes,
            max_distance=120
        )
    )

    # ==========================================
    # REDUNDANCY SCORE
    # ==========================================

    candidate_nodes["redundancy_score"] = (
        candidate_nodes["neighbor_count"]
        /
        max(
            candidate_nodes["neighbor_count"].max(),
            1
        )
    )

    # ==========================================
    # DISTANCE SCORE
    # ==========================================

    candidate_nodes["distance_score"] = (
        500 - candidate_nodes["distance"]
    ) / 500

    # ==========================================
    # MESH SCORE
    # ==========================================

    max_neighbors = max(
        candidate_nodes["neighbor_count"].max(),
        1
    )

    candidate_nodes["mesh_score"] = (
        candidate_nodes["neighbor_count"]
        /
        max_neighbors
    )

    # ==========================================
    # MERGE REACHABILITY
    # ==========================================

    candidate_nodes = candidate_nodes.merge(
        mesh_df[
            [
                "node_id",
                "reachable",
                "hop_count"
            ]
        ],
        on="node_id",
        how="left"
    )

    candidate_nodes["reachable"] = (
        candidate_nodes["reachable"]
        .fillna(False)
    )

    candidate_nodes["hop_count"] = (
        candidate_nodes["hop_count"]
        .fillna(999)
    )

    # ==========================================
    # REACHABILITY SCORE
    # ==========================================

    candidate_nodes["reachability_score"] = np.where(
        candidate_nodes["reachable"],
        1 / (candidate_nodes["hop_count"] + 1),
        0
    )

    # ==========================================
    # TOTAL SCORE
    # ==========================================

    candidate_nodes["total_score"] = (
        0.30 * candidate_nodes["distance_score"]
        +
        0.25 * candidate_nodes["mesh_score"]
        +
        0.25 * candidate_nodes["reachability_score"]
        +
        0.20 * candidate_nodes["redundancy_score"]
    )

    # ==========================================
    # BEST 250
    # ==========================================

    best_250_nodes = (
        candidate_nodes
        .sort_values(
            [
                "distance",
                "hop_count",
                "total_score"
            ],
            ascending=[
                True,
                True,
                False
            ]
        )
        .head(250)
        .copy()
    )

    # ==========================================
    # SYMMETRY METRICS
    # ==========================================

    (
        symmetry_score,
        rectangle_balance,
        row_balance
    ) = calculate_symmetry_score(
        best_250_nodes,
        master_x,
        master_y
    )

    best_250_nodes["symmetry_score"] = symmetry_score
    best_250_nodes["rectangle_balance"] = rectangle_balance
    best_250_nodes["row_balance"] = row_balance

    return best_250_nodes


# =====================================================
# CANDIDATE NODES
# =====================================================

def calculate_candidate_nodes(
    nodes_df,
    master_x,
    master_y
):

    nodes_df = nodes_df.copy()

    nodes_df["distance"] = np.sqrt(
        (nodes_df["x"] - master_x) ** 2 +
        (nodes_df["y"] - master_y) ** 2
    )

    candidate_nodes = nodes_df[
        nodes_df["distance"] <= 500
    ].copy()

    if len(candidate_nodes) == 0:
        return candidate_nodes

    mesh_df = calculate_reachability(
        candidate_nodes,
        master_x,
        master_y,
        master_range=70,
        node_range=120
    )

    candidate_nodes["neighbor_count"] = (
        count_neighbors(
            candidate_nodes,
            max_distance=120
        )
    )

    candidate_nodes["redundancy_score"] = (
        candidate_nodes["neighbor_count"]
        /
        max(
            candidate_nodes["neighbor_count"].max(),
            1
        )
    )

    candidate_nodes["distance_score"] = (
        500 - candidate_nodes["distance"]
    ) / 500

    max_neighbors = max(
        candidate_nodes["neighbor_count"].max(),
        1
    )

    candidate_nodes["mesh_score"] = (
        candidate_nodes["neighbor_count"]
        /
        max_neighbors
    )

    candidate_nodes = candidate_nodes.merge(
        mesh_df[
            [
                "node_id",
                "reachable",
                "hop_count"
            ]
        ],
        on="node_id",
        how="left"
    )

    candidate_nodes["reachable"] = (
        candidate_nodes["reachable"]
        .fillna(False)
    )

    candidate_nodes["hop_count"] = (
        candidate_nodes["hop_count"]
        .fillna(999)
    )

    candidate_nodes["reachability_score"] = np.where(
        candidate_nodes["reachable"],
        1 / (candidate_nodes["hop_count"] + 1),
        0
    )

    candidate_nodes["total_score"] = (
        0.30 * candidate_nodes["distance_score"]
        +
        0.25 * candidate_nodes["mesh_score"]
        +
        0.25 * candidate_nodes["reachability_score"]
        +
        0.20 * candidate_nodes["redundancy_score"]
    )

    candidate_nodes = (
        candidate_nodes
        .sort_values(
            [
                "distance",
                "hop_count",
                "total_score"
            ],
            ascending=[
                True,
                True,
                False
            ]
        )
    )

    return candidate_nodes