def create_mesh_links(
    mesh_df,
    nodes_df,
    master_x,
    master_y
):

    node_lookup = (
        nodes_df
        .set_index("node_id")
    )

    links = []

    reachable_nodes = mesh_df[
        mesh_df["reachable"]
    ]

    for _, row in reachable_nodes.iterrows():

        child_id = row["node_id"]
        parent_id = row["parent_node"]

        try:

            child_x = node_lookup.loc[
                child_id,
                "x"
            ]

            child_y = node_lookup.loc[
                child_id,
                "y"
            ]

        except:
            continue

        # MASTER CONNECTION

        if parent_id == "MASTER":

            parent_x = master_x
            parent_y = master_y

        else:

            try:

                parent_x = node_lookup.loc[
                    int(parent_id),
                    "x"
                ]

                parent_y = node_lookup.loc[
                    int(parent_id),
                    "y"
                ]

            except:
                continue

        links.append(
            {
                "parent_x": parent_x,
                "parent_y": parent_y,
                "child_x": child_x,
                "child_y": child_y,
                "hop_count": row["hop_count"]
            }
        )

    return links