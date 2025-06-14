import streamlit as st
import os
import cv2
import numpy as np
from PIL import Image
import subprocess

# Set paths
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.title("🖼️ Seamless Person Integration into a Scene")
st.write("Upload a person photo and background to blend them photorealistically.")

# Upload person and background
person_file = st.file_uploader("Upload Person Image", type=["jpg", "jpeg", "png"])
bg_file = st.file_uploader("Upload Background Image", type=["jpg", "jpeg", "png"])

if person_file and bg_file:
    person_path = os.path.join(UPLOAD_DIR, "person.jpg")
    bg_path = os.path.join(UPLOAD_DIR, "background.jpg")

    with open(person_path, "wb") as f:
        f.write(person_file.read())
    with open(bg_path, "wb") as f:
        f.write(bg_file.read())

    st.image([person_path, bg_path], caption=["Person", "Background"], width=300)

    if st.button("▶️ Start Integration Pipeline"):

        with st.spinner("Step 1: Removing background..."):
            subprocess.run([
                "python", "prepare_person.py", person_path,
                "--out_rgba", f"{UPLOAD_DIR}/person_rgba.png",
                "--out_mask", f"{UPLOAD_DIR}/person_mask.png"
            ])

        with st.spinner("Step 2: Detecting shadows in background..."):
            subprocess.run([
                "python", "shadow_detect.py", bg_path,
                "--hard", f"{UPLOAD_DIR}/shadow_hard.png",
                "--soft", f"{UPLOAD_DIR}/shadow_soft.png"
            ])

        shadow_path = f"{UPLOAD_DIR}/shadow_hard.png"
        sun_x, sun_y = 1.0, -0.2  # fallback default sun direction

        with st.spinner("Step 3: Estimating light direction..."):
            result = subprocess.run(
                ["python", "estimate_light_direction.py", shadow_path],
                capture_output=True, text=True
            )
            st.text(result.stdout)
            lines = result.stdout.splitlines()
            sun_line = next((line for line in lines if "Estimated sun direction" in line), None)

            if sun_line:
                try:
                    sun_vec = sun_line.split("=")[1].strip().replace("(", "").replace(")", "").split(",")
                    sun_x, sun_y = float(sun_vec[0]), float(sun_vec[1])
                    st.success(f"☀️ Sun direction extracted: ({sun_x:.3f}, {sun_y:.3f})")
                except Exception as e:
                    st.error(f"❌ Failed to parse sun d
