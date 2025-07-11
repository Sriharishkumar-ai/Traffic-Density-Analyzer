# main.py 🚦 Traffic Density Analyzer (no shaking version)

import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
import tempfile
import matplotlib.pyplot as plt

# ---------------- App config ----------------
st.set_page_config(page_title="🚦 Traffic Density Analyzer", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #e0f2f1, #80deea);
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #0f172a; /* Dark navy headings for clarity */
        font-weight: 700;
        text-align: center;
    }

    p, label, .stText, .stMarkdown, .stFileUploader, span {
        color: #0f172a !important; /* Dark navy for general text readability */
        font-size: 1rem;
        text-align: center;
    }

    .stButton>button {
        background-color: #00796b;
        color: white;
        padding: 0.6em 2em;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 1rem;
    }

    .stButton>button:hover {
        background-color: #004d40;
    }

    .result-box {
        background-color: #b2dfdb;
        border: 1px solid #4db6ac;
        padding: 1em;
        border-radius: 1em;
        text-align: center;
        color: #004d40;
        font-weight: 600;
        margin-top: 1.5em;
        font-size: 1.1rem;
    }

    .centered-img {
        display: flex;
        justify-content: center;
        margin-bottom: 1em;
    }

    .uploadedFileName, .stFileUploader .uploaded-file-name {
        color: #004d40 !important;
        font-weight: 600;
        font-size: 0.95rem;
    }

      /* Fix Drag and Drop text color to white */
    section[data-testid="stFileUploader"] div div div span {
        color: white !important;
        font-weight: 600;
    }

    footer {
        color: #374151 !important;
        font-size: 0.85rem;
        text-align: center;
        margin-top: 2em;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- Title & description ----------------
st.markdown("""
    <div style='text-align:center;'>
        <img src='https://img.icons8.com/color/96/traffic-jam.png' width='60' style='margin-bottom:-10px;'/>
    </div>
    <h1>Traffic Density Analyzer</h1>
    <p>Upload a highway traffic video to detect vehicle density using YOLOv8</p>
""", unsafe_allow_html=True)

# ---------------- Video Upload ----------------
uploaded_file = st.file_uploader("📤 Upload Traffic Video (mp4)", type=["mp4"])

if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    # ---------------- Load YOLOv8 model ----------------
    model = YOLO('yolov8n.pt')  # Using nano model for speed

    # ---------------- Video Processing ----------------
    cap = cv2.VideoCapture(tfile.name)
    frame_count = 0
    vehicle_counts = []
    sample_frames = []

    st.info("🔄 Processing video frames, please wait...")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        annotated_frame = results[0].plot()
        annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

        # Filter vehicle classes
        names = results[0].names
        classes = results[0].boxes.cls.cpu().numpy()
        vehicle_class_ids = [names[c] for c in classes if names[c] in ['car', 'bus', 'truck', 'motorcycle', 'bicycle']]
        vehicle_count = len(vehicle_class_ids)
        vehicle_counts.append(vehicle_count)

        # Store every 100th frame as sample
        if frame_count % 100 == 0:
            sample_frames.append((frame_count, annotated_frame, vehicle_count))

        frame_count += 1

    cap.release()

    # ✅ Define placeholder before displaying results
    results_placeholder = st.empty()

    # ✅ Display results inside container to prevent UI shaking
    with results_placeholder.container():
        # ---------------- Results Summary ----------------
        avg_vehicles = np.mean(vehicle_counts)

        st.markdown(f"""
            <div class="metric-box">
            ✅ Processed <strong>{frame_count}</strong> frames.<br>
            🚗 Average vehicles per frame: <strong>{avg_vehicles:.2f}</strong>
            </div>
        """, unsafe_allow_html=True)

        # ---------------- Display Sample Frames ----------------
        st.subheader("🖼 Sample Processed Frames")
        for f_num, img, v_count in sample_frames:
            st.image(img, caption=f"Frame {f_num} | Vehicles: {v_count}",  use_container_width =True)

        # ---------------- Traffic Density Plot ----------------
        st.subheader("📊 Traffic Density over Frames")
        fig, ax = plt.subplots(figsize=(10,5))
        ax.plot(range(len(vehicle_counts)), vehicle_counts, color='#2563eb', linewidth=2)
        ax.set_xlabel("Frame Number")
        ax.set_ylabel("Number of Vehicles")
        ax.set_title("Traffic Density")
        ax.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig)

else:
    st.info("Please upload a traffic video to begin analysis.")

# ---------------- Footer ----------------
st.markdown("""
    <hr style="margin-top:2em;">
    <p style="text-align:center; color:#64748b;">🚀 Built with Streamlit & YOLOv8 | Designed by Sri Harish</p>
""", unsafe_allow_html=True)