Seamless Integration of a Person into a Scene

A project that implements a photorealistic method to place a person into any scene using accurate lighting estimation, relighting, shadow generation, and seamless blending.

Objective

To develop an automated pipeline that takes a person image and a background scene and composites them such that the result appears realistic in terms of lighting, shadow behavior, color consistency, and edge integration.

📌 Features

Background removal using AI (rembg)

PCA-based outdoor light direction estimation

Reinhard color harmonization between person and scene

Gradient-based relighting of the person

Hard and soft shadow synthesis

Weighted shadow blending

Seamless compositing with Poisson blending

🛠 Tools Used

Python (OpenCV, NumPy, rembg)

Principal Component Analysis (PCA) for sun direction

Reinhard Transfer for color tone matching

cv2.seamlessClone for final blending

📁 Folder Structure

flamo_assignment/
├── images/
│   ├── person.jpg
│   ├── person_mask.png
│   ├── background.jpg
│   ├── shadow_soft.png
│   ├── shadow_hard.png
│   └── final_composite.png
├── harmonize_relight.py
├── make_shadow.py
├── composite_final.py
└── README.md

🧠 Algorithm Summary

Task 1: Person Image Preparation

Capture a front-facing image in diffuse lighting.

Remove background using rembg, saving both RGBA and binary mask.

Task 2: Shadow Analysis

Convert background to Lab space and extract shadow regions by subtracting blurred luminance.

Generate:

shadow_hard: Thresholded sharp shadows

shadow_soft: Diffuse ambient shadows

Task 3: Light Direction Estimation

Perform PCA on shadow_hard mask.

Use the primary eigenvector to estimate 2D sunlight direction.

Task 4: Harmonization and Shadow Synthesis

Color match person to background using Lab stats (Reinhard Transfer)

Relight using dot-product shading with sun vector

Generate Shadows:

Hard: project + anisotropic blur

Soft: eroded AO ring + isotropic blur

Blend both: 0.7 × hard + 0.5 × soft

Task 5: Compositing

Resize and position person and shadow

Darken BG under shadow mask

Alpha-blend person and apply Poisson blending to remove cutout edges

🚀 Usage Commands

1. Harmonize and Relight the Person

python harmonize_relight.py \
  --fg_rgba person_rgba.png \
  --fg_mask person_mask.png \
  --bg background.jpg \
  --sun 0.996 -0.084 \
  --key 0.9 --fill 0.3 \
  --out person_harmonized.png

2. Generate Shadow

python make_shadow.py person_mask.png --sun 0.996 -0.084

3. Composite Final Output

python composite_final.py \
  --bg background.jpg \
  --fg person_harmonized.png \
  --sh person_shadow_combined.png \
  --scale 0.75 \
  --out final_composite.png

🖼️ Result

A final composite image with:

Accurate shadow casting

Color and lighting matched person

Natural, seamless edge integration

👤 Author

Kunal Arora

