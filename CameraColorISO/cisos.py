import cv2
import numpy as np
import time
import asyncio as aio
import struct
from pitop import Camera
# YOU NEED TO SET THIS TO PROPER COLOR
color = "purple"
# YOU NEED TO SET THIS TO PROPER COLOR

# Add frame skip constant
PROCESS_EVERY_N_FRAMES = 2  # Adjust this value as needed

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
cam = Camera()

# Get the ranges for the selected color
lower1 = np.array(ranges[color][0], dtype=np.uint8)
lower2 = np.array(ranges[color][2], dtype=np.uint8)
upper1 = np.array(ranges[color][1], dtype=np.uint8)
upper2 = np.array(ranges[color][3], dtype=np.uint8)

# Set detection threshold (adjust as needed)
detection_threshold = 1000

async def detect_color(reader, writer):
    frame_count = 0
    while True:
        frame = cam.get_frame()
        if frame is None:
            # No valid frame this iteration
            time.sleep(0.01)
            continue
        frame = np.array(frame)
        # Only process every nth frame
        if frame_count % PROCESS_EVERY_N_FRAMES == 0:
            # Convert to HSV
            frame_hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

            # Create Masks
            mask1 = cv2.inRange(frame_hsv, lower1, upper1)
            mask2 = cv2.inRange(frame_hsv, lower2, upper2)
            full_mask = cv2.bitwise_or(mask1, mask2)

            pixel_count = cv2.countNonZero(full_mask)

            if pixel_count > detection_threshold:
                print(f"🟣 {color.capitalize()} Detected! ({pixel_count})")
                time.sleep(0.5)

            # Apply the mask and show result
            result = cv2.copyTo(frame, full_mask)
            _, jpeg = cv2.imencode(".jpg", result)
            data = jpeg.tobytes()
            header = struct.pack(">BI", 0x01, len(data))  # type=1, size
            writer.write(header + data)
            await writer.drain()
            await aio.sleep(0.033)  # ~30 FPS
            writer.close()

        frame_count += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()
async def main():
    video_server = await aio.start_server(detect_color, "0.0.0.0", 10000)
    print("Keybind server running on 9999")
    print("Video server running on 10000")
    async with video_server:
        await aio.gather(
            video_server.serve_forever(),
        )

aio.run(main())