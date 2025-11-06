# Object Detection — Color Isolation (OBJDET)

This folder contains simple color-isolation based object detection experiments and test harnesses. The goal of these scripts is to provide a lightweight alternative to heavy ML models: detect objects using color thresholds and classical image processing.

## Files
### - `cisoc.py` — primary color-isolation detection script
  - Purpose: capture frames from a camera, apply a color-space transform (commonly BGR -> HSV), threshold using color ranges, apply morphological operations to remove noise, find contours, and compute object centroids and areas. The output can be a simple (x, y) centroid and estimated object size used for navigation or pick tasks.
  - Typical flow:
    1. Initialize camera capture (OpenCV VideoCapture) and any required hardware (camera orientation, exposure).
    2. Convert each frame to HSV.
    3. Apply in-range threshold with calibrated lower/upper HSV tuples.
    4. Optional: blur to reduce noise, then morphological open/close to remove small blobs.
    5. Find contours and filter them by area or aspect ratio.
    6. Compute centroid (moments) and bounding box for the chosen contour.
    7. Publish or return centroid coordinates and size for downstream logic (motors, logging).

### - `cisos.py` — alternative/experimental color-isolation implementation
  - Purpose: a variation on `cisoc.py` that may use different heuristics (e.g., using LAB color space, performing adaptive thresholding, or different contour selection criteria). Keep it as an experimental playground for tuning detection under different lighting.

## Dependencies
- Required Python packages:
  - `opencv-python` (cv2)
  - `numpy`

## Calibration and tips
- Color spaces: HSV is commonly used for color-thresholding because hue separates color from intensity; however, LAB can be more robust under some lighting conditions.
- Lighting: consistent lighting greatly improves results. Avoid strong shadows or specular highlights on the object.
- Use interactive sliders (OpenCV trackbars) to find good HSV ranges while running `testc.py`.
- Noise reduction: applying a small Gaussian blur (e.g., kernel 5x5) and morphological opening/closing can reduce spurious detections.

## Integration
- Output from the detection scripts is simple: centroid (x, y) and an estimated size/area. Feed these values into your navigation or manipulation logic to center on objects, approach, or pick up.
- When used in a challenge script at the repo root, import the detector and call a single function that returns the current best detection; this keeps the runtime loop simple.
