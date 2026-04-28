# Peer City Temporal Similarity — 3D Visualization

**Learning from Peer Cities: A Temporal Similarity Analysis of Jacksonville**  
Anne Howell — Advisor: Dr. Karthikeyan Umapathy

**Stakeholders:** State of Jax, City of Jacksonville Initiative  
**Powered by:** mySidewalk

This repository is a companion visualization repo for the larger **Peer City Temporal Similarity** project. It hosts the Plotly-based 3D graph website and related Power BI visual workflow used to display interactive spectral graph views from the main analysis.

**Main project repository:** [Peer_City_Temporal_Similarity](https://github.com/annehowell/Peer_City_Temporal_Similarity)  
**Live 3D site:** [Peer City Temporal Similarity 3D Site](https://annehowell.github.io/Peer_City_Temporal_Similarity_3D_Site/)

---

**Live site:** https://annehowell.github.io/Peer_City_Temporal_Similarity_3D_Site/
*(URL is inferred from the GitHub username. If the site is not loading, confirm that GitHub Pages is enabled in the repository Settings → Pages, set to deploy from the `main` branch root.)*

This repo contains two independent but related things:

1. **A hosted website** — interactive 3D Plotly graphs showing peer-city spectral clustering similarity across three five-year periods.
2. **A Power BI custom visual** — the same graphs rendered inside Power BI Desktop, loaded directly from the project's CSV files.

---

## Quick start

### Refresh the website after a data update
```
# 1. Drop the new CSV into plots/input/
# 2. Register the new period in two places (see "Adding a New Time Bin")
# 3. Regenerate the graph HTML:
python scripts/build_site_graphs.py

# 4. Commit and push plots/spectral_*.html and index.html
git add plots/spectral_*.html index.html
git commit -m "Add YYYY-YYYY period"
git push
```

### Rebuild the Power BI visual
```
cd powerbi_visual/spectral3d
npm install          # only needed the first time or after dependency changes
pbiviz package       # produces dist/spectral3d*.pbiviz
```
Import the `.pbiviz` file into Power BI Desktop via the Visualizations pane → **... → Import a visual from a file**.

---

## Repo structure

```
/
├── index.html                    Website entry point (GitHub Pages root)
├── .nojekyll                     Tells GitHub Pages to skip Jekyll processing
│
├── plots/
│   ├── input/                    Source data (one CSV per period — do not edit by hand)
│   │   ├── spectral_graph_data_2010_2014.csv
│   │   ├── spectral_graph_data_2015_2019.csv
│   │   └── spectral_graph_data_2020_2024.csv
│   ├── spectral_2010_2014.html   Generated — do not edit directly
│   ├── spectral_2015_2019.html   Generated — do not edit directly
│   └── spectral_2020_2024.html   Generated — do not edit directly
│
├── scripts/
│   └── build_site_graphs.py      Reads CSVs from plots/input/, writes HTML to plots/
│
├── powerbi_visual/
│   ├── README.md                 Full Power BI setup and usage guide
│   ├── combine_periods.py        Optional: merges all CSVs for multi-period slicing in Power BI
│   ├── spectral3d/               Production Power BI custom visual (TypeScript source + compiled output)
│   │   ├── src/visual.ts         Visual source
│   │   ├── dist/                 Compiled .pbiviz — import this into Power BI Desktop
│   │   └── package.json          npm dependencies
│   └── archive/spectral3dv2/     Experimental v2 variant, not in active use
│
└── tableau_extension/            Tableau Desktop extension (separate workflow, see its README)
```

---

## Prerequisites

### For website graph generation
| Requirement | Notes |
|-------------|-------|
| Python 3.x | Must have `numpy`, `pandas`, and `plotly` installed |
| plotly | `pip install plotly` |
| pandas | `pip install pandas` |
| numpy | `pip install numpy` |

> **Note:** If your system has multiple Python installations, make sure you invoke the one that has these packages. Example with Anaconda: `D:\Anaconda\python.exe scripts/build_site_graphs.py`

### For Power BI visual development
| Requirement | Notes |
|-------------|-------|
| Node.js 18 LTS or later | https://nodejs.org |
| npm | Ships with Node.js |
| powerbi-visuals-tools | Installed locally via `npm install` in `spectral3d/` |
| Power BI Desktop | Windows only; free from Microsoft |

---

## Data format

Each CSV in `plots/input/` is an **edge list** — one row per connection between two cities. All 11 columns are required:

| Column | Type | Description |
|--------|------|-------------|
| `source_label` | string | City name for the edge source node |
| `source_cluster` | integer | Cluster assignment (0, 1, 2, …) — controls node color |
| `source_x` | float | 3D embedding X coordinate |
| `source_y` | float | 3D embedding Y coordinate |
| `source_z` | float | 3D embedding Z coordinate |
| `target_label` | string | City name for the edge target node |
| `target_cluster` | integer | Cluster assignment for the target node |
| `target_x` | float | 3D embedding X coordinate |
| `target_y` | float | 3D embedding Y coordinate |
| `target_z` | float | 3D embedding Z coordinate |
| `weight` | float (0–1) | Edge weight / similarity score |

File naming convention: `spectral_graph_data_{YYYY}_{YYYY}.csv` (e.g., `spectral_graph_data_2025_2029.csv`).

The coordinates and cluster assignments are expected to come from your upstream spectral clustering pipeline. This repo does not perform the clustering — it only visualizes the results.

---

## Website workflow

The website is a static site served by GitHub Pages. `index.html` presents a dropdown; each option loads a pre-generated self-contained Plotly HTML file into an `<iframe>`. Nothing runs server-side.

### How the files relate

```
plots/input/spectral_graph_data_YYYY_YYYY.csv
        ↓  (build_site_graphs.py)
plots/spectral_YYYY_YYYY.html
        ↓  (served via iframe)
index.html  ←  user selects period from dropdown
```

### Step-by-step: update the website

1. **Replace or add the CSV** in `plots/input/` with updated data in the format described above.

2. **Regenerate graph HTML:**
   ```
   python scripts/build_site_graphs.py
   ```
   This overwrites all HTML files listed in the script's `PERIODS` list. It does not touch any CSV files.

3. **Verify locally** by opening `index.html` directly in a browser (or via a local server). Check that:
   - The dropdown shows the correct period labels.
   - The on-graph title inside each Plotly figure matches the selected period.
   - The graph data (city positions, edges) looks correct.

4. **Commit and push:**
   ```
   git add plots/spectral_*.html
   git commit -m "Regenerate graphs for YYYY-YYYY update"
   git push
   ```
   GitHub Pages deploys automatically from the `main` branch within a minute or two.

---

## Adding a new time bin

When new period data becomes available, three things must be updated:

### Step 1 — Add the CSV
Place the new edge-list CSV in:
```
plots/input/spectral_graph_data_{YYYY}_{YYYY}.csv
```

### Step 2 — Register the period in the build script
Open `scripts/build_site_graphs.py` and add a line to the `PERIODS` list:
```python
PERIODS = [
    ("2010_2014", "2010–2014"),
    ("2015_2019", "2015–2019"),
    ("2020_2024", "2020–2024"),
    ("2025_2029", "2025–2029"),   # ← add this line
]
```
- First element: matches the CSV filename suffix (underscores, no spaces).
- Second element: the label displayed in the graph title and dropdown (use an en-dash `–`).

### Step 3 — Register the period in the website dropdown
Open `index.html` and add an `<option>` to the `<select>` block:
```html
<select id="period">
  <option value="plots/spectral_2010_2014.html" selected>2010–2014</option>
  <option value="plots/spectral_2015_2019.html">2015–2019</option>
  <option value="plots/spectral_2020_2024.html">2020–2024</option>
  <option value="plots/spectral_2025_2029.html">2025–2029</option>  <!-- add this -->
</select>
```

### Step 4 — Regenerate, verify, commit
```
python scripts/build_site_graphs.py
# verify in browser
git add plots/spectral_2025_2029.html index.html scripts/build_site_graphs.py
git commit -m "Add 2025-2029 time bin"
git push
```

> **Important:** The dropdown in `index.html` and the `PERIODS` list in the build script are independent — both must be updated. Forgetting one will cause either a missing graph file (404 in the iframe) or a missing dropdown option.

---

## Power BI workflow

The Power BI custom visual (`powerbi_visual/spectral3d/`) renders the same 3D spectral graph inside Power BI Desktop. Data comes directly from the CSV files — no separate build step is needed for the data itself.

Full setup and usage instructions are in [powerbi_visual/README.md](powerbi_visual/README.md). Key points are summarized below.

### Loading data into Power BI

**Single period** — load one CSV directly:
- Power BI Desktop → Home → Get data → Text/CSV → select `plots/input/spectral_graph_data_YYYY_YYYY.csv`
- In the data model, set all numeric columns (`source_x`, `source_y`, `source_z`, `target_x`, `target_y`, `target_z`, `source_cluster`, `target_cluster`, `weight`) to **Don't summarize**.

**All periods with a slicer** — merge the CSVs first:
```
python powerbi_visual/combine_periods.py
```
Output: `powerbi_visual/spectral_all_periods.csv` — load this, then add a Power BI Slicer on the `period` column.

### Using the pre-compiled visual

The compiled `.pbiviz` file is already in `powerbi_visual/spectral3d/dist/`. To use it without rebuilding:

1. Power BI Desktop → Visualizations pane → **... → Import a visual from a file**
2. Select `powerbi_visual/spectral3d/dist/spectral3d*.pbiviz`
3. Click the new "Peer City Spectral 3D" icon to add it to the canvas
4. Drag all 11 CSV columns into the visual's **Edge List Columns** field bucket
5. Set every numeric column to **Don't summarize** (click the column dropdown in the field bucket)

### Rebuilding the visual after source changes

Only needed if you modify `powerbi_visual/spectral3d/src/visual.ts` or its dependencies:
```
cd powerbi_visual/spectral3d
npm install       # first time or after package.json changes
pbiviz package    # outputs to dist/
```

### When a new time bin is added

1. If using single-period mode: load the new CSV directly — no Power BI visual rebuild needed.
2. If using the merged CSV: re-run `python powerbi_visual/combine_periods.py` and refresh the data source in Power BI Desktop.
3. The visual itself does not need to be repackaged unless the data schema changes.

---

## Deployment

The site is hosted on **GitHub Pages** from the root of the `main` branch. The `.nojekyll` file in the repo root tells GitHub Pages to serve files directly without Jekyll processing.

Deployment is automatic: pushing to `main` triggers a GitHub Pages rebuild, typically within 60–90 seconds.

To confirm Pages is enabled: GitHub repo → Settings → Pages → Source should be set to `main` branch, root `/`.

---

## Known limitations and maintenance notes

- **Python environment must have numpy, pandas, plotly.** If you have multiple Python installs, be explicit about which one you invoke. The build script uses only standard scientific Python — any conda or venv with these packages works.

- **Two places must be kept in sync when adding a period.** The `PERIODS` list in `scripts/build_site_graphs.py` and the `<option>` list in `index.html` are not linked. See "Adding a New Time Bin" above.

- **The build script regenerates all periods every run.** There is no incremental build. If you only changed one period's CSV, all three (or more) HTML files will be rewritten. This is intentional — it keeps all graph files consistent.

- **Graph HTML files are committed output.** `plots/spectral_*.html` are generated files but are committed to the repo so that GitHub Pages can serve them without a build step. They should not be edited by hand.

- **Power BI `node_modules/` is not committed** (covered by `.gitignore`). Run `npm install` inside `powerbi_visual/spectral3d/` before attempting to package the visual on a new machine.

- **The compiled `.pbiviz` is committed.** Unlike `node_modules`, the `dist/` folder is tracked so the visual can be downloaded directly from the repo without a local build. Rebuild and commit it when `visual.ts` changes.

- **Tableau extension** is in `tableau_extension/` and requires a local HTTP server on port 8765. It is a separate workflow not covered by this README — see `tableau_extension/README.md`.
