# cartoonify_cli.py
import cv2
import numpy as np
import imageio
import matplotlib
matplotlib.use('Agg')      # headless backend (no display)
import matplotlib.pyplot as plt
import os
import sys
import argparse

def cartoonify_image(image_path, out_dir):
    # read the image
    original = cv2.imread(image_path)
    if original is None:
        print(f"ERROR: cannot read image: {image_path}")
        sys.exit(2)

    original = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
    ReSized1 = cv2.resize(original, (960, 540))

    # grayscale + smoothing
    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    smoothGrayScale = cv2.medianBlur(gray, 5)

    # edges
    edges = cv2.adaptiveThreshold(smoothGrayScale, 255,
                                  cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 9)

    # bilateral filter for color
    color = cv2.bilateralFilter(original, 9, 300, 300)

    # mask edges with color
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    ReSized6 = cv2.resize(cartoon, (960, 540))

    # save result
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(image_path))[0]
    out_path = os.path.join(out_dir, f"{base}_cartoonified.png")
    cv2.imwrite(out_path, cv2.cvtColor(ReSized6, cv2.COLOR_RGB2BGR))
    print(f"Saved cartoon image: {out_path}")

    # optional: save a combined preview image (grid) for easier CI viewing
    images = [ReSized1, cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB),
              cv2.cvtColor(smoothGrayScale, cv2.COLOR_GRAY2RGB),
              cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB),
              ReSized6, ReSized6]
    fig, axes = plt.subplots(3, 2, figsize=(8, 8), subplot_kw={'xticks':[], 'yticks':[]})
    for i, ax in enumerate(axes.flat):
        ax.imshow(images[i])
    preview_path = os.path.join(out_dir, f"{base}_preview.png")
    fig.savefig(preview_path, bbox_inches='tight')
    print(f"Saved preview image: {preview_path}")
    plt.close(fig)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cartoonify an image (CLI)")
    parser.add_argument("--input", "-i", default="input/sample.jpg", help="Input image path")
    parser.add_argument("--out", "-o", default="output", help="Output directory")
    args = parser.parse_args()
    cartoonify_image(args.input, args.out)
