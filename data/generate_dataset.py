import pandas as pd
import numpy as np

# Generate 600 seconds of telemetry data (1Hz sampling rate)
timestamps = np.arange(0, 600, 1)
rpm = []
engine_load = []
maf = []
stft = []
ltft = []
o2_front = []
o2_rear = []

for t in timestamps:
    # Simulate a typical driving cycle: Idle -> Acceleration -> Cruise -> Decel
    if t < 120:  # Idle
        current_rpm = float(np.random.normal(750, 15))
        current_load = float(np.random.normal(15, 2))
        current_maf = float(np.random.normal(2.5, 0.2))
        # Vacuum leak signature: high positive fuel trims at idle
        current_stft = float(np.random.normal(8.0, 1.5))
        current_ltft = float(np.random.normal(12.0, 0.5))
    elif t < 240:  # Hard Acceleration
        current_rpm = float(np.linspace(750, 3500, 120)[t - 120] + np.random.normal(0, 30))
        current_load = float(np.linspace(15, 85, 120)[t - 120] + np.random.normal(0, 3))
        current_maf = float(current_rpm * 0.015 + np.random.normal(0, 1))
        # Under load, vacuum leak influence drops; trims normalize
        current_stft = float(np.random.normal(2.0, 1.0))
        current_ltft = float(np.random.normal(3.0, 0.5))
    elif t < 480:  # Highway Cruise
        current_rpm = float(np.random.normal(2400, 40))
        current_load = float(np.random.normal(45, 4))
        current_maf = float(np.random.normal(18.5, 0.8))
        current_stft = float(np.random.normal(0.5, 1.0))
        current_ltft = float(np.random.normal(1.5, 0.5))
    else:  # Return to Idle
        current_rpm = float(np.linspace(2400, 750, 120)[t - 480] + np.random.normal(0, 15))
        current_load = float(np.linspace(45, 15, 120)[t - 480] + np.random.normal(0, 2))
        current_maf = float(np.random.normal(2.5, 0.2))
        current_stft = float(np.random.normal(9.0, 1.5))
        current_ltft = float(np.random.normal(13.0, 0.5))

    # Front O2: normal upstream switching (0.1V–0.9V at ~0.5Hz) — indicates combustion quality
    front_voltage = float(0.5 + 0.4 * np.sin(t * 0.5) + np.random.normal(0, 0.04))

    # Rear O2: dampened — healthy cat keeps rear signal flat (~0.6–0.7V)
    # Slight oscillation simulates a mildly aged converter (not dead, not perfect)
    rear_voltage = float(0.65 + 0.12 * np.sin(t * 0.5 + 0.8) + np.random.normal(0, 0.025))

    rpm.append(max(0, current_rpm))
    engine_load.append(max(0, current_load))
    maf.append(max(0, current_maf))
    stft.append(current_stft)
    ltft.append(current_ltft)
    o2_front.append(max(0.05, min(0.95, front_voltage)))
    o2_rear.append(max(0.05, min(0.95, rear_voltage)))

df = pd.DataFrame({
    'Timestamp_sec': timestamps,
    'Engine_RPM': rpm,
    'Engine_Load_Pct': engine_load,
    'Mass_Air_Flow_g_s': maf,
    'Short_Term_Fuel_Trim_Pct': stft,
    'Long_Term_Fuel_Trim_Pct': ltft,
    'O2_Front_Volts': o2_front,
    'O2_Rear_Volts': o2_rear,
})

df.to_csv('data/engine_telemetry_log.csv', index=False)
print("Dataset generated: data/engine_telemetry_log.csv")
print(f"Rows: {len(df)} | Columns: {list(df.columns)}")