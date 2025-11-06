import asyncio
import struct
import cv2
import numpy as np

HOST = "0.0.0.0"
PORT = 11000

async def handle_client(reader, writer):
    print("Client connected.")
    try:
        while True:
            # Read 4-byte length prefix
            header = await reader.readexactly(4)
            (size,) = struct.unpack(">I", header)

            # Read JPEG frame
            data = await reader.readexactly(size)
            frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)

            if frame is not None:
                cv2.imshow("Camera Stream", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    except asyncio.IncompleteReadError:
        print("Client disconnected.")
    finally:
        writer.close()
        await writer.wait_closed()
        cv2.destroyAllWindows()

async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    print(f"Listening on {HOST}:{PORT}")
    async with server:
        await server.serve_forever()

asyncio.run(main())
