import json


def export_best250_geojson(
    best_250_nodes,
    output_file
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
                "node_id": int(
                    row["node_id"]
                ),
                "total_score": float(
                    row["total_score"]
                ),
                "hop_count": int(
                    row["hop_count"]
                ),
                "reachable": bool(
                    row["reachable"]
                )
            }
        }

        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(
        output_file,
        "w"
    ) as f:

        json.dump(
    geojson,
    f,
    indent=2
)


def export_all_masters_best250(
    all_features,
    output_file
):

    geojson = {
        "type": "FeatureCollection",
        "features": all_features
    }

    with open(
        output_file,
        "w"
    ) as f:

        json.dump(
            geojson,
            f,
            indent=2
        )