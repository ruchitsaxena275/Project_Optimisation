import numpy as np

def count_neighbors(nodes_df, max_distance=120):

    coords = nodes_df[["x", "y"]].values

    neighbor_counts = []

    for i in range(len(coords)):

        distances = np.sqrt(
            np.sum(
                (coords - coords[i]) ** 2,
                axis=1
            )
        )

        count = np.sum(
            (distances <= max_distance)
            & (distances > 0)
        )

        neighbor_counts.append(int(count))

    return neighbor_counts