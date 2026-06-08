import pandas as pd
from Modules.reachability_engine import calculate_reachability


def detect_bridge_nodes(
    nodes_df,
    master_x,
    master_y,
    master_range=70,
    node_range=120
):
    nodes_df = nodes_df.reset_index(drop=True)

    base_mesh = calculate_reachability(
        nodes_df,
        master_x,
        master_y,
        master_range,
        node_range
    )

    base_reachable = (
        base_mesh["reachable"]
        .sum()
    )

    results = []

    for idx in range(len(nodes_df)):

        temp_nodes = nodes_df.drop(
            index=idx
        ).reset_index(drop=True)

        temp_mesh = calculate_reachability(
            temp_nodes,
            master_x,
            master_y,
            master_range,
            node_range
        )

        temp_reachable = (
            temp_mesh["reachable"]
            .sum()
        )

        impact = (
            base_reachable
            - temp_reachable
        )

        results.append(
            {
                "node_id":
                nodes_df.iloc[idx]["node_id"],

                "bridge_impact":
                impact
            }
        )

    bridge_df = pd.DataFrame(
        results
    )

    bridge_df = bridge_df.sort_values(
        "bridge_impact",
        ascending=False
    )

    return bridge_dfS