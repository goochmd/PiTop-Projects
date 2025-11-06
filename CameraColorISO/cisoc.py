import asyncio
import struct
import cv2
import numpy as np
import json

HOST = "0.0.0.0"
FRAME_PORT = 11000
CONTROL_PORT = 11001

DETECTION_THRESHOLD = 500
# ROYGBV HSV ranges (OpenCV H: 0-180, S:0-255, V:0-255)
COLOR_RANGES = {
    "red": [
        np.array((0, 100, 50), dtype=np.uint8), 
        np.array((10, 255, 255), dtype=np.uint8)
    ],
    "orange": [
        np.array((11, 100, 50), dtype=np.uint8), 
        np.array((25, 255, 255), dtype=np.uint8)
    ],
    "yellow": [
        np.array((26, 100, 50), dtype=np.uint8), 
        np.array((34, 255, 255), dtype=np.uint8)
    ],
    "green": [
        np.array((35, 50, 50), dtype=np.uint8), 
        np.array((85, 255, 255), dtype=np.uint8)
    ],
    "blue": [
        np.array((86, 50, 50), dtype=np.uint8), 
        np.array((125, 255, 255), dtype=np.uint8)
    ],
    "violet": [
        np.array((125, 50, 50), dtype=np.uint8), 
        np.array((159, 255, 255), dtype=np.uint8)
    ],
}
lower, upper = COLOR_RANGES[input("Enter color to detect (red, orange, yellow, green, blue, violet): ").strip().lower()]
print(f"Detecting color range: lower={lower}, upper={upper}")
# default single-range variables used by the rest of the script (keep purple as default)

# helper to retrieve ranges for a color name (returns list of (lower, upper) pairs)
def get_hsv_ranges(color_name):
    return COLOR_RANGES.get(color_name.lower(), [(lower, upper)])

# Map client IP -> control writer (to send JSON detections)
control_writers = {}

async def handle_control_client(reader, writer):
    peer = writer.get_extra_info("peername")
    if not peer:
        writer.close()
        await writer.wait_closed()
        return
    ip = peer[0]
    print(f"[CONTROL] Connected from {ip}")
    control_writers[ip] = writer
    try:
        # Keep connection open until client disconnects
        while True:
            data = await reader.read(100)  # we don't expect incoming data; just detect disconnect
            if not data:
                break
    except asyncio.IncompleteReadError:
        pass
    finally:
        print(f"[CONTROL] Disconnected {ip}")
        control_writers.pop(ip, None)
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass

async def handle_frame_client(reader, writer):
    peer = writer.get_extra_info("peername")
    if not peer:
        writer.close()
        await writer.wait_closed()
        return
    ip = peer[0]
    print(f"[FRAME] Connected from {ip}")
    try:
        while True:
            header = await reader.readexactly(4)
            (frame_size,) = struct.unpack(">I", header)
            data = await reader.readexactly(frame_size)
            frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            if frame is None:
                print("[FRAME] Received bad frame, skipping")
                continue

            # Detect purple objects
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, lower, upper)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            obj_found = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > DETECTION_THRESHOLD:
                    x, y, w, h = cv2.boundingRect(cnt)
                    obj_found.append((int(x), int(y), int(w), int(h)))
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Send detection JSON back on control channel if available
            writer_ctrl = control_writers.get(ip)
            if writer_ctrl:
                payload = json.dumps({"objects": obj_found})
                try:
                    writer_ctrl.write(struct.pack(">I", len(payload)) + payload.encode())
                    await writer_ctrl.drain()
                except Exception as e:
                    # If send fails, remove writer (client likely disconnected)
                    print(f"[CONTROL] Failed to send to {ip}: {e}")
                    control_writers.pop(ip, None)

            # Display for debug
            cv2.imshow(f"Feed {ip}", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("User requested exit (q).")
                break

    except asyncio.IncompleteReadError:
        print(f"[FRAME] Client {ip} disconnected.")
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass
        cv2.destroyAllWindows()

async def main():
    frame_server = await asyncio.start_server(handle_frame_client, HOST, FRAME_PORT)
    control_server = await asyncio.start_server(handle_control_client, HOST, CONTROL_PORT)

    addr1 = frame_server.sockets[0].getsockname()
    addr2 = control_server.sockets[0].getsockname()
    print(f"Frame server listening on {addr1}")
    print(f"Control server listening on {addr2}")

    async with frame_server, control_server:
        await asyncio.gather(frame_server.serve_forever(), control_server.serve_forever())

if __name__ == "__main__":
    asyncio.run(main())