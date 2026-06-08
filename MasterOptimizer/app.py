import streamlit as st
import plotly.graph_objects as go
import numpy as np

from Modules.loader import load_data
from Modules.mesh_engine import count_neighbors
from Modules.cluster_engine import detect_clusters
#from Modules.bridge_engine import detect_bridge_nodes
from Modules.master_health import calculate_master_health
from Modules.master_ranking import rank_all_masters
from Modules.master_diagnosis import diagnose_master
from Modules.cluster_center import (
    find_largest_cluster_center
)
from Modules.master_optimizer import (
    optimize_master_location
)
from Modules.location_evaluator import (
    evaluate_candidate_locations
)
from Modules.mesh_visualizer import (
    create_mesh_links
)
from Modules.geojson_exporter import (
    export_best250_geojson
)
from Modules.master_network_exporter import (
    create_master_feature,
    create_best250_features,
    build_master_network_features
)
from Modules.geojson_exporter import (
    export_best250_geojson,
    export_all_masters_best250
)
from Modules.master_network_exporter import (
    create_master_feature,
    create_best250_features,
    build_master_network_features
)
from Modules.best250_engine import (
    calculate_best250
)
# from Modules.node_assignment_engine import (
#     initialize_master_capacity,
#     initialize_node_assignment,
#     allocate_best_nodes,
#     build_assignment_report
# )
from Modules.best250_engine import (
    calculate_best250
)
from Modules.planning_engine import (
    load_requirements,
    process_master_assignments,
    convert_report_to_dataframe
)
# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Master Controller Optimizer",
    layout="wide"
)

st.title("Master Controller Optimizer")

# =====================================================
# LOAD DATA
# =====================================================

FILE_PATH = r"data\node_master_coordinates.xlsx"

nodes_df, masters_df = load_data(FILE_PATH)
# =====================================================
# SIDEBAR
# =====================================================

selected_master = st.sidebar.selectbox(
    "Select Master",
    masters_df["master_id"]
)

# =====================================================
# MASTER DETAILS
# =====================================================

master_row = masters_df[
    masters_df["master_id"] == selected_master
].iloc[0]

master_x = master_row["x"]
master_y = master_row["y"]


# =====================================================
# DISTANCE CALCULATION
# =====================================================

nodes_df["distance"] = np.sqrt(
    (nodes_df["x"] - master_x) ** 2 +
    (nodes_df["y"] - master_y) ** 2
)

nodes_in_radius = nodes_df[
    nodes_df["distance"] <= 500
].copy()
from Modules.reachability_engine import calculate_reachability

mesh_df = calculate_reachability(
    nodes_in_radius,
    master_x,
    master_y,
    master_range=70,
    node_range=120
)
mesh_links = create_mesh_links(
    mesh_df,
    nodes_df,
    master_x,
    master_y
)
st.write(
    "Mesh Links Found:",
    len(mesh_links)
)

if len(mesh_links) > 0:

    st.dataframe(
        mesh_links[:20]
    )
cluster_df = detect_clusters(
    nodes_in_radius,
    communication_range=120
)
cluster_center = (
    find_largest_cluster_center(
        cluster_df
    )
)
#bridge_df = detect_bridge_nodes(
 #   nodes_in_radius,
  #  master_x,
   # master_y
#)

# -------------------------------------
# CLUSTER KPI
# -------------------------------------

cluster_count = cluster_df["cluster_id"].nunique()

cluster_sizes = (
    cluster_df
    .groupby("cluster_id")
    .size()
    .reset_index(name="node_count")
)

largest_cluster = cluster_sizes[
    "node_count"
].max()

st.subheader("Cluster Statistics")

c1, c2 = st.columns(2)

with c1:
    st.metric(
        "Clusters Found",
        cluster_count
    )

with c2:
    st.metric(
        "Largest Cluster",
        largest_cluster
    )

# -------------------------------------
# CLUSTER DETAILS
# -------------------------------------

with st.expander("Cluster Details"):

    st.dataframe(
        cluster_sizes.sort_values(
            "node_count",
            ascending=False
        )
    )
# -------------------------------------
# REACHABILITY KPI
# -------------------------------------

reachable_nodes = mesh_df[
    mesh_df["reachable"]
]

unreachable_nodes = mesh_df[
    ~mesh_df["reachable"]
]

st.write(
    "Total Mesh Records:",
    len(mesh_df)
)

st.write(
    "Reachable Nodes:",
    len(reachable_nodes)
)

st.write(
    "Unreachable Nodes:",
    len(unreachable_nodes)
)

