import pandas as pd


def find_largest_cluster_center(cluster_df):

    cluster_sizes = (
        cluster_df
        .groupby("cluster_id")
        .size()
        .reset_index(name="node_count")
    )

    largest_cluster_id = (
        cluster_sizes
        .sort_values(
            "node_count",
            ascending=False
        )
        .iloc[0]["cluster_id"]
    )

    largest_cluster_nodes = cluster_df[
        cluster_df["cluster_id"]
        == largest_cluster_id
    ]

    center_x = (
        largest_cluster_nodes["x"]
        .mean()
    )

    center_y = (
        largest_cluster_nodes["y"]
        .mean()
    )

    return {
        "cluster_id": largest_cluster_id,
        "cluster_size": len(
            largest_cluster_nodes
        ),
        "center_x": center_x,
        "center_y": center_y
    }