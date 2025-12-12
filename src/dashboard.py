import streamlit as st
import json
import time
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

st.set_page_config(page_title="Sentry Vision Dashboard", layout="wide")

st.title("📊 Sentry Vision MVP - Analysis Dashboard")

st.markdown("**Real-time monitoring of detections, movement patterns, and performance metrics.**")

placeholder = st.empty()

while True:
    try:
        with open('data/dashboard_data.json', 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"detections": [], "fps": 0, "last_update": "N/A"}

    detections = data.get('detections', [])
    fps = data.get('fps', 0)
    last_update = data.get('last_update', 'N/A')

    # Main metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current FPS", f"{fps:.1f}")
    with col2:
        st.metric("Total Detections", len(detections))
    with col3:
        st.metric("Last Update", last_update)

    # Count by class
    if detections:
        classes = [d['class'] for d in detections]
        class_counts = Counter(classes)
        st.subheader("📈 Detection Count by Class")
        df_counts = pd.DataFrame(list(class_counts.items()), columns=['Class', 'Count'])
        st.bar_chart(df_counts.set_index('Class'))
    else:
        st.subheader("📈 Detection Count by Class")
        st.write("No detections yet.")

    # Recent detections
    st.subheader("🕒 Recent Detections")
    if detections:
        recent = detections[-10:]  # Last 10
        df_recent = pd.DataFrame(recent)
        df_recent['timestamp'] = pd.to_datetime(df_recent['timestamp'])
        st.dataframe(df_recent[['timestamp', 'class', 'confidence']].rename(columns={
            'timestamp': 'Time',
            'class': 'Class',
            'confidence': 'Confidence'
        }))
    else:
        st.write("No recent detections.")

    # Movement patterns
    st.subheader("🎯 Movement Patterns (Centroids)")
    if detections:
        centroids = [d['centroid'] for d in detections if 'centroid' in d]
        if centroids:
            x_coords = [c[0] for c in centroids]
            y_coords = [c[1] for c in centroids]
            fig, ax = plt.subplots()
            ax.scatter(x_coords, y_coords, alpha=0.6)
            ax.set_xlabel('X Position')
            ax.set_ylabel('Y Position')
            ax.set_title('Centroid Trajectory (last detections)')
            ax.invert_yaxis()  # To match image coordinates
            st.pyplot(fig)
        else:
            st.write("No centroid data.")
    else:
        st.write("No movement data.")

    time.sleep(2)  # Update every 2 seconds