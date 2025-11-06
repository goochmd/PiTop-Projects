# cisos.py
import cv2
import numpy as np
import asyncio
import struct
from pitop import Camera

PROCESSOR_HOST = "127.0.0.1"
PROCESSOR_PORT = 11000

cam = Camera()
color = "purple"
detection_threshold = 500

# HSV ranges for purple
ranges = {
    "purple": [(125, 50, 50), (155, 255, 255), (150, 50, 50), (170, 255, 255)]
}
lower1 = np.array(ranges[color][0], np.uint8)
upper1 = np.array(ranges[color][1], np.uint8)
lower2 = np.array(ranges[color][2], np.uint8)
upper2 = np.array(ranges[color][3], np.uint8)

# Helper to send a single frame
async def send_frame(writer, frame):
    _, jpeg = cv2.imencode(".jpg", frame)
    data = jpeg.tobytes()
    header = struct.pack(">BI", 0x01, len(data))
    writer.write(header + data)
    await writer.drain()

# Helper to receive a single frame
async def recv_frame(reader):
    header = await reader.readexactly(5)
    msg_type, size = struct.unpack(">BI", header)
    data = await reader.readexactly(size)
    frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    return frame

# Task to continuously send camera frames
async def send_camera_frames(reader, writer):
    while True:
        frame = cam.get_frame()
        await send_frame(writer, frame)
        await asyncio.sleep(0.033)  # ~30 FPS

# Task to continuously receive processed frames
async def receive_processed_frames(reader, writer):
    while True:
        try:
            frame = await recv_frame(reader)
            if frame is not None:
                # Optional: show processed frame
                cv2.imshow("Processed Frame from cisoc", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except asyncio.IncompleteReadError:
            print("Connection closed by cisoc")
            break

async def main():
    reader, writer = await asyncio.open_connection(PROCESSOR_HOST, PROCESSOR_PORT)
    print("Connected to cisoc.py")

    await asyncio.gather(
        send_camera_frames(reader, writer),
        receive_processed_frames(reader, writer)
    )

asyncio.run(main())
cv2.destroyAllWindows()