st.write(
    "Maximum Hop Count:",
    mesh_df["hop_count"].max()
)
reachability_percent = round(
    (
        len(reachable_nodes)
        /
        max(len(nodes_in_radius), 1)
    ) * 100,
    1
)
# -------------------------------------
# BRIDGE NODE ANALYSIS
# -------------------------------------

# st.subheader("Bridge Node Analysis")

# bridge_nodes = bridge_df[
#     bridge_df["bridge_impact"] > 0
# ]

# st.metric(
#     "Bridge Nodes Found",
#     len(bridge_nodes)
# )

# with st.expander(
#     "Critical Bridge Nodes"
# ):
#     st.dataframe(
#         bridge_nodes.head(20)
#     )
st.subheader("Reachability Statistics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Reachable Nodes",
        len(reachable_nodes)
    )

with col2:
    st.metric(
        "Unreachable Nodes",
        len(unreachable_nodes)
    )

with col3:
    if len(reachable_nodes) > 0:
        st.metric(
            "Average Hop Count",
            round(
                reachable_nodes["hop_count"].mean(),
                2
            )
        )

with col4:
    if len(reachable_nodes) > 0:

        st.metric(
            "Maximum Hop Count",
            int(
                reachable_nodes["hop_count"].max()
            )
        )

with col5:
    st.metric(
        "Reachability %",
        f"{reachability_percent}%"
    )
st.write("Master X:", master_x)
st.write("Master Y:", master_y)

st.write("Node X Min:", nodes_in_radius["x"].min())
st.write("Node X Max:", nodes_in_radius["x"].max())

st.write("Node Y Min:", nodes_in_radius["y"].min())
st.write("Node Y Max:", nodes_in_radius["y"].max())

nodes_within_70m = nodes_df[
    nodes_df["distance"] <= 70
].copy()

# =====================================================
# AUTO ZOOM LIMITS
# =====================================================

if len(nodes_in_radius) > 0:

    xmin = nodes_in_radius["x"].min() - 50
    xmax = nodes_in_radius["x"].max() + 50

    ymin = nodes_in_radius["y"].min() - 50
    ymax = nodes_in_radius["y"].max() + 50

else:

    xmin = master_x - 500
    xmax = master_x + 500

    ymin = master_y - 500
    ymax = master_y + 500

# =====================================================
# MESH ANALYSIS
# =====================================================

candidate_nodes = nodes_in_radius.copy()
nodes_in_radius["node_type"] = "Other"

if len(candidate_nodes) > 0:

    candidate_nodes["neighbor_count"] = count_neighbors(
        candidate_nodes,
        max_distance=120
    )

    candidate_nodes["redundancy_score"] = (
        candidate_nodes["neighbor_count"]
        /
        candidate_nodes["neighbor_count"].max()
    )

    candidate_nodes["distance_score"] = (
        500 - candidate_nodes["distance"]
    ) / 500

    max_neighbors = max(
        candidate_nodes["neighbor_count"].max(),
        1
    )

    candidate_nodes["mesh_score"] = (
        candidate_nodes["neighbor_count"]
        / max_neighbors
    )

    candidate_nodes = candidate_nodes.merge(
        mesh_df[
            [
                "node_id",
                "reachable",
                "hop_count"
            ]
        ],
        on="node_id",
        how="left"
    )

    candidate_nodes["reachable"] = (
        candidate_nodes["reachable"]
        .fillna(False)
    )

    candidate_nodes["hop_count"] = (
        candidate_nodes["hop_count"]
        .fillna(999)
    )

    candidate_nodes["reachability_score"] = np.where(
        candidate_nodes["reachable"],
        1 / (candidate_nodes["hop_count"] + 1),
        0
    )

    candidate_nodes["total_score"] = (
        0.30 * candidate_nodes["distance_score"]
        +
        0.25 * candidate_nodes["mesh_score"]
        +
        0.25 * candidate_nodes["reachability_score"]
        +
        0.20 * candidate_nodes["redundancy_score"]
    )

    best_250_nodes = (
        candidate_nodes
        .sort_values(
            "total_score",
            ascending=False
        )
        .head(250)
    )

    export_best250_geojson(
        best_250_nodes,
        "best250_nodes.geojson"
    )

    master_feature = create_master_feature(
        selected_master,
        master_x,
        master_y
    )

    best250_features = create_best250_features(
        best_250_nodes,
        selected_master
    )

    network_features = (
        build_master_network_features(
            master_feature,
            best250_features
        )
    )

    st.write(
        "Network Features:",
        len(network_features)
    )

else:

    best_250_nodes = candidate_nodes
    network_features = []

# =====================================================
# HEADER
# =====================================================

