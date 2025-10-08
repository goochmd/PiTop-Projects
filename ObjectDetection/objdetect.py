from signal import pause
import asyncio as aio
import cv2
from pitop.camera import Camera
from pitop.processing.algorithms import BallDetector
import numpy as np
import struct

cam = Camera(resolution=(640, 480))
import os


ball_detector = BallDetector()

async def process_frame(reader, writer):
    while True:
        frame = cam.get_frame()  # PIL image
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        imgGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detected_balls = ball_detector(frame, color=["red", "green", "blue"])

        red_ball = detected_balls.red
        if red_ball.found:
            print(f"Red ball center: {red_ball.center}")
            print(f"Red ball radius: {red_ball.radius}")
            print(f"Red ball angle: {red_ball.angle}")
            print()
            info = "Red Ball Found!"

        green_ball = detected_balls.green
        if green_ball.found:
            print(f"Green ball center: {green_ball.center}")
            print(f"Green ball radius: {green_ball.radius}")
            print(f"Green ball angle: {green_ball.angle}")
            print()
            info = "Green Ball Found!"

        blue_ball = detected_balls.blue
        if blue_ball.found:
            print(f"Blue ball center: {blue_ball.center}")
            print(f"Blue ball radius: {blue_ball.radius}")
            print(f"Blue ball angle: {blue_ball.angle}")
            print()
            info = "Blue Ball Found!"
        else:
            info = "No Ball Found"

        frame = detected_balls.robot_view
        cv2.putText(frame, f"{info}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        _, jpeg = cv2.imencode(".jpg", frame)
        data = jpeg.tobytes()
        header = struct.pack(">BI", 0x01, len(data))  # type=1, size
        writer.write(header + data)
        await writer.drain()
        await aio.sleep(0.033)  # ~30 FPS
async def main():
    server = await aio.start_server(process_frame, "0.0.0.0", 10000)
    print("Server started on 0.0.0.0:10000")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":  
    aio.run(main())
# This script captures frames from the camera, detects colored balls (red, green, blue),
# and sends the processed frames with detection info over a TCP socket server.
