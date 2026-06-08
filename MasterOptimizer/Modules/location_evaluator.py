from Modules.master_evaluator import (
    evaluate_master_location
)


def evaluate_candidate_locations(
    nodes_df,
    locations
):

    results = []

    for location in locations:

        result = evaluate_master_location(
            nodes_df,
            location["X"],
            location["Y"]
        )

        results.append(
    {
        "location":
            str(location["Master"]),

        "x":
            float(location["X"]),

        "y":
            float(location["Y"]),

        "health_score":
            result["health_score"],

        "coverage_nodes":
            result["coverage_nodes"],

        "reachable_nodes":
            result["reachable_nodes"],

        "cluster_count":
            result["cluster_count"]
    }
)

    results = sorted(
        results,
        key=lambda x: x["health_score"],
        reverse=True
    )

    return results