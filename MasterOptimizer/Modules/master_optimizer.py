import numpy as np
from Modules.master_evaluator import (
    evaluate_master_location
)

def generate_candidate_points(
    center_x,
    center_y,
    search_radius=300,
    step=50
):

    candidates = []

    for dx in range(
        -search_radius,
        search_radius + step,
        step
    ):

        for dy in range(
            -search_radius,
            search_radius + step,
            step
        ):

            candidates.append(
                (
                    center_x + dx,
                    center_y + dy
                )
            )

    return candidates
def find_best_candidate(
    candidate_results
):

    if len(candidate_results) == 0:
        return None

    best = max(
        candidate_results,
        key=lambda x: x["health_score"]
    )

    return best
def evaluate_candidate(
    candidate_x,
    candidate_y,
    health_score
):

    return {
        "x": candidate_x,
        "y": candidate_y,
        "health_score": health_score
    }
def optimize_master_location(
    nodes_df,
    center_x,
    center_y,
    search_radius=200,
    step=100
):

    candidates = generate_candidate_points(
        center_x,
        center_y,
        search_radius,
        step
    )

    candidate_results = []

    for candidate_x, candidate_y in candidates:

        result = evaluate_master_location(
            nodes_df,
            candidate_x,
            candidate_y
        )

        candidate_results.append(
            evaluate_candidate(
                candidate_x,
                candidate_y,
                result["health_score"]
            )
        )

    candidate_results = sorted(
        candidate_results,
        key=lambda x: x["health_score"],
        reverse=True
    )

    best_candidate = candidate_results[0]

    return best_candidate, candidate_results