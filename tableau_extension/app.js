document.addEventListener("DOMContentLoaded", () => {
  const statusEl = document.getElementById("status");
  const periodEl = document.getElementById("periodSelect");
  const graphEl  = document.getElementById("graph");

  function setStatus(msg) {
    if (statusEl) statusEl.textContent = msg;
  }

  function loadGraph(period) {
    setStatus(`Loading ${period}\u2026`);

    fetch(`spectral_${period}.json`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status} fetching spectral_${period}.json`);
        return r.json();
      })
      .then((fig) => {
        // Merge layout: keep the exported layout but force autosize so Plotly
        // fills whatever height the extension pane gives us.
        const layout = Object.assign({}, fig.layout, {
          autosize: true,
          margin: { l: 0, r: 0, t: 80, b: 0 },
        });
        return Plotly.react(graphEl, fig.data, layout, { responsive: true });
      })
      .then(() => setStatus("Loaded"))
      .catch((err) => {
        setStatus(`Error: ${err.message}`);
        console.error(err);
      });
  }

  periodEl.addEventListener("change", () => loadGraph(periodEl.value));

  // Initial load
  loadGraph(periodEl.value);

  // Tableau init is fire-and-forget: the graph renders whether or not
  // this succeeds (works in plain browser for local testing too).
  if (window.tableau && tableau.extensions && tableau.extensions.initializeAsync) {
    tableau.extensions.initializeAsync().catch((err) => {
      console.error("Tableau init failed:", err);
    });
  }
});
