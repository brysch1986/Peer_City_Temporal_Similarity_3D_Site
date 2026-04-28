"use strict";

import "./../style/visual.less";

import powerbi from "powerbi-visuals-api";
import IVisual = powerbi.extensibility.visual.IVisual;
import VisualConstructorOptions = powerbi.extensibility.visual.VisualConstructorOptions;
import VisualUpdateOptions = powerbi.extensibility.visual.VisualUpdateOptions;
import DataViewMetadataColumn = powerbi.DataViewMetadataColumn;

import * as Plotly from "plotly.js-dist-min";

// ── colour palette — mirrors Build_Public_Site_Graphs.py exactly ─────────────
const PALETTE = [
    "#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e",
    "#17becf", "#8c564b", "#e377c2", "#bcbd22", "#7f7f7f",
];

function clusterColor(cluster: number): string {
    if (!isFinite(cluster) || cluster === -1) return "#888888";
    return PALETTE[Math.abs(Math.round(cluster)) % PALETTE.length];
}

// Mirrors the log-weight scaling from Build_Public_Site_Graphs.py
function logScaleWeights(weights: number[]): number[] {
    const eps = 1e-9;
    const lw = weights.map(w => Math.log10(Math.max(w, eps)));
    const sorted = [...lw].sort((a, b) => a - b);
    const lo10 = sorted[Math.max(0, Math.floor(sorted.length * 0.1))];
    const clipped = lw.map(v => Math.max(v, lo10));
    const lo2 = Math.min(...clipped);
    const hi2 = Math.max(...clipped);
    if (hi2 > lo2) return clipped.map(v => (v - lo2) / (hi2 - lo2));
    return clipped.map(() => 1);
}

// ── column-name resolution ────────────────────────────────────────────────────
const COL_ALIASES: Record<string, string[]> = {
    srcLabel:   ["source_label",   "sourceLabel",   "SourceLabel",   "Source Label"],
    srcCluster: ["source_cluster", "sourceCluster", "SourceCluster", "Source Cluster"],
    srcX:       ["source_x",       "sourceX",       "SourceX",       "Source X"],
    srcY:       ["source_y",       "sourceY",       "SourceY",       "Source Y"],
    srcZ:       ["source_z",       "sourceZ",       "SourceZ",       "Source Z"],
    tgtLabel:   ["target_label",   "targetLabel",   "TargetLabel",   "Target Label"],
    tgtX:       ["target_x",       "targetX",       "TargetX",       "Target X"],
    tgtY:       ["target_y",       "targetY",       "TargetY",       "Target Y"],
    tgtZ:       ["target_z",       "targetZ",       "TargetZ",       "Target Z"],
    weight:     ["weight",         "Weight"],
};

const OPT_COL_ALIASES: Record<string, string[]> = {
    tgtCluster: ["target_cluster", "targetCluster", "TargetCluster", "Target Cluster"],
};

function findColumn(cols: DataViewMetadataColumn[], key: string): number {
    const aliases = COL_ALIASES[key] ?? OPT_COL_ALIASES[key] ?? [key];
    for (const alias of aliases) {
        const idx = cols.findIndex(c =>
            c.displayName === alias ||
            (c.queryName ?? "").split(".").pop() === alias
        );
        if (idx !== -1) return idx;
    }
    return -1;
}

// ── Visual ────────────────────────────────────────────────────────────────────
export class Visual implements IVisual {
    private container: HTMLElement;

    constructor(options: VisualConstructorOptions) {
        this.container = options.element;
        this.container.style.overflow = "hidden";
    }

