# Peer City Spectral 3D — Power BI Custom Visual

Renders the peer-city spectral clustering graph as an interactive 3D Plotly
chart inside Power BI Desktop.  Data comes directly from the project's
existing `plots/input/spectral_graph_data_YYYY_YYYY.csv` edge-list files —
no new data pipeline is needed.

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Power BI Desktop | Latest | Windows only; free download from Microsoft |
| Node.js | 18 LTS or later | https://nodejs.org |
| npm | 8+ | ships with Node.js |
| powerbi-visuals-tools | 5.3.0 | installed below |
| Python + pandas | existing env | only needed for `combine_periods.py` |

---

## One-time global install

```cmd
npm install -g powerbi-visuals-tools@5.3.0
```

Verify:
```cmd
pbiviz --version
```

---

## Build the visual

From the repo root:

```cmd
cd powerbi_visual\spectral3d
npm install
pbiviz package
```

This produces:
```
powerbi_visual\spectral3d\dist\spectral3d.pbiviz
```

That single `.pbiviz` file is everything Power BI needs.

---

## Load data into Power BI Desktop

### Option A — single period (simplest)

1. Open Power BI Desktop.
2. **Home → Get data → Text/CSV**.
3. Browse to:
   ```
   plots\input\spectral_graph_data_2020_2024.csv
   ```
4. In the preview dialog, click **Transform Data**.
5. For each of the numeric columns below, set **Data Type** to **Decimal Number**
   and ensure **Don't summarize** is set (do this in the report view after loading):
   - `source_x`, `source_y`, `source_z`, `source_cluster`
   - `target_x`, `target_y`, `target_z`, `target_cluster`
   - `weight`
6. Click **Close & Apply**.

### Option B — all three periods with a slicer

Run from the repo root:

```cmd
python powerbi_visual\combine_periods.py
```

Then load `powerbi_visual\spectral_all_periods.csv` instead.
Add a native Power BI **Slicer** visual on the `period` column to switch
between 2010-2014, 2015-2019, and 2020-2024.

---

## Import the custom visual into Power BI Desktop

1. In Power BI Desktop, go to the **Visualizations** pane.
2. Click the **"..."** (more visuals) button at the bottom of the pane.
3. Select **"Import a visual from a file"**.
4. Browse to:
   ```
   powerbi_visual\spectral3d\dist\spectral3d.pbiviz
   ```
5. Click **Import** → accept the warning about unverified visuals.
6. A new "Peer City Spectral 3D" icon appears in the Visualizations pane.

---

## Add the visual to a report page

1. Click the **Peer City Spectral 3D** icon to add it to the canvas.
2. Resize it to fill most of the page.
3. In the **Fields** pane, drag **all columns** from your loaded table into
   the visual's **"Edge List Columns"** bucket:
   - `source_label`
   - `source_cluster`
   - `source_x`, `source_y`, `source_z`
   - `target_label`
   - `target_cluster`
   - `target_x`, `target_y`, `target_z`
   - `weight`
4. **Critical**: for every numeric column after dropping it in the bucket,
   click the dropdown arrow next to it and choose **"Don't summarize"**.
   Power BI defaults to SUM which will break the coordinates.
5. The 3D graph should appear.  Drag to rotate, scroll to zoom, right-click
   to pan.

---

## Development / live preview mode

If you want to iterate on `visual.ts` without re-packaging each time:

1. Enable **Developer Visual** in Power BI Desktop:
   - File → Options → Security → check "Enable custom visuals developed
     using the Power BI SDK developer tools".
2. In the `spectral3d` folder:
   ```cmd
   pbiviz start
   ```
3. In Power BI Desktop, add the **Developer Visual** from the Visualizations
   pane (it connects to the local pbiviz dev server on port 8080).
4. Edits to `src/visual.ts` hot-reload automatically.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Graph blank, no error | Columns not mapped | Add all 11 columns to Edge List Columns bucket |
| Red error: "Missing columns: ..." | Column names changed | Check column names in Power Query match CSV originals |
| Coordinates look wrong / all nodes at origin | Numeric columns being aggregated | Set all coordinate/weight columns to "Don't summarize" |
| WebGL error | GPU disabled | Power BI Desktop on physical hardware should have WebGL. Check DirectX is working. |
| `pbiviz package` fails with TypeScript errors | Type mismatch | Run `npm install` again; delete `.tmp/` folder and retry |

---

## File map

```
powerbi_visual/
├── README.md                    This file
├── combine_periods.py           Optional: merges 3 CSVs for multi-period slicing
├── spectral3d/                  Production visual
│   ├── assets/icon.png          Placeholder icon (replace with any 20×20 PNG)
│   ├── src/
│   │   ├── visual.ts            Main visual (Plotly 3D rendering + data parsing)
│   │   └── plotly.d.ts          Minimal TypeScript types for plotly.js-dist-min
│   ├── style/visual.less        Minimal container styles
│   ├── capabilities.json        One data role: "Edge List Columns" (table mapping)
│   ├── package.json             npm deps: powerbi-visuals-tools, plotly.js-dist-min
│   ├── pbiviz.json              Visual metadata
│   ├── tsconfig.json            TypeScript config
│   └── dist/spectral3d.pbiviz   Compiled visual — import this into Power BI Desktop
└── archive/
    └── spectral3dv2/            Experimental v2 variant (not in active use)
```

Data source (unchanged project files):
```
plots/input/spectral_graph_data_2010_2014.csv
plots/input/spectral_graph_data_2015_2019.csv
plots/input/spectral_graph_data_2020_2024.csv
```

---

## How this stays isolated from the existing website

- `powerbi_visual/` has its own `package.json` and `node_modules/`.  
  Running `npm install` here does not affect any other part of the repo.
- The source CSVs in `plots/input/` are read-only inputs to Power BI;  
  nothing here writes to them.
- The existing `index.html`, `spectral_*.html`, and `tableau_extension/`  
  files are completely unaffected.
