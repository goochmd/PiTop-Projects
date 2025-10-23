import cv2
import numpy as np
import time
try:
    from pitop import Camera
except:
    pass
# YOU NEED TO SET THIS TO PROPER COLOR
color = "purple"
# YOU NEED TO SET THIS TO PROPER COLOR

# Add frame skip constant
PROCESS_EVERY_N_FRAMES = 2  # Adjust this value as needed
frame_count = 0

# Define the color ranges for purple
# Purple can be tricky as it spans across the end/beginning of the HSV hue spectrum
ranges = {
    # Two ranges for each color to account for error or lighting variations
    "red": [(0, 100, 100), (10, 255, 255), (160, 100, 100), (180, 255, 255)],
    "orange": [(10, 100, 100), (20, 255, 255), (15, 100, 100), (25, 255, 255)],
    "yellow": [(20, 100, 100), (30, 255, 255), (25, 100, 100), (35, 255, 255)],
    "green": [(40, 50, 50), (80, 255, 255), (60, 100, 100), (80, 255, 255)],
    "blue": [(100, 150, 0), (140, 255, 255), (90, 100, 100), (130, 255, 255)],
    # Improved purple/magenta ranges — covers violet → magenta spectrum and overlaps to be robust under lighting
    "purple": [(125, 50, 50), (155, 255, 255), (150, 50, 50), (170, 255, 255)]
}

# Initialize camera
try:
    cam = Camera()
except:
    cam = cv2.VideoCapture(0)

# Get the ranges for the selected color
lower1, lower2 = np.array(ranges[color][0]), np.array(ranges[color][2])
upper1, upper2 = np.array(ranges[color][1]), np.array(ranges[color][3])

# Set detection threshold (adjust as needed)
detection_threshold = 1000

while True:
    try:
        ret, frame = cam.get_frame()
    except:
        ret, frame = cam.read()
    if not ret:
        print("Error: Could not read frame from camera.")
        break

    # Only process every nth frame
    if frame_count % PROCESS_EVERY_N_FRAMES == 0:
        # Convert to HSV
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create Masks
        mask1 = cv2.inRange(frame_hsv, lower1, upper1)
        mask2 = cv2.inRange(frame_hsv, lower2, upper2)
        full_mask = cv2.bitwise_or(mask1, mask2)

        pixel_count = cv2.countNonZero(full_mask)

        if pixel_count > detection_threshold:
            print("🟣 Purple Detected! (Pixel Count:", pixel_count, ")")
            time.sleep(0.5)

        # Apply the mask and show result
        result = cv2.bitwise_and(frame, frame, mask=full_mask)
        cv2.imshow('Purple Isolation', result)

    frame_count += 1
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    time.sleep(0.03)

cam.release()
cv2.destroyAllWindows()
