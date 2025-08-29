import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Magnus Formula
def calculate_dew_point(temp_c, humidity):
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + np.log(humidity/100.0)
    dew_point = (b * alpha) / (a - alpha)
    return dew_point

# Data generation
def generate_server_room_data(days=7):
    start_time = datetime.now().replace(second=0, microsecond=0)
    periods = days * 24 * 60

    timestamps = pd.date_range(start=start_time, periods=periods, freq="T")
    data = []

    for room_id in [1, 2]:
        # Basic parameters
        base_temp = 22 if room_id == 1 else 23  # Room 2 is a little warmer
        base_humidity = 50

        # Daily temperature change with sin wave
        time_index = np.arange(periods)
        daily_cycle = np.sin(2 * np.pi * time_index / (24*60))  # 1 day cycle

        temperature = base_temp + 2 * daily_cycle + np.random.normal(0, 0.5, periods)
        humidity = base_humidity + (-5 * daily_cycle) + np.random.normal(0, 2, periods)

        # Ground-Neutral Voltage (Normal 0-2V)
        tn_voltage = np.clip(np.random.normal(0.5, 0.3, periods), 0, 2)

        # H2 air quality (ppm)
        h2_quality = np.clip(np.random.normal(5, 2, periods), 0, 20)

        # Flood sensor (No anomaly)
        flood_sensor = np.zeros(periods)

        # Voltage (Around 220V)
        voltage = np.clip(np.random.normal(220, 2, periods), 215, 225)

        # Frequency (Around 50Hz)
        frequency = np.clip(np.random.normal(50, 0.05, periods), 49.8, 50.2)

        # Dew point
        dew_point = calculate_dew_point(temperature, humidity)

        # Adding temperature and humidity anomalies
        anomaly_indices = np.random.choice(periods, size=5, replace=False)  # 5 random anomaly
        for idx in anomaly_indices:
            temperature[idx] += np.random.choice([5, -5])  # sudden increase/decrease
            humidity[idx] += np.random.choice([10, -10])   # sudden increase/decrease
            humidity[idx] = np.clip(humidity[idx], 0, 100) # humidity % limit

        # Add data
        for t, temp, hum, dew, tn, h2, flood, volt, freq in zip(
            timestamps, temperature, humidity, dew_point, tn_voltage, h2_quality, flood_sensor, voltage, frequency
        ):
            data.append([t, room_id, temp, hum, dew, tn, h2, flood, volt, freq])

    # Create dataframe
    df = pd.DataFrame(data, columns=[
        "timestamp", "room_id", "temperature_C", "humidity_%",
        "dew_point_C", "tn_voltage_V", "H2_ppm", "flood_sensor",
        "voltage_V", "frequency_Hz"
    ])

    return df

# Create data and save as CSV
df = generate_server_room_data(days=7)
df.to_csv("server_room_data.csv", index=False)
print("Veri oluşturuldu ve 'server_room_data.csv' olarak kaydedildi.")
print(df.head())

# Data visualization
plt.style.use("seaborn-v0_8-whitegrid")

# Temperature time series
plt.figure(figsize=(14,5))
for room in df["room_id"].unique():
    room_data = df[df["room_id"] == room]
    plt.plot(room_data["timestamp"], room_data["temperature_C"], label=f"Oda {room}")
plt.title("Sıcaklık Zaman Serisi (2 Server Odası)")
plt.xlabel("Zaman")
plt.ylabel("Sıcaklık (°C)")
plt.legend()
plt.tight_layout()
plt.show()

# Humidity time series
plt.figure(figsize=(14,5))
for room in df["room_id"].unique():
    room_data = df[df["room_id"] == room]
    plt.plot(room_data["timestamp"], room_data["humidity_%"], label=f"Oda {room}")
plt.title("Nem Zaman Serisi")
plt.xlabel("Zaman")
plt.ylabel("Nem (%)")
plt.legend()
plt.tight_layout()
plt.show()

# Room 1: Temperature and Dew Point comparison
plt.figure(figsize=(14,5))
room_data = df[df["room_id"] == 1]
plt.plot(room_data["timestamp"], room_data["temperature_C"], label="Sıcaklık")
plt.plot(room_data["timestamp"], room_data["dew_point_C"], label="Çiğ Noktası")
plt.title("Oda 1 - Sıcaklık ve Çiğ Noktası Karşılaştırması")
plt.xlabel("Zaman")
plt.ylabel("°C")
plt.legend()
plt.tight_layout()
plt.show()

# Highlighting anomaly points
df["temp_zscore"] = (df["temperature_C"] - df["temperature_C"].mean()) / df["temperature_C"].std()
df["humidity_zscore"] = (df["humidity_%"] - df["humidity_%"].mean()) / df["humidity_%"].std()
anomalies = df[(abs(df["temp_zscore"]) > 3) | (abs(df["humidity_zscore"]) > 3)]

plt.figure(figsize=(14,5))
plt.plot(df["timestamp"], df["temperature_C"], label="Sıcaklık", color="blue")
plt.scatter(anomalies["timestamp"], anomalies["temperature_C"], color="red", label="Anomali", s=20)
plt.title("Sıcaklık Zaman Serisi ve Anomali Noktaları")
plt.xlabel("Zaman")
plt.ylabel("Sıcaklık (°C)")
plt.legend()
plt.tight_layout()
plt.show()

# Room comparison box plot
plt.figure(figsize=(8,5))
sns.boxplot(data=df, x="room_id", y="temperature_C")
plt.title("Server Odalarına Göre Sıcaklık Dağılımı")
plt.xlabel("Oda")
plt.ylabel("Sıcaklık (°C)")
plt.show()

# Correlation Heatmap
plt.figure(figsize=(8,6))
sns.heatmap(df[["temperature_C","humidity_%","dew_point_C","tn_voltage_V","H2_ppm","voltage_V","frequency_Hz"]].corr(),
            annot=True, cmap="coolwarm")
plt.title("Sensörler Arası Korelasyon")
plt.show()
