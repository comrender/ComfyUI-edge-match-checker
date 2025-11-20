import numpy as np
import cv2
from aiohttp import web

class EdgeMatchChecker:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_a": ("IMAGE",),      # Green outline or mask A
                "image_b": ("IMAGE",),      # Red outline or mask B
                "tolerance_pixels": ("INT", {
                    "default": 2,
                    "min": 0,
                    "max": 10,
                    "step": 1,
                    "display": "slider"
                }),
                "min_overlap_percent": ("FLOAT", {
                    "default": 90.0,
                    "min": 50.0,
                    "max": 100.0,
                    "step": 0.5,
                    "display": "slider"
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "compare_edges"
    CATEGORY = "utils"

    def compare_edges(self, image_a, image_b, tolerance_pixels=2, min_overlap_percent=90.0):
        # Convert ComfyUI torch tensors [B,H,W,C] -> numpy [H,W,C]
        img_a = image_a[0].cpu().numpy() * 255
        img_b = image_b[0].cpu().numpy() * 255
        img_a = img_a.astype(np.uint8)
        img_b = img_b.astype(np.uint8)

        # To grayscale
        gray_a = cv2.cvtColor(img_a, cv2.COLOR_RGB2GRAY)
        gray_b = cv2.cvtColor(img_b, cv2.COLOR_RGB2GRAY)

        # Binarize (anything > 20 is edge)
        _, bin_a = cv2.threshold(gray_a, 20, 255, cv2.THRESH_BINARY)
        _, bin_b = cv2.threshold(gray_b, 20, 255, cv2.THRESH_BINARY)

        # Optional morphological tolerance (very useful for 1-2 pixel shifts)
        if tolerance_pixels > 0:
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            bin_a = cv2.dilate(bin_a, kernel, iterations=tolerance_pixels)
            bin_b = cv2.dilate(bin_b, kernel, iterations=tolerance_pixels)

        # Compute intersection over the larger edge set
        intersection = cv2.bitwise_and(bin_a, bin_b)
        inter_pixels = np.sum(intersection > 0)

        edges_a = np.sum(bin_a > 0)
        edges_b = np.sum(bin_b > 0)

        if max(edges_a, edges_b) == 0:
            return ("No",)

        overlap_ratio = inter_pixels / max(edges_a, edges_b)
        threshold = min_overlap_percent / 100.0

        result = "Yes" if overlap_ratio >= threshold else "No"
        
        # Optional: print debug info in console
        print(f"[EdgeMatchChecker] Overlap: {overlap_ratio*100:.2f}% → {result}")

        return (result,)


NODE_CLASS_MAPPINGS = {
    "EdgeMatchChecker": EdgeMatchChecker
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EdgeMatchChecker": "Edge Match 90% Checker"
}