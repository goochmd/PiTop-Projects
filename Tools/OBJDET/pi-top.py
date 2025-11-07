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


async def send_frames(frame_writer, keepalive=True):
    """Continuously capture and send frames to the server."""
    try:
        while True:
            frame = np.array(cam.get_frame())
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            ok, jpeg = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            if not ok:
                await asyncio.sleep(0.03)
                continue

            data = jpeg.tobytes()
            frame_writer.write(struct.pack(">I", len(data)) + data)
            await frame_writer.drain()

            await asyncio.sleep(0.03)
    except (ConnectionResetError, asyncio.IncompleteReadError):
        print("[FRAME CLIENT] Connection lost.")
    except Exception as e:
        print(f"[FRAME CLIENT] Error: {e}")
    finally:
        if keepalive:
            try:
                frame_writer.close()
                await frame_writer.wait_closed()
            except Exception:
                pass


async def receive_detections(control_reader):
    """Receive JSON detection messages from the server."""
    try:
        while True:
            header = await control_reader.readexactly(4)
            (msg_len,) = struct.unpack(">I", header)
            payload = await control_reader.readexactly(msg_len)
            data = json.loads(payload.decode())

            if data.get("objects"):
                print("Detections from server:", data["objects"])
    except asyncio.IncompleteReadError:
        print("[CONTROL CLIENT] Server closed control connection.")
    except Exception as e:
        print(f"[CONTROL CLIENT] Error: {e}")


async def start_client(server_ip=SERVER_IP, frame_port=FRAME_PORT, control_port=CONTROL_PORT):
    """Launch both channels for use by tools.py or directly."""
    print("Connecting frame channel...")
    _, writer_f = await asyncio.open_connection(server_ip, frame_port)
    print("Connecting control channel...")
    reader_c, _ = await asyncio.open_connection(server_ip, control_port)
    print("Both channels connected. Streaming...")

    # Run both coroutines until one fails
    await asyncio.gather(
        send_frames(writer_f),
        receive_detections(reader_c)
    )


if __name__ == "__main__":
    try:
        asyncio.run(start_client())
    except KeyboardInterrupt:
        print("Stopped by user.")
