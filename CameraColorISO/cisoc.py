# cisoc.py (Refactored Server)
import cv2
import numpy as np
import asyncio
import struct
import json  # Using JSON for data transfer

# Listen on all network interfaces
PROCESSOR_HOST = "0.0.0.0"
PROCESSOR_PORT = 11000

# --- Color Detection Settings ---
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
# --- End Settings ---


# Helper to receive a single frame from the client
async def recv_frame(reader):
    try:
        header = await reader.readexactly(5)
        msg_type, size = struct.unpack(">BI", header)
        data = await reader.readexactly(size)
        frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        return frame
    except asyncio.IncompleteReadError:
        return None

# Helper to send location data back to the client
async def send_data(writer, data):
    # Serialize data using JSON
    json_data = json.dumps(data).encode("utf-8")
    
    # Use the same 5-byte header protocol
    header = struct.pack(">BI", 0x02, len(json_data))
    writer.write(header + json_data)
    await writer.drain()

# This is your core processing logic
def process_frame(frame):
    """
    Processes a frame to find purple objects and returns their locations.
    Returns: A list of tuples, e.g., [(x1, y1, w1, h1), (x2, y2, w2, h2)]
    """
    barrel_locations = []
    
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(frame_hsv, lower1, upper1)
    mask2 = cv2.inRange(frame_hsv, lower2, upper2)
    full_mask = cv2.bitwise_or(mask1, mask2)

    contours, _ = cv2.findContours(full_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > detection_threshold:
            x, y, w, h = cv2.boundingRect(cnt)
            barrel_locations.append((x, y, w, h))
            
    return barrel_locations

# This function runs for each client that connects
async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Client connected: {addr}")

    while True:
        # 1. Receive a frame from the client
        frame = await recv_frame(reader)
        if frame is None:
            print("Client disconnected.")
            break

        # 2. Process the frame to find barrels
        locations = process_frame(frame)
        for (x, y, w, h) in locations:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imshow("Server View", frame)
        
        if locations:
            print(f"Found {len(locations)} barrels. Sending locations...")
        
        # 3. Send the location data back
        await send_data(writer, locations)

async def main():
    server = await asyncio.start_server(
        handle_client, PROCESSOR_HOST, PROCESSOR_PORT
    )

    addr = server.sockets[0].getsockname()
    print(f"Serving on {addr}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer shutting down.")