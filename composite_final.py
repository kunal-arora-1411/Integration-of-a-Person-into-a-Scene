import cv2
import numpy as np

def composite(bg_path, fg_rgba_path, shadow_path,
              scale_frac=0.6, pos=None):
    # Load
    bg = cv2.imread(bg_path)
    fg = cv2.imread(fg_rgba_path, cv2.IMREAD_UNCHANGED)
    sh = cv2.imread(shadow_path, cv2.IMREAD_GRAYSCALE)

    h_bg, w_bg = bg.shape[:2]
    h_fg, w_fg = fg.shape[:2]

    # Scale person+shadow if too tall
    max_h = int(h_bg * scale_frac)
    if h_fg > max_h:
        s = max_h / h_fg
        w_new = int(w_fg * s)
        h_new = max_h
        fg = cv2.resize(fg, (w_new, h_new), interpolation=cv2.INTER_LINEAR)
        sh = cv2.resize(sh, (w_new, h_new), interpolation=cv2.INTER_LINEAR)
        h_fg, w_fg = fg.shape[:2]

    # Determine position
    if pos is None:
        x = (w_bg - w_fg) // 2
        y = h_bg - h_fg
    else:
        x, y = pos
    x = np.clip(x, 0, w_bg - w_fg)
    y = np.clip(y, 0, h_bg - h_fg)

    # Darken background under combined shadow
    shadow_alpha = (sh.astype(np.float32) / 255.0)
    shadow_alpha = np.dstack([shadow_alpha]*3) * 0.7  # strength factor
    roi = bg[y:y+h_fg, x:x+w_fg].astype(np.float32)
    darkened = roi * (1 - shadow_alpha)

    canvas = bg.copy().astype(np.float32)
    canvas[y:y+h_fg, x:x+w_fg] = darkened

    # Alpha‐blend the person
    bgr_fg = fg[..., :3].astype(np.float32)
    alpha  = fg[..., 3:] .astype(np.float32) / 255.0
    comp_region = bgr_fg * alpha + canvas[y:y+h_fg, x:x+w_fg] * (1 - alpha)
    canvas[y:y+h_fg, x:x+w_fg] = comp_region

    return canvas.astype(np.uint8)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--bg",  required=True)
    p.add_argument("--fg",  required=True)
    p.add_argument("--sh",  required=True)
    p.add_argument("--scale", type=float, default=0.6,
                   help="Max fraction of background height")
    p.add_argument("--x", type=int, help="optional X offset")
    p.add_argument("--y", type=int, help="optional Y offset")
    p.add_argument("--out", default="final_composite.png")
    args = p.parse_args()

    pos = (args.x, args.y) if args.x is not None and args.y is not None else None
    final = composite(args.bg, args.fg, args.sh,
                      scale_frac=args.scale, pos=pos)
    cv2.imwrite(args.out, final)
    print(f"Saved final composite → {args.out}")
