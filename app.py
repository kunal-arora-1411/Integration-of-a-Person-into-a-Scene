import streamlit as st
import tempfile
from PIL import Image
import numpy as np
import cv2

# Import pipeline functions
from prepare_person import remove_background
from shadow_detect import detect_shadows
from estimate_light_direction import estimate_direction
from make_shadow import make_shadow
from harmonize_relight import color_harmonize, apply_relighting
from composite_final import composite

st.set_page_config(page_title="Person Integration App", layout="wide")
st.title("🤝 Person Integration Streamlit App")
st.write("Upload your person and background images, then run the full integration pipeline: background removal, shadow detection, light estimation, shadow generation, harmonization, relighting, and final compositing.")

# Sidebar parameters
st.sidebar.header("⚙️ Parameters")
# Person scaling
scale_frac = st.sidebar.slider("Max person height fraction", min_value=0.1, max_value=1.0, value=0.6)
# Shadow detection
blur_ksize = st.sidebar.slider("Shadow blur kernel size", 1, 101, 51, step=2)
hard_thresh = st.sidebar.slider("Hard shadow threshold", 0, 100, 30)
soft_thresh = st.sidebar.slider("Soft shadow threshold", 0, hard_thresh, 15)
# Shadow generation
length_frac = st.sidebar.slider("Generated shadow length fraction", 0.1, 2.0, 0.8)
blur_frac = st.sidebar.slider("Shadow anisotropic blur fraction", 0.0, 0.1, 0.03)
strength = st.sidebar.slider("Shadow strength", 0.0, 1.0, 0.7)
soft_strength = st.sidebar.slider("Soft ambient occlusion strength", 0.0, 1.0, 0.5)
contact_ksize = st.sidebar.slider("Contact kernel size (odd)", 1, 101, 51, step=2)
# Relighting
key = st.sidebar.slider("Key light intensity", 0.0, 1.0, 0.9)
fill = st.sidebar.slider("Fill light intensity", 0.0, 1.0, 0.3)
# Composite position
x_offset = st.sidebar.number_input("X offset for composite", value=0)
y_offset = st.sidebar.number_input("Y offset for composite", value=0)

# File upload
st.header("1️⃣ Upload Images")
person_file = st.file_uploader("Upload person image (JPG/PNG)", type=["png", "jpg", "jpeg"] )
bg_file = st.file_uploader("Upload background image (JPG/PNG)", type=["png", "jpg", "jpeg"] )

if person_file and bg_file:
    if st.button("▶️ Run Integration Pipeline"):
        with st.spinner("Running pipeline..."):
            # Save uploads to temp files
            person_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            person_temp.write(person_file.read())
            person_temp.flush()
            bg_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            bg_temp.write(bg_file.read())
            bg_temp.flush()

            # 2. Background removal
            rgba_path = person_temp.name.replace(".png", "_rgba.png")
            mask_path = person_temp.name.replace(".png", "_mask.png")
            remove_background(person_temp.name, rgba_path, mask_path)
            st.subheader("✅ Background Removal")
            col1, col2 = st.columns(2)
            col1.image(Image.open(rgba_path), caption="Person RGBA", use_column_width=True)
            col2.image(Image.open(mask_path), caption="Person Mask", use_column_width=True)

            # 3. Shadow detection on background
            hard_path = bg_temp.name.replace(".jpg", "_shadow_hard.png")
            soft_path = bg_temp.name.replace(".jpg", "_shadow_soft.png")
            detect_shadows(bg_temp.name, hard_path, soft_path,
                           blur_ksize=blur_ksize,
                           hard_thresh=hard_thresh,
                           soft_thresh=soft_thresh)
            st.subheader("✅ Background Shadow Detection")
            c1, c2 = st.columns(2)
            c1.image(Image.open(hard_path), caption="Hard Shadow Mask", use_column_width=True)
            c2.image(Image.open(soft_path), caption="Soft Shadow Mask", use_column_width=True)

            # 4. Light direction estimation
            sun_dir, angle = estimate_direction(hard_path)
            st.subheader("☀️ Estimated Sun Direction")
            st.write(f"Direction vector: {sun_dir}")
            st.write(f"Azimuth angle: {angle:.1f}°")

            # 5. Person shadow generation
            shadow_arr = make_shadow(
                cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE),
                sun_dir,
                length_frac=length_frac,
                blur_frac=blur_frac,
                strength=strength,
                soft_strength=soft_strength,
                contact_ksize=contact_ksize)
            shadow_path = person_temp.name.replace(".png", "_person_shadow.png")
            cv2.imwrite(shadow_path, shadow_arr)
            st.subheader("🌑 Generated Person Shadow")
            st.image(shadow_arr, caption="Person Shadow", use_column_width=True)

            # 6. Color harmonization & relighting
            # Load RGBA and split
            fg_rgba = cv2.imread(rgba_path, cv2.IMREAD_UNCHANGED)
            fg_bgr = fg_rgba[..., :3]
            fg_mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            bg_bgr = cv2.imread(bg_temp.name)
            # Harmonize
            harmonized = color_harmonize(fg_bgr, fg_mask, bg_bgr)
            # Relight
            lit = apply_relighting(harmonized, fg_mask, sun_dir, key=key, fill=fill)
            # Reapply alpha
            lit_rgba = cv2.cvtColor(lit, cv2.COLOR_BGR2BGRA)
            lit_rgba[...,3] = fg_rgba[...,3]
            lit_path = person_temp.name.replace(".png", "_lit.png")
            cv2.imwrite(lit_path, lit_rgba)
            st.subheader("🎨 Harmonized & Relit Person")
            st.image(lit_path, caption="Relit Person RGBA", use_column_width=True)

            # 7. Final compositing
            comp_img = composite(bg_temp.name, lit_path, shadow_path,
                                 scale_frac=scale_frac,
                                 pos=(int(x_offset), int(y_offset)))
            final_path = "final_composite.png"
            cv2.imwrite(final_path, comp_img)
            st.subheader("📸 Final Composite")
            st.image(final_path, caption="Composite Result", use_column_width=True)
            st.success("Pipeline complete!")