st.success(
    f"Loaded {len(nodes_df)} Nodes and {len(masters_df)} Masters"
)

st.subheader(
    f"Analysis for {selected_master}"
)

# =====================================================
# KPI SECTION
# =====================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Nodes Within 500m",
        len(nodes_in_radius)
    )

with col2:
    if len(nodes_in_radius):
        st.metric(
            "Average Distance",
            round(
                nodes_in_radius["distance"].mean(),
                1
            )
        )

with col3:
    if len(nodes_in_radius):
        st.metric(
            "Maximum Distance",
            round(
                nodes_in_radius["distance"].max(),
                1
            )
        )

with col4:
    st.metric(
        "Nodes Within 70m",
        len(nodes_within_70m)
    )

# =====================================================
# MESH KPI
# =====================================================

if len(best_250_nodes):

    st.subheader("Mesh Statistics")

    col5, col6 = st.columns(2)

    with col5:
        st.metric(
            "Average Neighbors",
            round(
                best_250_nodes["neighbor_count"].mean(),
                1
            )
        )

    with col6:
        st.metric(
            "Maximum Neighbors",
            int(
                best_250_nodes["neighbor_count"].max()
            )
        )
st.subheader("Redundancy Statistics")

r1, r2 = st.columns(2)

with r1:
    st.metric(
        "Average Redundancy",
        round(
            candidate_nodes[
                "redundancy_score"
            ].mean(),
            2
        )
    )

with r2:
    st.metric(
        "Maximum Neighbors",
        int(
            candidate_nodes[
                "neighbor_count"
            ].max()
        )
    )
    avg_hop = (
    reachable_nodes["hop_count"]
    .mean()
)

avg_redundancy = (
    candidate_nodes[
        "redundancy_score"
    ].mean()
)

master_health = calculate_master_health(
    nodes_in_radius,
    reachable_nodes,
    cluster_count,
    avg_hop,
    avg_redundancy
)

reachability_percent = (
    len(reachable_nodes)
    /
    max(len(nodes_in_radius), 1)
) * 100

issues, recommendations = diagnose_master(
    master_health,
    reachability_percent,
    cluster_count,
    len(nodes_in_radius),
    avg_hop,
    avg_redundancy
)
if master_health >= 80:
    health_status = "Excellent"

elif master_health >= 60:
    health_status = "Good"

elif master_health >= 40:
    health_status = "Average"

elif master_health >= 20:
    health_status = "Poor"

else:
    health_status = "Critical"

# -------------------------------------
# MASTER HEALTH KPI
# -------------------------------------

st.subheader("Master Health")

h1, h2 = st.columns(2)

with h1:
    st.metric(
        "Health Score",
        master_health
    )

with h2:
    st.metric(
        "Status",
        health_status
    )
    st.subheader("Master Diagnosis")

for issue in issues:
    st.warning(issue)

st.subheader("Recommendations")

for rec in recommendations:
    st.success(rec)
    # -------------------------------------
# SUGGESTED CLUSTER CENTER
# -------------------------------------

if master_health < 80:

    st.subheader(
        "Suggested Cluster Center"
    )

st.write(
    "Largest Cluster ID:",
    cluster_center["cluster_id"]
)

st.write(
    "Cluster Size:",
    cluster_center["cluster_size"]
)

st.write(
    "Suggested X:",
    round(
        cluster_center["center_x"],
        2
    )
)

st.write(
    "Suggested Y:",
    round(
        cluster_center["center_y"],
        2
    )
)
# -------------------------------------
# MOVEMENT RECOMMENDATION
# -------------------------------------

delta_x = (
    cluster_center["center_x"]
    - master_x
)

delta_y = (
    cluster_center["center_y"]
    - master_y
)

st.subheader(
    "Movement Recommendation"
)

st.write(
    f"Move East/West: {round(delta_x,1)} m"
)

st.write(
    f"Move North/South: {round(delta_y,1)} m"
)
optimized_location, candidate_results = (
    optimize_master_location(
        nodes_df,
        cluster_center["center_x"],
        cluster_center["center_y"]
    )
)
st.subheader(
    "Optimized Master Location"
)

st.write(
    "Suggested X:",
    round(
        optimized_location["x"],
        2
    )
)

st.write(
    "Suggested Y:",
    round(
        optimized_location["y"],
        2
    )
)

st.write(
    "Expected Health Score:",
    optimized_location[
        "health_score"
    ]
)
st.subheader(
    "Top Candidate Locations"
)

import pandas as pd

candidate_df = pd.DataFrame(
    candidate_results
)

