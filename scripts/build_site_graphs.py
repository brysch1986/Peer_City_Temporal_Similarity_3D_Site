from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

# =========================================================
# PATHS  (relative to this script — works on any machine)
# =========================================================
REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = REPO_ROOT / "plots" / "input"
OUT_DIR   = REPO_ROOT / "plots"

PERIODS = [
    ("2010_2014", "2010–2014"),
    ("2015_2019", "2015–2019"),
    ("2020_2024", "2020–2024"),
]

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
# - clip to positive
# - log10
# - clip low end at 10th percentile
# - rescale to [0, 1]
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
# BUILD AND WRITE ONE GRAPH PER PERIOD
# =========================================================
REQUIRED_COLS = {
    "source_label", "source_cluster", "source_x", "source_y", "source_z",
    "target_label", "target_cluster", "target_x", "target_y", "target_z",
    "weight",
}

def build_graph(period_key: str, period_label: str):
    input_csv = INPUT_DIR / f"spectral_graph_data_{period_key}.csv"
    output_html = OUT_DIR / f"spectral_{period_key}.html"

    df = pd.read_csv(input_csv)
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in {input_csv.name}: {sorted(missing)}")

    src = df[["source_label", "source_cluster", "source_x", "source_y", "source_z"]].copy()
    src.columns = ["label", "cluster", "x", "y", "z"]
    tgt = df[["target_label", "target_cluster", "target_x", "target_y", "target_z"]].copy()
    tgt.columns = ["label", "cluster", "x", "y", "z"]
    nodes = pd.concat([src, tgt], ignore_index=True).drop_duplicates(subset=["label"]).reset_index(drop=True)

    weights = df["weight"].to_numpy(dtype=float)
    w_scaled = log_scale_weights(weights)

    edge_traces = []
    for (_, row), ws in zip(df.iterrows(), w_scaled):
        alpha = 0.55 + 0.20 * ws
        width = 2.2 + 2.5 * ws
        edge_traces.append(
            go.Scatter3d(
                x=[row["source_x"], row["target_x"], None],
                y=[row["source_y"], row["target_y"], None],
                z=[row["source_z"], row["target_z"], None],
                mode="lines",
                line=dict(width=width, color=f"rgba(50,50,50,{alpha})"),
                hoverinfo="text",
                hovertext=f"Weight: {row['weight']:.4f}",
                showlegend=False,
            )
        )

    node_colors = [cluster_color(c) for c in nodes["cluster"]]
    hover_text = [
        f"{r.label}<br>Cluster: {int(r.cluster)}"
        for r in nodes.itertuples(index=False)
    ]
    node_trace = go.Scatter3d(
        x=nodes["x"], y=nodes["y"], z=nodes["z"],
        mode="markers+text",
        text=nodes["label"],
        textposition="top center",
        hovertext=hover_text,
        hoverinfo="text",
        marker=dict(size=8, color=node_colors, line=dict(width=1, color="white")),
        showlegend=False,
    )

    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        title=f"Spectral Clustering Affinity Graph (3D)<br>{period_label}",
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
        ),
        margin=dict(l=0, r=0, t=80, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    fig.write_html(output_html, include_plotlyjs="cdn", full_html=True)
    print(f"Saved: {output_html}")


if __name__ == "__main__":
    for key, label in PERIODS:
        build_graph(key, label)
