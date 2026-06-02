# OBD2 Engine Diagnostics Telemetry Lab

A production-grade Streamlit dashboard for visualizing and diagnosing engine health from OBD2 automotive telemetry logs. Built with a modular architecture, feature-branch Git workflow, and interactive Plotly charts.

---

## What It Does

Instead of generic business data, this dashboard visualizes real-world automotive sensor time-series — the kind of data a mechanic reads from a scan tool. Three diagnostic panels work together to tell a complete engine health story:

### 1. Fuel Trim Diagnostic Gauge
Displays the latest **Short Term Fuel Trim (STFT)** and **Long Term Fuel Trim (LTFT)** as individual KPI metrics, then sums them into a **Total Fuel Trim** reading.

- If total trim exceeds **±10%**, a conditional warning fires with a plain-English diagnosis
- **Positive breach (> +10%)** → engine running lean → vacuum leak or unmetered air
- **Negative breach (< -10%)** → engine running rich → over-fueling or injector leak
- **% Time in Warning** shows how much of the drive cycle the engine spent outside the healthy band

### 2. RPM vs. Total Fuel Trim Scatter Plot
Every sensor reading plotted as a dot — RPM on the X axis, Total Fuel Trim on the Y axis, colored by mixture status (Lean / Nominal / Rich).

- ±10% threshold lines drawn as reference
- **Engine Load slider** in the sidebar filters points by load percentage in real time
- Isolate idle (0–20% load) to see the lean cluster, or cruise (40–60%) to see normalized trims

### 3. O₂ Sensor Waveform Sweeps
Dual-line chart tracking front (pre-cat) and rear (post-cat) oxygen sensor voltages over time.

- **Front O₂** oscillates rapidly between ~0.1V and ~0.9V — normal upstream switching behavior
- **Rear O₂** stays dampened and flat when the catalytic converter is healthy
- A rear sensor that starts mimicking the front is a dead cat
- **Time window slider** lets you zoom into any phase of the drive cycle
- Stoichiometric reference line at 0.45V (λ=1)

---

## The Dataset

Simulated OBD2 telemetry at **1Hz over 600 seconds**, modeling a realistic drive cycle:

| Phase | Time | Engine Condition |
|---|---|---|
| Idle | 0–120s | Vacuum leak signature — high positive fuel trims |
| Hard Acceleration | 120–240s | 750 → 3,500 RPM, trims normalize under load |
| Highway Cruise | 240–480s | Steady 2,400 RPM, stable mixture |
| Return to Idle | 480–600s | Vacuum leak returns as manifold vacuum rises |

### Column Schema

| Column | Unit | Description |
|---|---|---|
| `Timestamp_sec` | s | Elapsed time at 1Hz |
| `Engine_RPM` | RPM | Engine rotational speed |
| `Engine_Load_Pct` | % | Calculated engine load |
| `Mass_Air_Flow_g_s` | g/s | Mass air flow sensor reading |
| `Short_Term_Fuel_Trim_Pct` | % | ECU's immediate fuel correction |
| `Long_Term_Fuel_Trim_Pct` | % | ECU's learned long-term correction |
| `O2_Front_Volts` | V | Upstream O₂ sensor (pre-catalytic converter) |
| `O2_Rear_Volts` | V | Downstream O₂ sensor (post-catalytic converter) |

---

## Project Structure

```
engine-diagnostics-dashboard/
├── app.py                      # Streamlit entry point — layout and wiring only
├── data/
│   ├── generate_dataset.py     # Reproducible dataset generation script
│   └── engine_telemetry_log.csv
├── src/
│   ├── __init__.py
│   ├── ingest.py               # CSV loading, schema validation, dtype enforcement
│   ├── transforms.py           # Total fuel trim calculation, mixture classification
│   ├── diagnostics.py          # ±10% threshold logic, alert messages, KPI aggregations
│   └── charts.py               # Plotly chart builders (scatter + O2 waveform)
├── requirements.txt            # Pinned dependencies
└── README.md
```

### Module Responsibilities

| Module | Responsibility |
|---|---|
| `ingest.py` | Loads CSV, validates all required columns exist, coerces to float64, raises descriptive errors on bad data |
| `transforms.py` | Computes `Total_Fuel_Trim_Pct` (STFT + LTFT), classifies each reading as Lean / Nominal / Rich using `np.select` |
| `diagnostics.py` | Evaluates latest reading against ±10% threshold, generates warning message, computes fleet-level KPIs |
| `charts.py` | Builds the RPM scatter plot with load filtering and the dual O₂ waveform chart, both in Plotly dark theme |
| `app.py` | Streamlit layout only — imports from `src/`, no business logic lives here |

---

## Setup

```bash
# Clone and enter the project
git clone https://github.com/navneet-singh2907/engine-diagnostics-dashboard.git
cd engine-diagnostics-dashboard

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux

# Install pinned dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

Open your browser at `http://localhost:8501`

### Regenerate the Dataset

```bash
python data/generate_dataset.py
```

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | 1.35.0 | Dashboard framework and UI components |
| `pandas` | 2.2.2 | Data loading, transformation, and filtering |
| `numpy` | 1.26.4 | Vectorised conditional logic (`np.select`) |
| `plotly` | 5.22.0 | Interactive scatter and line charts |

---

## Git Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Production-ready releases only |
| `develop` | Integration — all feature branches merge here first |
| `feature/*` | One branch per feature, merged via `--no-ff` |
| `fix/*` | Bug fixes and peer-review refactors |

### Completed Branches

| Branch | What it delivered |
|---|---|
| `feature/project-setup` | Directory structure, dataset generation, pinned requirements |
| `feature/data-ingestion` | `src/ingest.py` — CSV loader with schema validation |
| `feature/fuel-trim-diagnostics` | `src/transforms.py`, `src/diagnostics.py` — fuel trim logic and alerts |
| `feature/streamlit-ui` | `app.py` — Cupcake MVP with fuel trim gauge |
| `feature/rpm-scatter-plot` | `src/charts.py` — scatter and O₂ waveform chart builders |
| `feature/dashboard-wiring` | Full chart integration with sidebar sliders |
| `fix/classify-mixture-refactor` | Replaced fragile `map/fillna` chain with `np.select` |

---

## Diagnostic Logic Reference

```
Total Fuel Trim = STFT + LTFT

If Total > +10%  →  Engine LEAN  →  Possible vacuum leak / unmetered air
If Total < -10%  →  Engine RICH  →  Possible over-fueling / injector leak
If -10% ≤ Total ≤ +10%  →  NOMINAL
```

O₂ sensor health rule:

```
Front O₂ oscillates  +  Rear O₂ stays flat    =  Healthy catalytic converter
Front O₂ oscillates  +  Rear O₂ also oscillates  =  Cat is failing or dead
```