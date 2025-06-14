import cv2
import numpy as np
def make_shadow(mask, sun_dir,
                length_frac=0.8,
                blur_frac=0.03,
                strength=0.7,
                soft_strength=0.5,
                contact_ksize=51):
    h, w = mask.shape
    sun = sun_dir / np.linalg.norm(sun_dir)

    # 1) Project silhouette
    dx, dy = sun * (h * length_frac)
    M = np.array([[1,0,dx],[0,1,dy]],np.float32)
    hard = cv2.warpAffine(mask, M, (w, h), flags=cv2.INTER_LINEAR)

    # 2) Anisotropic blur (ensure odd ksize)
    base = max(1, int(h * blur_frac))
    kx = max(1, int(base * abs(sun[0])))
    ky = max(1, int(base * abs(sun[1])))
    if kx % 2 == 0: kx += 1
    if ky % 2 == 0: ky += 1
    hard = cv2.GaussianBlur(hard, (kx, 1), 0)
    hard = cv2.GaussianBlur(hard, (1, ky), 0)
    hard_f = (hard.astype(np.float32)/255.0) * strength

    # … rest of the code unchanged …

    # 2) Soft AO ring: erode + heavy blur
    kern = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (contact_ksize, contact_ksize))
    soft = cv2.erode(mask, kern, iterations=2)
    soft = cv2.GaussianBlur(soft, (contact_ksize*2+1, contact_ksize*2+1), 0)
    soft_f = (soft.astype(np.float32) / 255.0) * soft_strength

    # 3) Combine & clamp
    combined = np.clip(hard_f + soft_f, 0.0, 1.0)
    return (combined * 255).astype(np.uint8)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("mask", help="person_mask.png (binary)")
    p.add_argument("--sun", nargs=2, type=float, required=True,
                   help="Sun direction Lx Ly")
    p.add_argument("--out", default="person_shadow_combined.png")
    args = p.parse_args()

    mask = cv2.imread(args.mask, cv2.IMREAD_GRAYSCALE)
    sun  = np.array(args.sun, dtype=np.float32)

    shadow = make_shadow(mask, sun,
                         length_frac=0.8,
                         blur_frac=0.03,
                         strength=0.7,
                         soft_strength=0.5,
                         contact_ksize=51)
    cv2.imwrite(args.out, shadow)
    print(f"Saved combined shadow → {args.out}")