    public update(options: VisualUpdateOptions): void {
        const dv = options.dataViews?.[0];

        if (!dv?.table) {
            this.showMessage(
                "Add all columns from the spectral edge-list CSV to the " +
                "'Edge List Columns' field bucket in the Fields pane.",
                "#555"
            );
            return;
        }

        const { columns, rows } = dv.table;

        const ci: Record<string, number> = {};
        for (const key of Object.keys(COL_ALIASES)) {
            ci[key] = findColumn(columns, key);
        }
        ci.tgtCluster = findColumn(columns, "tgtCluster");

        const missing = Object.keys(COL_ALIASES).filter(k => ci[k] === -1);

        if (missing.length > 0) {
            const names = missing.map(k => COL_ALIASES[k][0]).join(", ");
            this.showMessage(
                "Missing columns: " + names + ". " +
                "Make sure all edge-list columns are in the Edge List Columns bucket " +
                "and numeric columns are set to Don't summarize.",
                "#b00"
            );
            return;
        }

        if (rows.length === 0) {
            this.showMessage("No data rows. Check your data source and any active filters.", "#555");
            return;
        }

        // ── parse edge rows ───────────────────────────────────────────────────
        const edges = rows.map(row => ({
            srcLabel:   String(row[ci.srcLabel]   ?? ""),
            srcCluster: Number(row[ci.srcCluster]),
            srcX:       Number(row[ci.srcX]),
            srcY:       Number(row[ci.srcY]),
            srcZ:       Number(row[ci.srcZ]),
            tgtLabel:   String(row[ci.tgtLabel]   ?? ""),
            tgtCluster: ci.tgtCluster !== -1 ? Number(row[ci.tgtCluster]) : NaN,
            tgtX:       Number(row[ci.tgtX]),
            tgtY:       Number(row[ci.tgtY]),
            tgtZ:       Number(row[ci.tgtZ]),
            weight:     Number(row[ci.weight]),
        }));

        // ── unique node table ─────────────────────────────────────────────────
        const nodeMap = new Map<string, { x: number; y: number; z: number; cluster: number }>();
        for (const e of edges) {
            if (!nodeMap.has(e.srcLabel))
                nodeMap.set(e.srcLabel, { x: e.srcX, y: e.srcY, z: e.srcZ, cluster: e.srcCluster });
            if (!nodeMap.has(e.tgtLabel))
                nodeMap.set(e.tgtLabel, { x: e.tgtX, y: e.tgtY, z: e.tgtZ, cluster: e.tgtCluster });
        }

        // ── edge traces ───────────────────────────────────────────────────────
        const wScaled = logScaleWeights(edges.map(e => e.weight));
        const edgeTraces: Plotly.Data[] = edges.map((e, i) => {
            const ws    = wScaled[i];
            const alpha = (0.55 + 0.20 * ws).toFixed(4);
            const width = 2.2 + 2.5 * ws;
            return {
                type: "scatter3d",
                x: [e.srcX, e.tgtX, null],
                y: [e.srcY, e.tgtY, null],
                z: [e.srcZ, e.tgtZ, null],
                mode: "lines",
                line: { width, color: "rgba(50,50,50," + alpha + ")" },
                hoverinfo: "text",
                hovertext: e.srcLabel + " \u2194 " + e.tgtLabel + "<br>Weight: " + e.weight.toFixed(4),
                showlegend: false,
            };
        });

        // ── node trace ────────────────────────────────────────────────────────
        const labels = [...nodeMap.keys()];
        const coords = labels.map(l => nodeMap.get(l)!);

        const nodeTrace: Plotly.Data = {
            type: "scatter3d",
            x: coords.map(c => c.x),
            y: coords.map(c => c.y),
            z: coords.map(c => c.z),
            mode: "markers+text",
            text: labels,
            textposition: "top center",
            hovertext: labels.map((l, i) => {
                const cl = coords[i].cluster;
                return l + "<br>Cluster: " + (isNaN(cl) ? "?" : Math.round(cl));
            }),
            hoverinfo: "text",
            marker: {
                size: 8,
                color: coords.map(c => clusterColor(c.cluster)),
                line: { width: 1, color: "white" },
            },
            showlegend: false,
        };

        // ── layout ────────────────────────────────────────────────────────────
        const layout: Partial<Plotly.Layout> = {
            autosize: true,
            scene: {
                xaxis: { visible: false },
                yaxis: { visible: false },
                zaxis: { visible: false },
            },
            margin: { l: 0, r: 0, t: 0, b: 0 },
            paper_bgcolor: "rgba(0,0,0,0)",
        };

        Plotly.react(
            this.container,
            [...edgeTraces, nodeTrace],
            layout,
            { responsive: true, displayModeBar: false }
        );
    }

    private showMessage(text: string, color: string): void {
        Plotly.purge(this.container);
        while (this.container.firstChild) {
            this.container.removeChild(this.container.firstChild);
        }
        const div = document.createElement("div");
        div.style.padding = "20px";
        div.style.color = color;
        div.style.fontFamily = "Arial, sans-serif";
        div.style.fontSize = "13px";
        div.style.lineHeight = "1.6";
        div.textContent = text;
        this.container.appendChild(div);
    }
}
