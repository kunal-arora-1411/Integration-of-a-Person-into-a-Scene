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
                    st.error(f"❌ Failed to parse sun direction.
{e}")
            else:
                if os.path.exists(shadow_path) and os.path.getsize(shadow_path) > 0:
                    st.image(shadow_path, caption="Detected Hard Shadows")
                st.warning("⚠️ Sun direction not found. Using default direction: (1.0, -0.2)")

        with st.spinner("Step 4: Harmonizing and relighting person..."):
            subprocess.run([
                "python", "harmonize_relight.py",
                "--fg_rgba", f"{UPLOAD_DIR}/person_rgba.png",
                "--fg_mask", f"{UPLOAD_DIR}/person_mask.png",
                "--bg", bg_path,
                "--sun", str(sun_x), str(sun_y),
                "--key", "0.9", "--fill", "0.3",
                "--out", f"{UPLOAD_DIR}/person_harmonized.png"
            ])

        with st.spinner("Step 5: Generating shadows..."):
            subprocess.run([
                "python", "make_shadow.py", f"{UPLOAD_DIR}/person_mask.png",
                "--sun", str(sun_x), str(sun_y),
                "--out", f"{UPLOAD_DIR}/person_shadow_combined.png"
            ])

        with st.spinner("Step 6: Final compositing..."):
            subprocess.run([
                "python", "composite_final.py",
                "--bg", bg_path,
                "--fg", f"{UPLOAD_DIR}/person_harmonized.png",
                "--sh", f"{UPLOAD_DIR}/person_shadow_combined.png",
                "--scale", "0.75",
                "--out", f"{UPLOAD_DIR}/final_composite.png"
            ])

        st.success("🎉 Integration Complete!")
        st.image(f"{UPLOAD_DIR}/final_composite.png", caption="Final Composite", use_column_width=True)
