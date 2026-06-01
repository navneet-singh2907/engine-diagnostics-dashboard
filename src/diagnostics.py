import pandas as pd

FUEL_TRIM_WARNING_THRESHOLD = 10.0


def get_fuel_trim_alert(df: pd.DataFrame) -> dict:
    """
    Return the latest fuel trim reading and whether it exceeds the ±10% threshold.
    Positive breach = lean (vacuum leak / unmetered air).
    Negative breach = rich (over-fueling).
    """
    latest = df.iloc[-1]
    stft = latest["Short_Term_Fuel_Trim_Pct"]
    ltft = latest["Long_Term_Fuel_Trim_Pct"]
    total = latest["Total_Fuel_Trim_Pct"]

    breached = abs(total) > FUEL_TRIM_WARNING_THRESHOLD
    direction = "lean" if total > 0 else "rich"

    return {
        "stft": round(stft, 2),
        "ltft": round(ltft, 2),
        "total": round(total, 2),
        "breached": breached,
        "direction": direction if breached else "nominal",
        "message": (
            f"WARNING: Total fuel trim {total:+.1f}% — engine running {direction}. "
            f"Possible {'vacuum leak or unmetered air' if direction == 'lean' else 'over-fueling or injector leak'}."
            if breached
            else f"Fuel trim nominal ({total:+.1f}%)"
        ),
    }


def get_fleet_summary(df: pd.DataFrame) -> dict:
    """Aggregate fuel trim stats across the full log for dashboard KPIs."""
    total = df["Total_Fuel_Trim_Pct"]
    breach_pct = (total.abs() > FUEL_TRIM_WARNING_THRESHOLD).mean() * 100
    return {
        "mean_total_trim": round(total.mean(), 2),
        "max_total_trim": round(total.max(), 2),
        "min_total_trim": round(total.min(), 2),
        "pct_time_in_warning": round(breach_pct, 1),
    }