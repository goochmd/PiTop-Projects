# cisos.py (Updated Client)
import cv2
import numpy as np
import asyncio
import struct
import json  # Using JSON for data transfer
from pitop import Camera

# !!! IMPORTANT: CHANGE THIS to the IP of your processing computer
PROCESSOR_HOST = "IP_OF_PROCESSOR_HERE" 
PROCESSOR_PORT = 11000

cam = Camera()

# Helper to send a single frame
async def send_frame(writer, frame):
    _, jpeg = cv2.imencode(".jpg", frame)
    data = jpeg.tobytes()
    header = struct.pack(">BI", 0x01, len(data))
    writer.write(header + data)
    await writer.drain()

# Helper to receive barrel location data
async def recv_data(reader):
    try:
        header = await reader.readexactly(5)
        msg_type, size = struct.unpack(">BI", header)
        data = await reader.readexactly(size)
        
        # Deserialize the JSON data
        locations = json.loads(data.decode("utf-8"))
        return locations
    except asyncio.IncompleteReadError:
        return None

# Task to continuously send camera frames
async def send_camera_frames(reader, writer):
    while True:
        frame = cam.get_frame()
        await send_frame(writer, frame)
        await asyncio.sleep(0.033)  # ~30 FPS

# Task to continuously receive barrel locations
async def receive_barrel_locations(reader, writer):
    while True:
        try:
            # This now receives the list of coordinates
            locations = await recv_data(reader)
            
            if locations is None:
                print("Connection closed by server")
                break
            
            if locations:
                # This is where you would "use this data for something else"
                print(f"Received barrel locations: {locations}")
            else:
                # Optional: print when no barrels are found
                # print("No barrels detected.")
                pass

        except Exception as e:
            print(f"Error receiving data: {e}")
            break

async def main():
    print(f"Connecting to {PROCESSOR_HOST}:{PROCESSOR_PORT}...")
    try:
        reader, writer = await asyncio.open_connection(PROCESSOR_HOST, PROCESSOR_PORT)
        print("Connected to cisoc.py server.")
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    await asyncio.gather(
        send_camera_frames(reader, writer),
        receive_barrel_locations(reader, writer)
    )

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nClient shutting down.")