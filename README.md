# OBD2 Engine Diagnostics Telemetry Lab

A Streamlit dashboard for visualizing and diagnosing engine health from OBD2 CSV telemetry logs.

## Features

- **Fuel Trim Diagnostic Gauge** — Sums STFT + LTFT and flags a warning when total exceeds ±10% (vacuum leak / unmetered air indicator)
- **RPM vs. Fuel Trim Scatter Plot** — Filter by engine load to pinpoint rich/lean conditions across the RPM range
- **O₂ Sensor Waveform Sweeps** — Front vs. rear O₂ voltage oscillations to assess catalytic converter health

## Dataset

Simulated OBD2 telemetry at 1Hz over a 600-second drive cycle (Idle → Acceleration → Highway Cruise → Return to Idle).

| Column | Unit | Description |
|---|---|---|
| Timestamp_sec | s | Elapsed time |
| Engine_RPM | RPM | Engine speed |
| Engine_Load_Pct | % | Calculated engine load |
| Mass_Air_Flow_g_s | g/s | Mass air flow sensor |
| Short_Term_Fuel_Trim_Pct | % | Short-term fuel correction |
| Long_Term_Fuel_Trim_Pct | % | Long-term fuel correction |
| O2_Front_Volts | V | Upstream O₂ sensor (pre-cat) |
| O2_Rear_Volts | V | Downstream O₂ sensor (post-cat) |

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
streamlit run app.py
```

To regenerate the dataset:

```bash
python data/generate_dataset.py
```

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Production-ready releases only |
| `develop` | Integration — all features merge here first |
| `feature/*` | One branch per feature |

## Project Structure

```
engine-diagnostics-dashboard/
├── app.py                  # Streamlit entry point
├── data/
│   ├── generate_dataset.py # Dataset generation script
│   └── engine_telemetry_log.csv
├── src/
│   ├── ingest.py           # CSV loading and validation
│   ├── transforms.py       # Fuel trim calculations and classifications
│   ├── diagnostics.py      # Threshold logic and alert flags
│   └── charts.py           # Plotly chart builders
├── requirements.txt
└── README.md
```