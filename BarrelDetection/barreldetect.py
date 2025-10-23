import cv2
import numpy as np

# Adjust for your barrel color (example: orange plastic barrel)
LOWER_HSV = np.array([5, 120, 80], np.uint8)
UPPER_HSV = np.array([25, 255, 255], np.uint8)

def detect_barrels(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_HSV, UPPER_HSV)

    # Morphological cleanup (very cheap)
    mask = cv2.erode(mask, None, iterations=1)
    mask = cv2.dilate(mask, None, iterations=2)

    # Connected components instead of contours (faster)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, 8, cv2.CV_32S)

    barrels = []
    for i in range(1, num_labels):  # skip background
        x, y, w, h, area = stats[i]
        if area < 500:   # filter noise
            continue

        roi = mask[y:y+h, x:x+w]
        # Width profile at a few horizontal slices
        rows = np.linspace(0, roi.shape[0]-1, 6, dtype=int)
        widths = []
        for r in rows:
            cols = np.where(roi[r] > 0)[0]
            if len(cols) > 1:
                widths.append(cols[-1] - cols[0])
        if len(widths) < 4:
            continue

        mid = len(widths)//2
        top, midw, bottom = widths[0], widths[mid], widths[-1]

        # Check for hourglass / barrel curve
        if midw * 1.25 < top and midw * 1.25 < bottom:
            barrels.append((x, y, w, h))

    return barrels

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv2.CAP_PROP_FPS, 20)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        barrels = detect_barrels(frame)
        for (x, y, w, h) in barrels:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.imshow("Barrels", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
