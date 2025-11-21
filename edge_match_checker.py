# edge_match_checker.py
import numpy as np
import cv2
from PIL import Image

class EdgeMatchChecker:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_a": ("IMAGE",),
                "image_b": ("IMAGE",),
                "tolerance_pixels": ("INT", {"default": 2, "min": 0, "max": 10, "step": 1}),
                "min_overlap_percent": ("FLOAT", {"default": 90.0, "min": 50.0, "max": 100.0, "step": 0.5}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "compare_edges"
    CATEGORY = "utils"

    def compare_edges(self, image_a, image_b, tolerance_pixels=2, min_overlap_percent=90.0):
        # Convert ComfyUI batch tensor [B,H,W,C] → numpy uint8
        img_a = (image_a[0].cpu().numpy() * 255).astype(np.uint8)
        img_b = (image_b[0].cpu().numpy() * 255).astype(np.uint8)

        # ← NEW: Force same size by resizing the smaller one to the larger one
        h_a, w_a = img_a.shape[:2]
        h_b, w_b = img_b.shape[:2]
        if (h_a, w_a) != (h_b, w_b):
            target_size = (max(w_a, w_b), max(h_a, h_b))
            img_a = cv2.resize(img_a, target_size, interpolation=cv2.INTER_NEAREST)
            img_b = cv2.resize(img_b, target_size, interpolation=cv2.INTER_NEAREST)
            print(f"[EdgeMatchChecker] Resized images to {target_size} to match dimensions")

        # To grayscale
        gray_a = cv2.cvtColor(img_a, cv2.COLOR_RGB2GRAY)
        gray_b = cv2.cvtColor(img_b, cv2.COLOR_RGB2GRAY)

        # Binarize
        _, bin_a = cv2.threshold(gray_a, 20, 255, cv2.THRESH_BINARY)
        _, bin_b = cv2.threshold(gray_b, 20, 255, cv2.THRESH_BINARY)

        # Tolerance via dilation
        if tolerance_pixels > 0:
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            bin_a = cv2.dilate(bin_a, kernel, iterations=tolerance_pixels)
            bin_b = cv2.dilate(bin_b, kernel, iterations=tolerance_pixels)

        # Now safe — sizes are guaranteed equal
        intersection = cv2.bitwise_and(bin_a, bin_b)
        inter_pixels = np.count_nonzero(intersection)

        edges_a = np.count_nonzero(bin_a)
        edges_b = np.count_nonzero(bin_b)

        if max(edges_a, edges_b) == 0:
            return ("No",)

        overlap_ratio = inter_pixels / max(edges_a, edges_b)
        result = "Yes" if overlap_ratio >= min_overlap_percent / 100.0 else "No"

        print(f"[EdgeMatchChecker] Overlap: {overlap_ratio*100:.2f}% → {result}")
        return (result,)


NODE_CLASS_MAPPINGS = {"EdgeMatchChecker": EdgeMatchChecker}
NODE_DISPLAY_NAME_MAPPINGS = {"EdgeMatchChecker": "Edge Match 90% Checker"}
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
