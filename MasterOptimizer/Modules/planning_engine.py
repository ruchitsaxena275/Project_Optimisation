from Modules.best250_engine import (
    calculate_candidate_nodes
)
import pandas as pd


def load_requirements(
    requirement_df
):

    requirements = {}

    for _, row in requirement_df.iterrows():

        requirements[
            str(row["master_id"])
        ] = int(
            row["required_nodes"]
        )

    return requirements
def initialize_assignment_tracker():

    return {
        "assigned_nodes": set(),
        "master_assignments": {}
    }
def initialize_master_report(
    requirements
):

    report = {}

    for master_id, required_nodes in requirements.items():

        report[master_id] = {
            "required": required_nodes,
            "assigned": 0,
            "shortfall": required_nodes
        }

    return report
def update_master_report(
    report,
    master_id,
    assigned_count
):

    report[
        master_id
    ]["assigned"] = assigned_count

    report[
        master_id
    ]["shortfall"] = max(
        0,
        report[
            master_id
        ]["required"]
        -
        assigned_count
    )
def convert_report_to_dataframe(
    report
):

    rows = []

    for master_id, values in report.items():

        rows.append(
            {
                "master_id": master_id,
                "required_nodes": values["required"],
                "assigned_nodes": values["assigned"],
                "shortfall": values["shortfall"]
            }
        )

    return pd.DataFrame(
        rows
    )
def allocate_nodes_to_master(
    best_nodes_df,
    required_nodes,
    assigned_nodes
):

    available_nodes = best_nodes_df[
        ~best_nodes_df["node_id"].isin(
            assigned_nodes
        )
    ].copy()

    selected_nodes = (
        available_nodes
        .head(required_nodes)
    )

    assigned_nodes.update(
        selected_nodes[
            "node_id"
        ].tolist()
    )

    return selected_nodes
def count_assigned_nodes(
    selected_nodes
):

    return len(
        selected_nodes
    )
def save_master_assignment(
    tracker,
    master_id,
    selected_nodes
):

    tracker[
        "master_assignments"
    ][master_id] = (
        selected_nodes.copy()
    )
def get_unassigned_best_nodes(
    best_nodes_df,
    assigned_nodes
):

    return best_nodes_df[
        ~best_nodes_df["node_id"].isin(
            assigned_nodes
        )
    ].copy()       
def calculate_shortfall(
    required_nodes,
    assigned_nodes
):

    return max(
        0,
        required_nodes
        -
        assigned_nodes
    ) 
def process_master_assignments(
    nodes_df,
    masters_df,
    requirements
):

    tracker = (
        initialize_assignment_tracker()
    )

    report = (
        initialize_master_report(
            requirements
        )
    )

    assigned_nodes = (
        tracker["assigned_nodes"]
    )

    for master_id, required_nodes in requirements.items():

        master_row = masters_df[
            masters_df["master_id"]
            ==
            master_id
        ]

        if len(master_row) == 0:
            continue

        master_x = (
            master_row.iloc[0]["x"]
        )

        master_y = (
            master_row.iloc[0]["y"]
        )

        best_nodes = (
    calculate_candidate_nodes(
        nodes_df,
        master_x,
        master_y
    )
)

        available_nodes = (
            get_unassigned_best_nodes(
                best_nodes,
                assigned_nodes
            )
        )
        print(
    "MASTER:",
    master_id,
    "| Reachable:",
    len(best_nodes),
    "| Available:",
    len(available_nodes),
    "| Required:",
    required_nodes
)
        print(
    master_id,
    "Reachable:",
    len(best_nodes),
    "Available:",
    len(available_nodes)
)

        selected_nodes = (
            allocate_nodes_to_master(
                available_nodes,
                required_nodes,
                assigned_nodes
            )
        )

        assigned_count = (
            count_assigned_nodes(
                selected_nodes
            )
        )

        update_master_report(
            report,
            master_id,
            assigned_count
        )

        save_master_assignment(
            tracker,
            master_id,
            selected_nodes
        )

    return (
        tracker,
        report
    )