#NO PITOP YET
import cv2
import numpy as np
import time

# --- 1. Define the HSV Range for Purple ---
# Purple is unique because it spans the "wrap-around" point (0/180) on the Hue circle.
# You typically need two ranges to capture it fully.

# Range 1: Upper end of the Hue circle (closer to blue)
lower_purple_1 = np.array([125, 50, 50])
upper_purple_1 = np.array([179, 255, 255])

# Range 2: Lower end of the Hue circle (closer to red)
# This second range is often needed for deep purples/magentas
lower_purple_2 = np.array([0, 50, 50])
upper_purple_2 = np.array([5, 255, 255])

# --- 2. Camera Setup ---
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    ret, frame = cam.read()
    if not ret:
        print("Error: Could not read frame from camera.")
        break

    # 3. Convert to HSV
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # --- 4. Create Masks ---
    # cv2.inRange checks which pixels fall within the specified HSV ranges
    mask1 = cv2.inRange(frame_hsv, lower_purple_1, upper_purple_1)
    mask2 = cv2.inRange(frame_hsv, lower_purple_2, upper_purple_2)
    full_mask = cv2.bitwise_or(mask1, mask2)

    purple_pixel_count = cv2.countNonZero(full_mask)

    # Define a threshold (e.g., 5000 pixels) for what constitutes "seeing" purple.
    # This value may need adjustment based on your resolution (640x480 or 1280x720).
    detection_threshold = 50000

    if purple_pixel_count > detection_threshold:
        print("🟣 Purple Detected! (Pixel Count:", purple_pixel_count, ")")
        time.sleep(0.5)

    # Combine the two masks using a bitwise OR operation

    # --- 5. Apply the Mask ---
    # Use the mask to extract the purple pixels from the original frame.
    # The result will only contain the pixels where the mask is white (TRUE).
    # 
    result = cv2.bitwise_and(frame, frame, mask=full_mask)

    # --- 6. Display Results ---
    cv2.imshow('Original Frame', frame)
    cv2.imshow('Purple Isolation', result) # Shows only the isolated color
    cv2.imshow('Mask (Black/White)', full_mask) # Shows the filter itself

    

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    time.sleep(0.03)  # Small delay to reduce CPU usage
# Clean up
cam.release()
cv2.destroyAllWindows()