import pandas as pd
from pathlib import Path

REQUIRED_COLUMNS = {
    "Timestamp_sec": "float64",
    "Engine_RPM": "float64",
    "Engine_Load_Pct": "float64",
    "Mass_Air_Flow_g_s": "float64",
    "Short_Term_Fuel_Trim_Pct": "float64",
    "Long_Term_Fuel_Trim_Pct": "float64",
    "O2_Front_Volts": "float64",
    "O2_Rear_Volts": "float64",
}


def load_telemetry(path: str | Path) -> pd.DataFrame:
    """Load and validate an OBD2 telemetry CSV. Raises ValueError on schema mismatch."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Telemetry file not found: {path}")

    df = pd.read_csv(path)

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")

    for col, dtype in REQUIRED_COLUMNS.items():
        df[col] = pd.to_numeric(df[col], errors="coerce").astype(dtype)

    null_counts = df[list(REQUIRED_COLUMNS)].isnull().sum()
    if null_counts.any():
        bad = null_counts[null_counts > 0].to_dict()
        raise ValueError(f"Non-numeric values found after coercion: {bad}")

    return df.reset_index(drop=True)