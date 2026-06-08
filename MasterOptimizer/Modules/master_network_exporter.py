def create_master_feature(
    master_id,
    master_x,
    master_y
):

    return {
        "type": "Feature",

        "geometry": {
            "type": "Point",
            "coordinates": [
                float(master_x),
                float(master_y)
            ]
        },

        "properties": {
            "feature_type": "Master",
            "master_id": str(master_id)
        }
    }
def create_best250_features(
    best_250_nodes,
    master_id
):

    features = []

    for _, row in best_250_nodes.iterrows():

        feature = {

            "type": "Feature",

            "geometry": {
                "type": "Point",

                "coordinates": [
                    float(row["x"]),
                    float(row["y"])
                ]
            },

            "properties": {
                "feature_type": "Best250Node",
                "master_id": str(master_id),

                "node_id": int(
                    row["node_id"]
                ),

                "hop_count": int(
                    row["hop_count"]
                ),

                "reachable": bool(
                    row["reachable"]
                ),

                "total_score": float(
                    row["total_score"]
                )
            }
        }

        features.append(feature)

    return features
def build_master_network_features(
    master_feature,
    best250_features
):

    all_features = []

    all_features.append(
        master_feature
    )

    all_features.extend(
        best250_features
    )

    return all_features