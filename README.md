How to use it in your workflow
Your node chain becomes super clean:
textYour two original images
       ↓
  → Canny / Mask (green path)
       ↓
  Image Color Overlay (green) → [Green outline image]
                                   ↓
                               EdgeMatchChecker → "Yes" or "No"
                                   ↑
  Image Color Overlay (red)   ← [Red outline image]
Or even simpler: feed the raw canny/mask images directly (no need for colored overlays at all — the node ignores color).
