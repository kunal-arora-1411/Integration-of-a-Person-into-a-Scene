# Seamless Integration of a Person into a Scene

A project that implements a photorealistic method to place a person into any scene using accurate lighting estimation, relighting, shadow generation, and seamless blending.

---

## 🎯 Objective

To develop an automated pipeline that takes a person image and a background scene and composites them such that the result appears realistic in terms of:

- Lighting & shadows  
- Color consistency  
- Natural edge blending  

---

## 📌 Features

- ✂️ Background removal using AI (`rembg`)
- ☀️ PCA-based outdoor light direction estimation
- 🎨 Reinhard color harmonization
- 💡 Gradient-based relighting
- 🪞 Hard + Soft shadow generation
- 🖌️ Weighted shadow blending
- 🧩 Seamless Poisson cloning

---

## 🛠 Tools Used

- **Python** (OpenCV, NumPy, rembg)
- **Principal Component Analysis (PCA)** for light direction
- **Reinhard Transfer** for color matching
- **cv2.seamlessClone** for Poisson blending

---

## 📁 Folder Structure

```
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
```

---

## 🧠 Algorithm Steps

### Task 1: Person Image Preparation

- Captured front-facing image in good lighting.
- Removed background using `rembg`, saved RGBA + mask.

### Task 2: Shadow Analysis

- Converted BG image to Lab space.
- Detected shadows using blurred luminance subtraction.
- Generated binary masks:
  - `shadow_hard`: Sharp shadows
  - `shadow_soft`: Diffused soft shadows

### Task 3: Light Direction Estimation

- Used PCA on `shadow_hard` to estimate sunlight direction.

### Task 4: Harmonization & Shadow Synthesis

- Harmonized colors using Reinhard Transfer.
- Relit person image using directional dot-product shading.
- Generated:
  - Hard shadows via projection + directional blur
  - Soft shadows via AO rings + isotropic blur
- Blended shadow: `0.7 * hard + 0.5 * soft`

### Task 5: Final Compositing

- Positioned and scaled the person.
- Darkened background under shadow area.
- Merged everything using `cv2.seamlessClone`.

---

## 🚀 How to Run


### 1. Prepare the person cutout and mask

```bash
python prepare_person.py person.jpg 
```

### 2. Generate hard & soft shadow masks from the background

```bash
python shadow_detect.py background.jpg 
```

### 3. Estimate the sun (light) direction from the hard shadow mask

```bash
python estimate_light_direction.py shadow_hard.png
```


### 4. Harmonize and Relight the Person

```bash
python harmonize_relight.py \
  --fg_rgba person_rgba.png \
  --fg_mask person_mask.png \
  --bg background.jpg \
  --sun <Lx> <Ly> \
  --key 0.9 \
  --fill 0.3 \
  --out person_harmonized.png
```

### 5. Generate Shadow

```bash
python make_shadow.py person_mask.png \
  --sun <Lx> <Ly> \
  --out person_shadow_combined.png
```

### 6. Composite Final Output

```bash
python composite_final.py \
  --bg background.jpg \
  --fg person_harmonized.png \
  --sh person_shadow_combined.png \
  --scale 0.6 \
  --out final_composite.png
```

---

## 🖼️ Result

- ✅ Accurate directional shadows
- ✅ Color-matched person to environment
- ✅ Seamless edge integration into the background

---

## 👤 Author

**Kunal Arora**  
B.Tech CSE AIML @ UPES  
SAP ID: 500107730  
Roll: R2142221018
