"""
export_graph_json.py
--------------------
Exports a Plotly figure JSON file for each period so the Tableau extension
can render the real project graphs directly (without an iframe).

Run once from anywhere inside the repo, e.g.:
    python tableau_extension/export_graph_json.py

Outputs (next to this script, inside tableau_extension/):
    spectral_2010_2014.json
    spectral_2015_2019.json
    spectral_2020_2024.json

Re-run whenever the source CSVs change.
The graph-building logic is identical to Build_Public_Site_Graphs.py so the
Tableau extension always shows the same figures as the main website.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ── paths ──────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = REPO_ROOT / "plots" / "input"
OUT_DIR   = Path(__file__).resolve().parent   # tableau_extension/

PERIODS = ["2010_2014", "2015_2019", "2020_2024"]

# ── colours (identical to Build_Public_Site_Graphs.py) ─────────────────────
PALETTE = [
    "#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e",
    "#17becf", "#8c564b", "#e377c2", "#bcbd22", "#7f7f7f",
]

def cluster_color(cluster):
    if pd.isna(cluster):
        return "#888888"
    c = int(cluster)
    return "#888888" if c == -1 else PALETTE[c % len(PALETTE)]


def log_scale_weights(weights: np.ndarray) -> np.ndarray:
    eps = 1e-9
    w  = np.clip(np.asarray(weights, dtype=float), eps, None)
    lw = np.log10(w)
    lo = np.percentile(lw, 10)
    lw = np.clip(lw, lo, None)
    lo2, hi2 = lw.min(), lw.max()
    return (lw - lo2) / (hi2 - lo2) if hi2 > lo2 else np.ones_like(lw)


# ── figure builder (mirrors Build_Public_Site_Graphs.py exactly) ───────────
def build_figure(period: str) -> go.Figure:
    csv_path = INPUT_DIR / f"spectral_graph_data_{period}.csv"
    df = pd.read_csv(csv_path)

    src = df[["source_label", "source_cluster", "source_x", "source_y", "source_z"]].copy()
    src.columns = ["label", "cluster", "x", "y", "z"]
    tgt = df[["target_label", "target_cluster", "target_x", "target_y", "target_z"]].copy()
    tgt.columns = ["label", "cluster", "x", "y", "z"]

    nodes = (
        pd.concat([src, tgt], ignore_index=True)
        .drop_duplicates(subset=["label"])
        .reset_index(drop=True)
    )

    weights  = df["weight"].to_numpy(dtype=float)
    w_scaled = log_scale_weights(weights)

    edge_traces = []
    for (_, row), ws in zip(df.iterrows(), w_scaled):
        alpha = 0.55 + 0.20 * ws
        width = 2.2 + 2.5  * ws
        edge_traces.append(go.Scatter3d(
            x=[row["source_x"], row["target_x"], None],
            y=[row["source_y"], row["target_y"], None],
            z=[row["source_z"], row["target_z"], None],
            mode="lines",
            line=dict(width=width, color=f"rgba(50,50,50,{alpha:.4f})"),
            hoverinfo="text",
            hovertext=f"Weight: {row['weight']:.4f}",
            showlegend=False,
        ))

    node_trace = go.Scatter3d(
        x=nodes["x"], y=nodes["y"], z=nodes["z"],
        mode="markers+text",
        text=nodes["label"],
        textposition="top center",
        hovertext=[
            f"{r.label}<br>Cluster: {int(r.cluster)}"
            for r in nodes.itertuples(index=False)
        ],
        hoverinfo="text",
        marker=dict(
            size=8,
            color=[cluster_color(c) for c in nodes["cluster"]],
            line=dict(width=1, color="white"),
        ),
        showlegend=False,
    )

    year_label = period.replace("_", "\u20132")  # e.g. "2010–2014"
    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        title=f"Spectral Clustering Affinity Graph (3D)<br>{year_label}",
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
        ),
        margin=dict(l=0, r=0, t=80, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    return fig


# ── export ──────────────────────────────────────────────────────────────────
for period in PERIODS:
    print(f"Building {period} ...", end="  ", flush=True)
    fig      = build_figure(period)
    out_path = OUT_DIR / f"spectral_{period}.json"
    out_path.write_text(fig.to_json(), encoding="utf-8")
    print(f"saved -> {out_path.relative_to(REPO_ROOT)}")

print("\nAll done. Re-start the local server if it was already running.")
