import cv2
import numpy as np

def detect_shadows(bg_path, hard_out, soft_out,
                   blur_ksize=51, hard_thresh=30, soft_thresh=15):
    """
    - bg_path:      path to your background image
    - hard_out:     where to save the hard-shadow mask
    - soft_out:     where to save the soft-shadow mask
    - blur_ksize:   kernel size for Gaussian blur (must be odd, big to capture large-scale illumination)
    - hard_thresh:  minimum “shadow strength” for hard shadows
    - soft_thresh:  minimum for soft shadows (pixels between soft_thresh and hard_thresh)
    """
    # 1. Load & convert to L channel
    img = cv2.imread(bg_path)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    L = lab[:, :, 0]

    # 2. Estimate illumination by heavy blur
    illum = cv2.GaussianBlur(L, (blur_ksize, blur_ksize), 0)

    # 3. Shadow strength = illum – actual
    diff = cv2.subtract(illum, L)

    # 4. Threshold into hard & soft
    _, hard = cv2.threshold(diff, hard_thresh, 255, cv2.THRESH_BINARY)
    _, soft_temp = cv2.threshold(diff, soft_thresh, 255, cv2.THRESH_BINARY)
    soft = cv2.subtract(soft_temp, hard)

    # 5. Clean up masks
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15,15))
    hard = cv2.morphologyEx(hard, cv2.MORPH_CLOSE, kernel)
    soft = cv2.morphologyEx(soft, cv2.MORPH_CLOSE, kernel)

    # 6. Save outputs
    cv2.imwrite(hard_out, hard)
    cv2.imwrite(soft_out, soft)
    print(f"Hard shadow mask → {hard_out}\nSoft shadow mask → {soft_out}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("bg",      help="background image (e.g. background.jpg)")
    parser.add_argument("--hard",  default="shadow_hard.png",
                        help="output path for hard-shadow mask")
    parser.add_argument("--soft",  default="shadow_soft.png",
                        help="output path for soft-shadow mask")
    parser.add_argument("--blur",  type=int, default=51,
                        help="Gaussian blur kernel size (odd)")
    parser.add_argument("--hard_t", type=int, default=30,
                        help="threshold for hard shadows")
    parser.add_argument("--soft_t", type=int, default=15,
                        help="threshold for soft shadows")
    args = parser.parse_args()

    detect_shadows(args.bg, args.hard, args.soft,
                   blur_ksize=args.blur,
                   hard_thresh=args.hard_t,
                   soft_thresh=args.soft_t)
