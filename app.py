import streamlit as st
from src.ingest import load_telemetry
from src.transforms import apply_all
from src.diagnostics import get_fuel_trim_alert, get_fleet_summary
from src.charts import rpm_vs_fuel_trim_scatter, o2_waveform_chart
from src.nhtsa import get_fault_context
from src.styles import GLOBAL_CSS, badge, card

st.set_page_config(
    page_title="OBD2 Engine Diagnostics Lab",
    page_icon="🔧",
    layout="wide",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Hero header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">🔧 OBD2 Engine Diagnostics Telemetry Lab</div>
    <div class="hero-subtitle">
        Real-time automotive fault detection &amp; NHTSA vehicle intelligence
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔧 Controls")

    uploaded_file = st.file_uploader("Upload OBD2 CSV", type=["csv"])

    st.divider()
    st.markdown("**RPM Scatter — Engine Load Filter**")
    load_range = st.slider(
        "Engine Load (%)",
        min_value=0.0, max_value=100.0,
        value=(0.0, 100.0), step=1.0,
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("**O₂ Waveform — Time Window**")
    time_range = st.slider(
        "Time (seconds)",
        min_value=0, max_value=599,
        value=(0, 599), step=1,
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("**Drive Cycle Phases**")
    st.markdown("- `0–120s` Idle (vacuum leak zone)")
    st.markdown("- `120–240s` Hard Acceleration")
    st.markdown("- `240–480s` Highway Cruise")
    st.markdown("- `480–600s` Return to Idle")

    st.divider()
    st.markdown(
        '<div class="sidebar-footer">v2.0.0 · '
        '<a href="https://github.com/navneet-singh2907/engine-diagnostics-dashboard" '
        'style="color:#38bdf8;">GitHub</a></div>',
        unsafe_allow_html=True,
    )

# ── Data load ──────────────────────────────────────────────────────────────────
DEFAULT_PATH = "data/engine_telemetry_log.csv"

@st.cache_data(show_spinner="Loading telemetry data...")
def load_default():
    return apply_all(load_telemetry(DEFAULT_PATH))

try:
    if uploaded_file is not None:
        df = apply_all(load_telemetry(uploaded_file))
        source_label = f"📁 {uploaded_file.name}"
    else:
        df = load_default()
        source_label = f"📂 {DEFAULT_PATH} (bundled)"
except (FileNotFoundError, ValueError) as e:
    st.error(f"Failed to load telemetry data: {e}")
    st.stop()

st.caption(f"**Source:** {source_label} · {len(df):,} samples @ 1Hz")

# ── Fuel Trim Diagnostic Gauge ─────────────────────────────────────────────────
alert = get_fuel_trim_alert(df)
summary = get_fleet_summary(df)

if alert["breached"]:
    badge_html = badge(f"🔴 FAULT DETECTED — Engine Running {alert['direction'].title()}", "fault")
elif summary["pct_time_in_warning"] > 20:
    badge_html = badge("🟡 WARNING — Monitor Fuel Trim Closely", "warning")
else:
    badge_html = badge("🟢 NOMINAL — All Systems Healthy", "nominal")

st.markdown(
    card(f"""
        {badge_html}
        <br><br>
        <b>Diagnosis:</b> {alert['message']}
    """, header="⚡ Fuel Trim Diagnostic Gauge"),
    unsafe_allow_html=True,
)

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

st.divider()

# ── RPM Scatter ────────────────────────────────────────────────────────────────
st.markdown(
    card("", header="📊 RPM vs. Total Fuel Trim"),
    unsafe_allow_html=True,
)
st.caption("Filter by engine load in the sidebar to isolate rich/lean conditions across the RPM range.")

filtered_count = len(df[df["Engine_Load_Pct"].between(load_range[0], load_range[1])])
if filtered_count == 0:
    st.warning(f"No data points match engine load {load_range[0]:.0f}%–{load_range[1]:.0f}%. Widen the range in the sidebar.")
else:
    st.plotly_chart(rpm_vs_fuel_trim_scatter(df, load_range), use_container_width=True)
    st.caption(f"{filtered_count:,} of {len(df):,} samples visible at load {load_range[0]:.0f}%–{load_range[1]:.0f}%")

st.divider()

# ── O2 Waveform ───────────────────────────────────────────────────────────────
st.markdown(
    card("", header="〰️ O₂ Sensor Waveform Sweeps"),
    unsafe_allow_html=True,
)
st.caption("A healthy catalytic converter keeps the rear O₂ signal flat while the front oscillates freely.")

st.plotly_chart(
    o2_waveform_chart(df, (float(time_range[0]), float(time_range[1]))),
    use_container_width=True,
)
col_a, col_b = st.columns(2)
col_a.metric("Front O₂ Mean", f"{df['O2_Front_Volts'].iloc[time_range[0]:time_range[1]].mean():.3f} V")
col_b.metric("Rear O₂ Mean", f"{df['O2_Rear_Volts'].iloc[time_range[0]:time_range[1]].mean():.3f} V")

st.divider()

# ── NHTSA Vehicle Intelligence ─────────────────────────────────────────────────
st.markdown(
    card("", header="🚗 Vehicle Intelligence — NHTSA Recall & Complaint Lookup"),
    unsafe_allow_html=True,
)

vcol1, vcol2, vcol3, vcol4 = st.columns([2, 2, 1, 1])
make = vcol1.text_input("Make", placeholder="e.g. Toyota")
model = vcol2.text_input("Model", placeholder="e.g. Camry")
year = vcol3.number_input("Year", min_value=1990, max_value=2025, value=2019, step=1)
lookup = vcol4.button("🔍 Look Up", disabled=not (make and model), use_container_width=True)

@st.cache_data(ttl=3600, show_spinner=False)
def _cached_fault_context(make, model, year, direction):
    return get_fault_context(make, model, year, direction)

if lookup and make and model:
    with st.spinner("Querying NHTSA database..."):
        ctx = _cached_fault_context(make.strip(), model.strip(), int(year), alert["direction"])

    rcol1, rcol2, rcol3 = st.columns(3)
    rcol1.metric("Active Recalls", ctx["recall_count"])
    rcol2.metric("Total Complaints", ctx["total_complaints"])
    rcol3.metric(
        f"Fault-Relevant Complaints",
        ctx["relevant_complaints"],
        help=f"Complaints matching {', '.join(ctx['dtc_codes']) if ctx['dtc_codes'] else 'detected fault'}",
    )

    if ctx["dtc_codes"]:
        st.markdown(
            badge(f"Suggested DTCs: {' · '.join(ctx['dtc_codes'])}", "warning"),
            unsafe_allow_html=True,
        )

    if ctx["recall_count"] > 0:
        st.markdown("**Active Recalls:**")
        for r in ctx["recalls"]:
            subject = r.get("Subject", r.get("NHTSAActionNumber", "Unknown"))
            component = r.get("Component", "")
            st.markdown(
                f'<div class="recall-item">⚠️ <b>{subject}</b><br>'
                f'<span style="color:#94a3b8">{component}</span></div>',
                unsafe_allow_html=True,
            )
    elif ctx["total_complaints"] == 0:
        st.info("No recalls or complaints found for this vehicle. Try checking make/model spelling.")

    st.markdown(
        f'<a class="nhtsa-link" href="{ctx["nhtsa_url"]}" target="_blank">'
        f"🔗 View full NHTSA report for {year} {make} {model}</a>",
        unsafe_allow_html=True,
    )
elif not (make and model):
    st.caption("Enter make and model above to look up NHTSA recalls and complaints.")