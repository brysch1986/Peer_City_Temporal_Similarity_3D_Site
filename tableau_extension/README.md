# Peer City Spectral Graphs — Tableau Dashboard Extension

Renders the three interactive 3D peer-city spectral clustering graphs inside
Tableau Desktop on Windows. The extension reuses the existing pre-generated
graph HTML files from this repository (`plots/spectral_YYYY_YYYY.html`).

---

## Prerequisites

- Tableau Desktop 2019.3 or later (local HTTP extensions are supported)
- Python 3 (for the local file server — already required by the main project)
- The existing graph HTML files must be present in `plots/`
  (run `Build_Public_Site_Graphs.py` if they are missing or stale)

---

## Windows local setup

All commands run from the **repo root** (the folder containing `index.html`).

### 1. Confirm graph files exist

```
plots\spectral_2010_2014.html
plots\spectral_2015_2019.html
plots\spectral_2020_2024.html
```

If any are missing, regenerate them:

```cmd
python Build_Public_Site_Graphs.py
```

> Note: `Build_Public_Site_Graphs.py` currently hard-codes the 2010–2014
> period. Adjust `INPUT_CSV` and `OUTPUT_HTML` at the top of the script and
> re-run for each of the three periods.

### 2. Start the local HTTP server

Open a Command Prompt or PowerShell window, `cd` to the repo root, and run:

```cmd
python -m http.server 8765
```

Leave this window open while using the extension in Tableau.

Verify it works by visiting in your browser:

```
http://localhost:8765/tableau_extension/index.html
```

You should see the 2020–2024 graph with the period dropdown.

### 3. Load the extension in Tableau Desktop

1. Open Tableau Desktop.
2. Open an existing workbook, or create a new one (any data source is fine).
3. Navigate to a **Dashboard** sheet (or create one).
4. In the **Dashboard** panel on the left, scroll to the bottom and drag an
   **Extension** object onto the dashboard canvas.
5. In the "Add an Extension" dialog, click **"Access Local Extensions"**
   (bottom-left link).
6. Browse to and select:
   ```
   tableau_extension\plotly_extension.trex
   ```
7. When prompted about permissions, click **OK / Allow**.
   (The extension requests no Tableau data permissions.)
8. The 3D graph will appear inside the dashboard pane.

### 4. Interact with the graph

- Use the **Period** dropdown in the extension toolbar to switch between
  2010–2014, 2015–2019, and 2020–2024.
- The embedded Plotly graph supports full rotate / zoom / pan interaction.

---

## Stopping the server

Press `Ctrl+C` in the Command Prompt window where `python -m http.server 8765`
is running.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| "Extension initialization failed" message | Tableau Extensions API CDN unreachable | Check internet connection; or download `tableau.extensions.1.latest.min.js` and update the `<script src>` in `index.html` to a local path |
| White/blank iframe | Server not running | Start `python -m http.server 8765` from repo root |
| "Site not allowed" error in Tableau | Tableau's safe-list doesn't include localhost | In Tableau Desktop: Help → Settings and Performance → Manage Dashboard Extensions → add `http://localhost:8765` |
| Graph files not found (404) | Server started from wrong directory | Must run `python -m http.server` from the repo **root**, not from inside `tableau_extension/` |

---

## File map

```
tableau_extension/
├── plotly_extension.trex   Tableau manifest — points to localhost:8765
├── index.html              Extension UI (period selector + iframe)
├── app.js                  Tableau Extensions API init + period-swap logic
└── README.md               This file
```

The extension loads these **existing, unchanged** repo files via iframe:

```
plots/spectral_2010_2014.html
plots/spectral_2015_2019.html
plots/spectral_2020_2024.html
```

---

## Changing the server port

If port 8765 is in use, pick any free port and update **two places**:

1. The `python -m http.server` command (e.g., `8766`)
2. The `<url>` in `plotly_extension.trex`:
   ```xml
   <url>http://localhost:8766/tableau_extension/index.html</url>
   ```

Save the `.trex` file and re-load the extension in Tableau.

---

## Privacy

The extension makes no network requests except:

- Loading `tableau.extensions.1.latest.min.js` from
  `extensions.tableau.com` (Tableau's own CDN, one request on load)
- Loading `plotly-3.x.x.min.js` from `cdn.plot.ly` (already loaded by the
  existing graph HTML files)

No project data leaves the machine. The CSV data and graph content are served
entirely from localhost.
