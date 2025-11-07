import asyncio
import struct
import cv2
import numpy as np
import json
from pitop import Camera

SERVER_IP = "10.0.21.21" if input("Use default IP? (y/n): ") == "y" else input("Enter your PC IP: ")
FRAME_PORT = 11000
CONTROL_PORT = 11001

cam = Camera(resolution=(640, 480))

async def send_frames(frame_writer):
    try:
        frame = np.array(cam.get_frame())
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        ok, jpeg = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ok:
            await asyncio.sleep(0.03)
        data = jpeg.tobytes()
        frame_writer.write(struct.pack(">I", len(data)) + data)
        await frame_writer.drain()
        await asyncio.sleep(0.03)
        return frame
    except (ConnectionResetError, asyncio.IncompleteReadError):
        print("[FRAME CLIENT] Connection lost")
    finally:
        try:
            frame_writer.close()
            await frame_writer.wait_closed()
        except Exception:
            pass

async def receive_detections(control_reader):
    try:
        header = await control_reader.readexactly(4)
        (msg_len,) = struct.unpack(">I", header)
        payload = await control_reader.readexactly(msg_len)
        data = json.loads(payload.decode())
        if data.get("objects") != []:
            print("Detections from server:", data.get("objects", []))
            return data.get("objects", [])
    except asyncio.IncompleteReadError:
        print("[CONTROL CLIENT] Server closed control connection")
    finally:
        pass

async def main():
    print("Connecting frame channel...")
    _, writer_f = await asyncio.open_connection(SERVER_IP, FRAME_PORT)
    print("Connecting control channel...")
    reader_c, _ = await asyncio.open_connection(SERVER_IP, CONTROL_PORT)
    print("Both channels connected. Streaming...")

    # Keep writer_c alive (server expects control connection to remain open).
    # We don't send anything on it, but keeping the writer prevents server from closing.
    while True:
        await asyncio.gather(
            send_frames(writer_f),
            receive_detections(reader_c)
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped by user.")
