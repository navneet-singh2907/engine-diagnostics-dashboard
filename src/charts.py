import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

_MIXTURE_COLORS = {"Rich": "#ef4444", "Nominal": "#22c55e", "Lean": "#f97316"}


def rpm_vs_fuel_trim_scatter(df: pd.DataFrame, load_range: tuple[float, float]) -> go.Figure:
    """
    Scatter plot of Engine RPM vs Total Fuel Trim, filtered by engine load range.
    Points colored by mixture status (Rich/Nominal/Lean).
    """
    filtered = df[
        df["Engine_Load_Pct"].between(load_range[0], load_range[1])
    ].copy()

    fig = px.scatter(
        filtered,
        x="Engine_RPM",
        y="Total_Fuel_Trim_Pct",
        color="Mixture_Status",
        color_discrete_map=_MIXTURE_COLORS,
        hover_data={
            "Engine_Load_Pct": ":.1f",
            "Short_Term_Fuel_Trim_Pct": ":.2f",
            "Long_Term_Fuel_Trim_Pct": ":.2f",
            "Timestamp_sec": ":.0f",
        },
        labels={
            "Engine_RPM": "Engine RPM",
            "Total_Fuel_Trim_Pct": "Total Fuel Trim (%)",
            "Mixture_Status": "Mixture",
        },
        title=f"RPM vs. Total Fuel Trim — Engine Load {load_range[0]:.0f}%–{load_range[1]:.0f}%",
        template="plotly_dark",
    )

    # ±10% warning band
    fig.add_hline(y=10, line_dash="dash", line_color="#fbbf24", line_width=1,
                  annotation_text="+10% threshold", annotation_position="top right")
    fig.add_hline(y=-10, line_dash="dash", line_color="#fbbf24", line_width=1,
                  annotation_text="-10% threshold", annotation_position="bottom right")
    fig.add_hline(y=0, line_color="#6b7280", line_width=1)

    fig.update_layout(
        height=420,
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def o2_waveform_chart(df: pd.DataFrame, time_range: tuple[float, float]) -> go.Figure:
    """
    Dual-line chart of front and rear O2 sensor voltages over time.
    Healthy cat = rear line stays flat while front oscillates.
    """
    sliced = df[
        df["Timestamp_sec"].between(time_range[0], time_range[1])
    ].copy()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=sliced["Timestamp_sec"],
        y=sliced["O2_Front_Volts"],
        name="Front O₂ (pre-cat)",
        line=dict(color="#38bdf8", width=1.5),
        mode="lines",
    ))

    fig.add_trace(go.Scatter(
        x=sliced["Timestamp_sec"],
        y=sliced["O2_Rear_Volts"],
        name="Rear O₂ (post-cat)",
        line=dict(color="#a78bfa", width=1.5),
        mode="lines",
    ))

    # Stoichiometric reference at 0.45V
    fig.add_hline(y=0.45, line_dash="dot", line_color="#6b7280", line_width=1,
                  annotation_text="λ=1 (0.45V)", annotation_position="top left")

    fig.update_layout(
        title="O₂ Sensor Waveform Sweeps — Catalytic Converter Health",
        xaxis_title="Time (seconds)",
        yaxis_title="Sensor Voltage (V)",
        yaxis=dict(range=[0, 1.05]),
        template="plotly_dark",
        height=380,
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig