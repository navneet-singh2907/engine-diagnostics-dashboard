import numpy as np
import pandas as pd


def add_total_fuel_trim(df: pd.DataFrame) -> pd.DataFrame:
    """Add Total_Fuel_Trim_Pct column (STFT + LTFT) to the dataframe."""
    df = df.copy()
    df["Total_Fuel_Trim_Pct"] = (
        df["Short_Term_Fuel_Trim_Pct"] + df["Long_Term_Fuel_Trim_Pct"]
    )
    return df


def classify_mixture(df: pd.DataFrame) -> pd.DataFrame:
    """Add Mixture_Status column: 'Rich', 'Lean', or 'Nominal' based on total fuel trim."""
    df = df.copy()
    conditions = [
        df["Total_Fuel_Trim_Pct"] > 5,
        df["Total_Fuel_Trim_Pct"] < -5,
    ]
    choices = ["Lean", "Rich"]
    df["Mixture_Status"] = np.select(conditions, choices, default="Nominal")
    return df


def apply_all(df: pd.DataFrame) -> pd.DataFrame:
    df = add_total_fuel_trim(df)
    df = classify_mixture(df)
    return df