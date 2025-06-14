# prepare_person.py

import cv2
import numpy as np
from rembg import remove
from PIL import Image

def remove_background(input_path, rgba_path, mask_path):
    """
    - input_path:   original JPG/PNG of your subject
    - rgba_path:    where to save the RGBA PNG
    - mask_path:    where to save the binary mask (grayscale)
    """
    # 1. Load via PIL and remove background
    img = Image.open(input_path)
    img_rgba = remove(img)               # returns a PIL Image with alpha channel
    img_rgba.save(rgba_path)             # saves RGBA PNG

    # 2. Read back with OpenCV to split channels
    rgba = cv2.imread(rgba_path, cv2.IMREAD_UNCHANGED)
    alpha = rgba[:, :, 3]

    # 3. Refine the mask edges
    alpha_refined = cv2.GaussianBlur(alpha, (7,7), sigmaX=0)
    _, mask = cv2.threshold(alpha_refined, 10, 255, cv2.THRESH_BINARY)

    # 4. Save the final binary mask
    cv2.imwrite(mask_path, mask)
    print(f"Saved RGBA to '{rgba_path}' and mask to '{mask_path}'.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input",  help="path to input person image (JPG/PNG)")
    parser.add_argument("--out_rgba", default="person_rgba.png",
                        help="output RGBA PNG")
    parser.add_argument("--out_mask", default="person_mask.png",
                        help="output binary mask PNG")
    args = parser.parse_args()

    remove_background(args.input, args.out_rgba, args.out_mask)
