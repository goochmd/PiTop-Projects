import asyncio
import struct
import cv2
import numpy as np
import json

HOST = "0.0.0.0"
FRAME_PORT = 11000
CONTROL_PORT = 11001

DETECTION_THRESHOLD = 500

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
            # --- LINE DETECTION ---
            # Convert to grayscale or HSV depending on your line color
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, mask = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY_INV)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5,5), np.uint8))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5,5), np.uint8))

            # Focus on the bottom region of the frame (where the line usually is)
            height, width = mask.shape
            roi = mask[int(height * 0.6):, :]  # bottom 40%

            # Find contours in the region of interest
            contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            line_center = None
            if contours:
                # Find the largest contour — likely the main line
                largest = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest)
                if area > DETECTION_THRESHOLD:
                    M = cv2.moments(largest)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"]) + int(height * 0.6)
                        line_center = (cx, cy)
                        cv2.circle(frame, line_center, 6, (0, 255, 0), -1)
                        cv2.drawContours(frame, [largest + np.array([[0, int(height * 0.6)]])], -1, (255, 0, 0), 2)

            # Compute steering error (distance from center)
            error = None
            if line_center:
                frame_center = width // 2
                error = frame_center - line_center[0]
                cv2.line(frame, (frame_center, 0), (frame_center, height), (0, 255, 255), 1)
                cv2.putText(frame, f"Error: {error}", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            writer_ctrl = control_writers.get(ip)
            if writer_ctrl:
                payload = json.dumps({
                    "line_center": line_center,
                    "error": error
                })
                try:
                    writer_ctrl.write(struct.pack(">I", len(payload)) + payload.encode())
                    await writer_ctrl.drain()
                except Exception as e:
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