import cv2
import numpy as np
import math

def estimate_direction(mask_path):
    # 1. Load hard-shadow mask (white = shadow)
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise FileNotFoundError(f"Couldn’t read '{mask_path}'")

    # 2. Extract coordinates of shadow pixels
    ys, xs = np.nonzero(mask)
    pts = np.stack([xs, ys], axis=1).astype(np.float32)
    if len(pts) < 10:
        raise ValueError("Not enough shadow pixels detected.")

    # 3. Center and compute covariance
    mean = pts.mean(axis=0)
    centered = pts - mean
    cov = np.cov(centered, rowvar=False)

    # 4. PCA: largest eigenvector = main shadow direction
    eigvals, eigvecs = np.linalg.eigh(cov)
    principal = eigvecs[:, np.argmax(eigvals)]

    # 5. Sun’s 2D direction is opposite the shadow axis
    sun_dir = -principal
    sun_dir /= np.linalg.norm(sun_dir)

    # 6. Azimuth angle (deg) in image coords (0° = right, +ccw)
    angle = math.degrees(math.atan2(sun_dir[1], sun_dir[0]))

    return sun_dir, angle

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("mask", help="hard-shadow mask PNG")
    args = p.parse_args()

    dir2d, az = estimate_direction(args.mask)
    print(f"Estimated sun direction (x, y) = ({dir2d[0]:+.3f}, {dir2d[1]:+.3f})")
    print(f"Azimuth angle (image coords) = {az:.1f}° ⟶ 0°=→, +90°=↑, +180°=←, –90°=↓")
    print("\n⚠️ This gives only the 2D (in-plane) direction.  ")
    print("To get elevation (altitude) you’d need an object height vs. its shadow length.")