st.dataframe(
    candidate_df.head(5)
)
st.write(
    "Expected Health Score:",
    optimized_location[
        "health_score"
    ]
)
# =====================================================
# CANDIDATE LOCATION EVALUATION
# =====================================================

st.subheader(
    "Candidate Location Evaluation"
)

uploaded_location_file = st.file_uploader(
    "Upload Candidate Location Excel",
    type=["xlsx"]
)
# st.subheader(
#     "Node Assignment Planning"
# )

# requirement_file = st.file_uploader(
#     "Upload Master Requirement Excel",
#     type=["xlsx"]
# )

# if requirement_file is not None:

#     requirement_df = pd.read_excel(
#         requirement_file
#     )

#     st.write(
#         "Excel Columns:",
#         requirement_df.columns.tolist()
#     )

#     st.dataframe(
#         requirement_df.head()
#     )

#     master_capacity = (
#         initialize_master_capacity(
#             requirement_df
#         )
#     )

#     assigned_nodes = (
#         initialize_node_assignment()
#     )
# if requirement_file is not None:

#     requirement_df = pd.read_excel(
#         requirement_file
#     )

#     master_capacity = (
#         initialize_master_capacity(
#             requirement_df
#         )
#     )

#     assigned_nodes = (
#         initialize_node_assignment()
#     )

#     for _, row in requirement_df.iterrows():

#         master_id = row["master_id"]

#         master_row = masters_df[
#             masters_df["master_id"] == master_id
#         ]

#         if len(master_row) == 0:
#             continue

#         master_x = (
#             master_row.iloc[0]["x"]
#         )

#         master_y = (
#             master_row.iloc[0]["y"]
#         )

#         best_250_nodes = (
#             calculate_best250(
#                 nodes_df,
#                 master_x,
#                 master_y
#             )
#         )

#         allocate_best_nodes(
#             best_250_nodes,
#             master_id,
#             row["required_nodes"],
#             assigned_nodes,
#             master_capacity
#         )

#     assignment_report = (
#         build_assignment_report(
#             master_capacity
#         )
#     )

#     st.subheader(
#         "Final Assignment Report"
#     )

#     st.dataframe(
#         assignment_report
#     )
#     st.subheader(
#     "Assignment Capacity Report"
# )

#     st.dataframe(
#     assignment_report
# )

#     st.write(
#         "Requirements Loaded:"
#     )

#     st.dataframe(
#         requirement_df
#     )

if uploaded_location_file is not None:

    candidate_df = pd.read_excel(
        uploaded_location_file
    )

    locations = candidate_df.to_dict(
        orient="records"
    )

    location_results = (
        evaluate_candidate_locations(
            nodes_df,
            locations
        )
    )

    location_results_df = pd.DataFrame(
        location_results
    )

    st.subheader(
        "Location Ranking"
    )

    st.dataframe(
        location_results_df
    )

    best_location = (
        location_results_df
        .iloc[0]
    )

    st.subheader(
        "Best Practical Location"
    )

    st.success(
        f"""
Location: {best_location['location']}

Health Score: {best_location['health_score']}
"""
    )
# =====================================================
# MAP
# =====================================================

fig = go.Figure()
for link in mesh_links:

    fig.add_trace(
        go.Scatter(
            x=[
                link["parent_x"],
                link["child_x"]
            ],
            y=[
                link["parent_y"],
                link["child_y"]
            ],
            mode="lines",
            line=dict(
                width=1,
                color="rgba(100,100,100,0.3)"
            ),
            name="Mesh Link",
            showlegend=False
        )
    )
# All nodes inside 500m

fig.add_trace(
    go.Scattergl(
        x=nodes_in_radius["x"],
        y=nodes_in_radius["y"],
        mode="markers",
        name="Nodes <=500m",
        marker=dict(
            color="blue",
            size=6
        )
    )
)

# Best 250 nodes

fig.add_trace(
    go.Scattergl(
        x=best_250_nodes["x"],
        y=best_250_nodes["y"],
        mode="markers",
        name="Best 250 Nodes",
        marker=dict(
            color="green",
            size=10
        )
    )
)

# Master

fig.add_trace(
    go.Scattergl(
        x=[master_x],
        y=[master_y],
        mode="markers+text",
        text=[selected_master],
        textposition="top center",
        name="Master",
        marker=dict(
            color="red",
            size=20
        )
    )
)

# 500m Radius Circle

theta = np.linspace(0, 2*np.pi, 200)

circle_x = master_x + 500 * np.cos(theta)
circle_y = master_y + 500 * np.sin(theta)

fig.add_trace(
    go.Scatter(
        x=circle_x,
        y=circle_y,
        mode="lines",
        name="500m Radius"
    )
)

# Layout

