import cv2
import numpy as np

def lab_stats(img_lab, mask=None):
    """Compute mean & std per channel on pixels where mask>0 (or whole img if mask=None)."""
    if mask is not None:
        # only pixels inside mask
        vals = img_lab[mask>0]
    else:
        vals = img_lab.reshape(-1,3)
    mean = vals.mean(axis=0)
    std  = vals.std(axis=0)
    return mean, std

def color_harmonize(fg_bgr, fg_mask, bg_bgr):
    # Convert to Lab
    fg_lab = cv2.cvtColor(fg_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    bg_lab = cv2.cvtColor(bg_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)

    # Stats
    mean_fg, std_fg = lab_stats(fg_lab, fg_mask)
    mean_bg, std_bg = lab_stats(bg_lab, None)

    # Apply Reinhard transfer per channel
    h, w = fg_lab.shape[:2]
    out_lab = np.zeros_like(fg_lab)
    for c in range(3):
        # avoid divide by zero
        sfg = std_fg[c] if std_fg[c]>1e-6 else 1.0
        out_lab[:,:,c] = ((fg_lab[:,:,c] - mean_fg[c]) / sfg) * std_bg[c] + mean_bg[c]

    # Clip & convert back to BGR
    out_lab = np.clip(out_lab, 0, 255).astype(np.uint8)
    harmonized = cv2.cvtColor(out_lab, cv2.COLOR_LAB2BGR)
    return harmonized

def apply_relighting(fg_bgr, fg_mask, sun_dir, key=0.9, fill=0.3):
    """
    sun_dir: (Lx, Ly) unit array in image coords pointing toward the light
    key:    brightness at dot=1, fill: brightness at dot=0
    """
    h, w = fg_mask.shape
    # Prepare a grid of coords centered at object centroid
    ys, xs = np.nonzero(fg_mask)
    cy, cx = ys.mean(), xs.mean()

    # Create dot map
    Y, X = np.indices((h,w), dtype=np.float32)
    Xc = (X - cx) / (w/2)   # normalize to ±1
    Yc = (Y - cy) / (h/2)
    dots = (Xc * sun_dir[0] + Yc * sun_dir[1]).clip(-1,1)
    shade = (dots + 1) / 2  # now in [0,1]

    # map to [fill, key]
    shading = fill + (key - fill) * shade
    shading = np.stack([shading]*3, axis=-1)

    # apply only inside mask
    lit = fg_bgr.astype(np.float32) * shading
    lit = np.clip(lit, 0, 255).astype(np.uint8)
    return lit

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--fg_rgba", required=True,
                   help="RGBA PNG of your person (e.g. person_rgba.png)")
    p.add_argument("--fg_mask", required=True,
                   help="Binary mask PNG (e.g. person_mask.png)")
    p.add_argument("--bg", required=True,
                   help="Background image (e.g. background.jpg)")
    p.add_argument("--sun", nargs=2, type=float, required=True,
                   help="Sun direction (Lx Ly) from estimate_light_direction.py")
    p.add_argument("--key", type=float, default=0.9,
                   help="Key light intensity (0–1)")
    p.add_argument("--fill",type=float, default=0.3,
                   help="Fill light intensity (0–1)")
    p.add_argument("--out", default="person_harmonized.png",
                   help="Output PNG")
    args = p.parse_args()

    # Load images
    fg = cv2.imread(args.fg_rgba, cv2.IMREAD_UNCHANGED)
    bgr = fg[...,:3]
    alpha = fg[...,3]
    mask = cv2.threshold(alpha,10,255,cv2.THRESH_BINARY)[1]

    bg = cv2.imread(args.bg)

    # 1. Color-harmonize
    harmonized = color_harmonize(bgr, mask, bg)

    # 2. Relight
    sun = np.array(args.sun, dtype=np.float32)
    sun /= np.linalg.norm(sun)
    lit = apply_relighting(harmonized, mask, sun,
                           key=args.key, fill=args.fill)

    # 3. Save RGBA with updated colors & alpha
    out = cv2.cvtColor(lit, cv2.COLOR_BGR2BGRA)
    out[...,3] = alpha
    cv2.imwrite(args.out, out)
    print(f"Saved harmonized & relit person → {args.out}")
