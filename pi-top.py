import asyncio as aio
import cv2
import numpy as np
from typing import Optional, Tuple
import time

try:
    from pitop import Camera, ServoMotor, LED, UltrasonicSensor
    from pitop.robotics import DriveController
except Exception:
    # When not running on a pi-top, provide lightweight fallbacks for testing/importing elsewhere.
    Camera = None
    ServoMotor = None
    LED = None
    UltrasonicSensor = None
    DriveController = None


class CameraWrap:
    """Portable camera wrapper around pi-top Camera.

    If the pi-top Camera isn't available this wrapper will raise on use.
    """

    def __init__(self, resolution: Tuple[int, int] = (1280, 720)):
        self.resolution = resolution
        if Camera is None:
            print("Camera class not available in this environment")
            self.cam = cv2.VideoCapture(0)
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        else:
            self.cam = Camera(resolution=resolution)

    def get_frame(self) -> Optional[np.ndarray]:
        """Return a BGR frame (numpy array) suitable for OpenCV operations.

        Returns None if a frame could not be acquired.
        """
        if Camera is None:
            ret, frame = self.cam.read()
            if not ret:
                return None
            return frame
        else:
            frame = self.cam.get_frame()
            if frame is None:
                return None
        return cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)

    def record(self, duration: float = 5.0, filename: str = "output.mp4",
               codec_preferences=("mp4v", "XVID", "MJPG"), fps: float = 20.0,
               resize_frames: bool = True) -> None:
        """Record video to a file for `duration` seconds.

        Tries multiple codecs until a VideoWriter opens. Resizes frames to the
        configured resolution if required. Does not raise on failure but prints.
        """
        out = None
        for codec in codec_preferences:
            try:
                fourcc = cv2.VideoWriter_fourcc(*codec)
                out = cv2.VideoWriter(filename, fourcc, fps, self.resolution)
                if out.isOpened():
                    print(f"Recording to {filename} using codec '{codec}'")
                    break
                out.release()
                out = None
            except Exception:
                out = None

        if out is None or not out.isOpened():
            print("Failed to open VideoWriter with codecs:", codec_preferences)
            return

        start_time = time.time()
        while time.time() - start_time < duration:
            frame = self.get_frame()
            if frame is None:
                # No frame available; wait briefly and continue to avoid busy-looping.
                time.sleep(0.01)
                continue

            # Ensure frame size matches writer expectation
            h, w = frame.shape[:2]
            target_w, target_h = self.resolution
            if resize_frames and (w, h) != (target_w, target_h):
                frame = cv2.resize(frame, (target_w, target_h))

            try:
                out.write(frame)
            except Exception as e:
                print("Failed to write frame:", e)
                break

        out.release()


class DriveWrapper:
    """Simple wrapper around the pi-top DriveController with normalized speed."""

    def __init__(self, left_motor_port: str = "M2", right_motor_port: str = "M3"):
        if DriveController is None:
            raise RuntimeError("DriveController not available in this environment")
        self._drive = DriveController(left_motor_port=left_motor_port, right_motor_port=right_motor_port)

    def move(self, speed: int = 50) -> None:
        """Move the robot. speed is in range [-100, 100]."""
        if speed < -100 or speed > 100:
            raise ValueError("Speed must be between -100 and 100")
        if speed > 0:
            # DriveController.forward expects a fraction or speed depending on implementation; try fraction first
            try:
                self._drive.forward(speed / 100.0)
            except Exception:
                self._drive.forward(speed)
        elif speed < 0:
            try:
                self._drive.backward((-speed) / 100.0)
            except Exception:
                self._drive.backward(-speed)
        else:
            self._drive.stop()

    def stop(self) -> None:
        self._drive.stop()


class PanTiltController:
    def __init__(self, pan_port: str = "S0", tilt_port: str = "S1"):
        if ServoMotor is None:
            raise RuntimeError("ServoMotor not available in this environment")
        self.pan_servo = ServoMotor(pan_port)
        self.tilt_servo = ServoMotor(tilt_port)

    def pan(self, angle: float) -> None:
        self.pan_servo.target_angle = angle

    def tilt(self, angle: float) -> None:
        self.tilt_servo.target_angle = angle

