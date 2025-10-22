import asyncio as aio, cv2, numpy as np, struct, sys
from pitop import Camera, ServoMotor, LED, UltrasonicSensor
from pitop.robotics import DriveController
import time

class Camera():
    def __init__(self, resolution=(1280, 720)):
        self.resolution = resolution
        self.cam = Camera()

    def get_frame(self):
        frame = self.cam.get_frame()  # PIL image
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)

    def record(self, duration=5, filename="output.mp4"):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(filename, fourcc, 20.0, self.resolution)

        start_time = time.time()
        while time.time() - start_time < duration:
            frame = self.get_frame()
            if frame is not None:  # Add check to ensure frame exists
            out.write(frame)

        out.release()
