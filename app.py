import streamlit as st
from src.ingest import load_telemetry
from src.transforms import apply_all
from src.diagnostics import get_fuel_trim_alert, get_fleet_summary
from src.charts import rpm_vs_fuel_trim_scatter, o2_waveform_chart

st.set_page_config(
    page_title="OBD2 Engine Diagnostics Lab",
    page_icon="🔧",
    layout="wide",
)

st.title("🔧 OBD2 Engine Diagnostics Telemetry Lab")
st.caption("Real-time automotive sensor analysis — fuel trim, RPM dynamics, and catalytic converter health")

# ── Data load ──────────────────────────────────────────────────────────────────
DATA_PATH = "data/engine_telemetry_log.csv"

@st.cache_data
def load_data():
    df = load_telemetry(DATA_PATH)
    return apply_all(df)

try:
    df = load_data()
except (FileNotFoundError, ValueError) as e:
    st.error(f"Failed to load telemetry data: {e}")
    st.stop()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Controls")
    st.markdown(f"**Dataset:** `{DATA_PATH}`")
    st.markdown(f"**Samples:** {len(df):,} @ 1Hz ({len(df)//60} min {len(df)%60} sec)")
    st.divider()

    st.markdown("**RPM Scatter — Engine Load Filter**")
    load_range = st.slider(
        "Engine Load (%)",
        min_value=0.0,
        max_value=100.0,
        value=(0.0, 100.0),
        step=1.0,
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("**O₂ Waveform — Time Window**")
    time_range = st.slider(
        "Time (seconds)",
        min_value=0,
        max_value=599,
        value=(0, 599),
        step=1,
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("**Drive Cycle Phases**")
    st.markdown("- `0–120s` Idle (vacuum leak zone)")
    st.markdown("- `120–240s` Hard Acceleration")
    st.markdown("- `240–480s` Highway Cruise")
    st.markdown("- `480–600s` Return to Idle")

# ── KPI row ───────────────────────────────────────────────────────────────────
alert = get_fuel_trim_alert(df)
summary = get_fleet_summary(df)

st.subheader("Fuel Trim Diagnostic Gauge")

col1, col2, col3, col4 = st.columns(4)
col1.metric("STFT (latest)", f"{alert['stft']:+.1f}%")
col2.metric("LTFT (latest)", f"{alert['ltft']:+.1f}%")
col3.metric(
    "Total Fuel Trim",
    f"{alert['total']:+.1f}%",
    delta=f"{'⚠ BREACH' if alert['breached'] else 'nominal'}",
    delta_color="inverse" if alert["breached"] else "off",
)
col4.metric("Time in Warning", f"{summary['pct_time_in_warning']}%")

if alert["breached"]:
    st.warning(alert["message"])
else:
    st.success(alert["message"])

st.divider()

# ── RPM Scatter ────────────────────────────────────────────────────────────────
st.subheader("RPM vs. Total Fuel Trim")
st.caption("Filter by engine load in the sidebar to isolate rich/lean conditions across the RPM range.")

scatter_fig = rpm_vs_fuel_trim_scatter(df, load_range)
filtered_count = len(df[df["Engine_Load_Pct"].between(load_range[0], load_range[1])])
st.plotly_chart(scatter_fig, use_container_width=True)
st.caption(f"{filtered_count:,} of {len(df):,} samples visible at load {load_range[0]:.0f}%–{load_range[1]:.0f}%")

st.divider()

# ── O2 Waveform ───────────────────────────────────────────────────────────────
st.subheader("O₂ Sensor Waveform Sweeps")
st.caption("A healthy catalytic converter keeps the rear O₂ signal flat while the front oscillates freely.")

o2_fig = o2_waveform_chart(df, (float(time_range[0]), float(time_range[1])))
st.plotly_chart(o2_fig, use_container_width=True)

col_a, col_b = st.columns(2)
col_a.metric("Front O₂ Mean", f"{df['O2_Front_Volts'].iloc[time_range[0]:time_range[1]].mean():.3f} V")
col_b.metric("Rear O₂ Mean", f"{df['O2_Rear_Volts'].iloc[time_range[0]:time_range[1]].mean():.3f} V")