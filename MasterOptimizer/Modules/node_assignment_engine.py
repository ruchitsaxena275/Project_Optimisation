import pandas as pd


def initialize_master_capacity(
    requirement_df
):

    master_capacity = {}

    for _, row in requirement_df.iterrows():

        master_id = str(row.iloc[0])
        required_nodes = int(row.iloc[1])

        master_capacity[
            master_id
        ] = {

            "required": required_nodes,

            "assigned": 0
        }

    return master_capacity


def can_assign_node(
    master_capacity,
    master_id
):

    return (
        master_capacity[
            master_id
        ]["assigned"]

        <

        master_capacity[
            master_id
        ]["required"]
    )


def assign_node(
    master_capacity,
    master_id
):

    master_capacity[
        master_id
    ]["assigned"] += 1


def initialize_node_assignment():

    assigned_nodes = set()

    return assigned_nodes


def is_node_available(
    assigned_nodes,
    node_id
):

    return node_id not in assigned_nodes


def assign_node_to_master(
    assigned_nodes,
    node_id
):

    assigned_nodes.add(
        node_id
    )


def allocate_best_nodes(
    best_250_nodes,
    master_id,
    required_nodes,
    assigned_nodes,
    master_capacity
):

    assigned_list = []

    for _, row in best_250_nodes.iterrows():

        node_id = row["node_id"]

        if not is_node_available(
            assigned_nodes,
            node_id
        ):
            continue

        if not can_assign_node(
            master_capacity,
            master_id
        ):
            break

        assign_node_to_master(
            assigned_nodes,
            node_id
        )

        assign_node(
            master_capacity,
            master_id
        )

        assigned_list.append(
            row.to_dict()
        )

    return assigned_list


def build_assignment_report(
    master_capacity
):

    report = []

    for master_id, values in master_capacity.items():

        required = values["required"]
        assigned = values["assigned"]

        report.append(
            {
                "master_id": master_id,
                "required_nodes": required,
                "assigned_nodes": assigned,
                "shortfall": (
                    required - assigned
                )
            }
        )

    return pd.DataFrame(
        report
    )