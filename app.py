import streamlit as st
from src.ingest import load_telemetry
from src.transforms import apply_all
from src.diagnostics import get_fuel_trim_alert, get_fleet_summary

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

# ── Placeholder sections for upcoming features ─────────────────────────────────
st.subheader("RPM vs. Total Fuel Trim")
st.info("Coming in `feature/rpm-scatter-plot`")

st.subheader("O₂ Sensor Waveform Sweeps")
st.info("Coming in `feature/o2-waveform-charts`")