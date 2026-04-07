from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

# =========================================================
# INPUT / OUTPUT
# =========================================================
INPUT_CSV = Path(
    r"D:\VSCODE\Peer_City_Temporal_Similarity_3D_Site\plots\input\spectral_graph_data_2010_2014.csv"
)

# This writes to the repo root, matching the file structure in your screenshot
OUT_DIR = Path(r"D:\VSCODE\Peer_City_Temporal_Similarity_3D_Site")
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_HTML = OUT_DIR / "spectral_2010_2014.html"

# =========================================================
# COLORS
# =========================================================
PALETTE = [
    "#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e",
    "#17becf", "#8c564b", "#e377c2", "#bcbd22", "#7f7f7f"
]

def cluster_color(cluster):
    if pd.isna(cluster):
        return "#888888"
    c = int(cluster)
    if c == -1:
        return "#888888"
    return PALETTE[c % len(PALETTE)]

# =========================================================
# LOG WEIGHT SCALING
# Mirrors the old matplotlib idea:
# - clip
# - log10
# - low-end clip at 10th percentile
# - rescale to [0,1]
# =========================================================
def log_scale_weights(weights: np.ndarray) -> np.ndarray:
    eps = 1e-9
    w = np.clip(np.asarray(weights, dtype=float), eps, None)
    lw = np.log10(w)

    lo = np.percentile(lw, 10)
    lw = np.clip(lw, lo, None)

    lo2, hi2 = lw.min(), lw.max()
    if hi2 > lo2:
        return (lw - lo2) / (hi2 - lo2)

    return np.ones_like(lw)

# =========================================================
# LOAD EDGE-BASED GRAPH CSV
# Expected columns:
# source_label, source_cluster, source_x, source_y, source_z,
# target_label, target_cluster, target_x, target_y, target_z, weight
# =========================================================
df = pd.read_csv(INPUT_CSV)

required_cols = {
    "source_label", "source_cluster", "source_x", "source_y", "source_z",
    "target_label", "target_cluster", "target_x", "target_y", "target_z",
    "weight",
}
missing = required_cols - set(df.columns)
if missing:
    raise ValueError(f"Missing required columns in {INPUT_CSV.name}: {sorted(missing)}")

# =========================================================
# BUILD UNIQUE NODE TABLE
# =========================================================
source_nodes = df[
    ["source_label", "source_cluster", "source_x", "source_y", "source_z"]
].copy()
source_nodes.columns = ["label", "cluster", "x", "y", "z"]

target_nodes = df[
    ["target_label", "target_cluster", "target_x", "target_y", "target_z"]
].copy()
target_nodes.columns = ["label", "cluster", "x", "y", "z"]

nodes = pd.concat([source_nodes, target_nodes], ignore_index=True)
nodes = nodes.drop_duplicates(subset=["label"]).reset_index(drop=True)

# =========================================================
# BUILD EDGE TRACES
# One trace per edge so opacity/width can vary by weight
# =========================================================
weights = df["weight"].to_numpy(dtype=float)
w_scaled = log_scale_weights(weights)

edge_traces = []

for (_, row), ws in zip(df.iterrows(), w_scaled):
    # Slightly stronger than the matplotlib version so it reads better on the webpage
    alpha = 0.18 + 0.72 * ws
    width = 0.8 + 3.0 * ws

    edge_traces.append(
        go.Scatter3d(
            x=[row["source_x"], row["target_x"], None],
            y=[row["source_y"], row["target_y"], None],
            z=[row["source_z"], row["target_z"], None],
            mode="lines",
            line=dict(
                width=width,
                color=f"rgba(120,120,120,{alpha})"
            ),
            hoverinfo="text",
            hovertext=f"Weight: {row['weight']:.4f}",
            showlegend=False,
        )
    )

# =========================================================
# BUILD NODE TRACE
# =========================================================
node_colors = [cluster_color(c) for c in nodes["cluster"]]

hover_text = [
    f"{row.label}<br>Cluster: {int(row.cluster)}"
    for row in nodes.itertuples(index=False)
]

node_trace = go.Scatter3d(
    x=nodes["x"],
    y=nodes["y"],
    z=nodes["z"],
    mode="markers+text",
    text=nodes["label"],
    textposition="top center",
    hovertext=hover_text,
    hoverinfo="text",
    marker=dict(
        size=8,
        color=node_colors,
        line=dict(width=1, color="white"),
    ),
    showlegend=False,
)

# =========================================================
# FIGURE
# =========================================================
fig = go.Figure(data=edge_traces + [node_trace])

fig.update_layout(
    title="Spectral Clustering Affinity Graph (3D)<br>2020–2024",
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
    ),
    margin=dict(l=0, r=0, t=80, b=0),
    paper_bgcolor="white",
    plot_bgcolor="white",
)

fig.write_html(OUTPUT_HTML, include_plotlyjs="cdn", full_html=True)
print(f"Saved: {OUTPUT_HTML}")