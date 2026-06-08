def diagnose_master(
    health_score,
    reachability_percent,
    cluster_count,
    coverage_nodes,
    avg_hop,
    avg_redundancy
):

    issues = []
    recommendations = []

    if reachability_percent < 20:
        issues.append("Very low reachability")
        recommendations.append(
            "Move master closer to reachable node cluster"
        )

    elif reachability_percent < 50:
        issues.append("Moderate reachability")
        recommendations.append(
            "Improve first-hop connectivity"
        )

    if cluster_count > 1:
        issues.append(
            f"Network fragmented into {cluster_count} clusters"
        )
        recommendations.append(
            "Move master toward largest cluster center"
        )

    if coverage_nodes < 500:
        issues.append("Low node coverage")
        recommendations.append(
            "Move master toward denser node population"
        )

    if avg_hop > 5:
        issues.append("High hop count")
        recommendations.append(
            "Reduce communication path length"
        )

    if avg_redundancy < 0.50:
        issues.append("Low redundancy")
        recommendations.append(
            "Increase alternate communication paths"
        )

    if health_score >= 80:
        issues.append("Master location is healthy")

    elif health_score < 40:
        recommendations.append(
            "Master relocation strongly recommended"
        )

    return issues, recommendations