fig.update_layout(
    title=f"{selected_master} Coverage Analysis",
    height=900,
    showlegend=True,

    xaxis=dict(
        title="UTM Easting",
        range=[xmin, xmax]
    ),

    yaxis=dict(
        title="UTM Northing",
        range=[ymin, ymax]
    )
)

fig.update_yaxes(
    scaleanchor="x",
    scaleratio=1
)

# Debug

st.write(
    "Nodes plotted:",
    len(nodes_in_radius)
)

st.write(
    "Best 250 plotted:",
    len(best_250_nodes)
)
# =====================================================
# GRAPH DEBUG
# =====================================================

st.write("Master X:", master_x)
st.write("Master Y:", master_y)

st.write("xmin:", xmin)
st.write("xmax:", xmax)

st.write("ymin:", ymin)
st.write("ymax:", ymax)

if len(nodes_in_radius) > 0:
    st.write("Node X Min:", nodes_in_radius["x"].min())
    st.write("Node X Max:", nodes_in_radius["x"].max())

    st.write("Node Y Min:", nodes_in_radius["y"].min())
    st.write("Node Y Max:", nodes_in_radius["y"].max())
st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# TABLE
# =====================================================

st.subheader("Best 250 Nodes")

if len(best_250_nodes):

    st.dataframe(

        best_250_nodes[
            [
                "node_id",
                "x",
                "y",
                "distance",
                "neighbor_count",
                "hop_count",
                "reachable",
                "redundancy_score",
                "distance_score",
                "mesh_score",
                "reachability_score",
                "total_score"
            ]
        ]
    )
# =====================================================
# REACHABILITY PREVIEW
# =====================================================

with st.expander("Full Reachability Analysis"):

    st.dataframe(
        mesh_df[
            [
                "node_id",
                "reachable",
                "hop_count",
                "parent_node"
            ]
        ]
    )
# =====================================================
# DEBUG
# =====================================================

with st.expander("Debug Information"):

    st.write(
        "Node Shape:",
        nodes_df.shape
    )

    st.write(
        "Master Shape:",
        masters_df.shape
    )

    st.write(
        "Node X Range:",
        nodes_df["x"].min(),
        "to",
        nodes_df["x"].max()
    )

    st.write(
        "Node Y Range:",
        nodes_df["y"].min(),
        "to",
        nodes_df["y"].max()
    )
    st.subheader("Master Ranking")

ranking_df = rank_all_masters(
    nodes_df,
    masters_df
)

st.dataframe(ranking_df)
# =====================================================
# NETWORK PLANNING
# =====================================================

st.header(
    "Network Planning"
)

planning_file = st.file_uploader(
    "Upload Planning Excel",
    type=["xlsx"],
    key="planning"
)

if planning_file is not None:

    planning_df = pd.read_excel(
        planning_file
    )

    requirements = (
        load_requirements(
            planning_df
        )
    )

    tracker, report = (
        process_master_assignments(
            nodes_df,
            masters_df,
            requirements
        )
    )
    st.session_state["tracker"] = tracker
    st.session_state["requirements"] = requirements

    report_df = (
        convert_report_to_dataframe(
            report
        )
    )

    st.subheader(
        "Planning Report"
    )

    st.dataframe(
        report_df
    )
    st.write(
    "Total Assigned Nodes:",
    len(
        tracker["assigned_nodes"]
    )
)
# =====================================================
# FULL NETWORK GEOJSON EXPORT
# =====================================================

st.subheader(
    "Generate Full Network GeoJSON"
)

if st.button("Generate All Masters GeoJSON"):

    if "tracker" not in st.session_state:

        st.error(
            "Please upload Planning Excel first."
        )

    else:

        tracker = st.session_state["tracker"]

        all_features = []

        for _, master_row in masters_df.iterrows():

            master_id = master_row["master_id"]

            if master_id not in tracker[
                "master_assignments"
            ]:
                continue

            master_x = master_row["x"]
            master_y = master_row["y"]

            selected_nodes = tracker[
                "master_assignments"
            ][master_id]

            master_feature = create_master_feature(
                master_id,
                master_x,
                master_y
            )

            best250_features = create_best250_features(
                selected_nodes,
                master_id
            )

            all_features.append(
                master_feature
            )

            all_features.extend(
                best250_features
            )

        export_all_masters_best250(
            all_features,
            "exports/all_masters_best250.geojson"
        )

        st.success(
            f"""
GeoJSON Created Successfully

Total Features:
{len(all_features)}

Assigned Nodes:
{len(tracker["assigned_nodes"])}

File:
exports/all_masters_best250.geojson
"""
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
            calculate_best250(
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