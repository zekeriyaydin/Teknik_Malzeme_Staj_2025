import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("server_room_data.csv", parse_dates=["timestamp"])

    # Calculate Z-score for anomalies
    df["temp_zscore"] = (df["temperature_C"] - df["temperature_C"].mean()) / df["temperature_C"].std()
    df["humidity_zscore"] = (df["humidity_%"] - df["humidity_%"].mean()) / df["humidity_%"].std()
    df["anomaly"] = ((abs(df["temp_zscore"]) > 3) | (abs(df["humidity_zscore"]) > 3))

    return df


df = load_data()

# Sidebar (Filters)
st.sidebar.header("Filtreler")

# Select room
room_options = df["room_id"].unique().tolist()
selected_room = st.sidebar.selectbox("Oda Seçin", room_options)

# Date range filter
min_date, max_date = df["timestamp"].min(), df["timestamp"].max()
date_range = st.sidebar.date_input("Tarih Aralığı Seçin", [min_date, max_date], min_value=min_date, max_value=max_date)

# Filtered data
filtered_df = df[(df["room_id"] == selected_room) &
                 (df["timestamp"].dt.date >= date_range[0]) &
                 (df["timestamp"].dt.date <= date_range[1])]

# Header
st.title("Server Odası Sensör Dashboardu")

st.markdown(f"Seçilen Oda: **{selected_room}** | Tarih Aralığı: **{date_range[0]} - {date_range[1]}**")

# Temperature time series
fig_temp = px.line(filtered_df, x="timestamp", y="temperature_C",
                   title="Sıcaklık Zaman Serisi",
                   labels={"temperature_C": "Sıcaklık (°C)", "timestamp": "Zaman"})
st.plotly_chart(fig_temp, use_container_width=True)

# Humidity time series
fig_hum = px.line(filtered_df, x="timestamp", y="humidity_%",
                  title="Nem Zaman Serisi",
                  labels={"humidity_%": "Nem (%)", "timestamp": "Zaman"})
st.plotly_chart(fig_hum, use_container_width=True)

# Temperature and Dew Point comparison
fig_compare = go.Figure()
fig_compare.add_trace(go.Scatter(x=filtered_df["timestamp"], y=filtered_df["temperature_C"],
                                 mode="lines", name="Sıcaklık (°C)"))
fig_compare.add_trace(go.Scatter(x=filtered_df["timestamp"], y=filtered_df["dew_point_C"],
                                 mode="lines", name="Çiğ Noktası (°C)"))
fig_compare.update_layout(title="Sıcaklık ve Çiğ Noktası Karşılaştırması",
                          xaxis_title="Zaman", yaxis_title="°C")
st.plotly_chart(fig_compare, use_container_width=True)

# Anomaly points
anomalies = filtered_df[filtered_df["anomaly"] == True]
fig_anomaly = px.line(filtered_df, x="timestamp", y="temperature_C",
                      title="Sıcaklık Zaman Serisi ve Anomali Noktaları",
                      labels={"temperature_C": "Sıcaklık (°C)", "timestamp": "Zaman"})
fig_anomaly.add_scatter(x=anomalies["timestamp"], y=anomalies["temperature_C"],
                        mode="markers", marker=dict(color='red', size=8),
                        name="Anomali Noktası")
st.plotly_chart(fig_anomaly, use_container_width=True)

# Correlation Heatmap
corr = filtered_df[
    ["temperature_C", "humidity_%", "dew_point_C", "tn_voltage_V", "H2_ppm", "voltage_V", "frequency_Hz"]].corr()
fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r",
                     title="Sensörler Arası Korelasyon")
st.plotly_chart(fig_corr, use_container_width=True)

# Dataframe
st.subheader("Ham Veri Önizlemesi")
st.dataframe(filtered_df.head(50))

# First run ServerRoomProject.py then in terminal enter "streamlit run ServerApp.py"
