# pi_top_tools.py
import asyncio as aio
import cv2
import numpy as np
from typing import Optional, Tuple
import time
from CameraColorISO.cisoc import main as isomain

try:
    from pitop import Camera, ServoMotor, LED, UltrasonicSensor
    from pitop.robotics import DriveController
except Exception:
    # Lightweight fallbacks for testing on non-pi-top environments
    Camera = None
    ServoMotor = None
    LED = None
    UltrasonicSensor = None
    DriveController = None


class CameraWrap:
    """Portable camera wrapper around pi-top Camera or fallback to OpenCV."""

    def __init__(self, resolution: Tuple[int, int] = (1280, 720)):
        self.resolution = resolution
        if Camera is None:
            print("Camera class not available, using OpenCV fallback")
            self.cam = cv2.VideoCapture(0)
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        else:
            self.cam = Camera(resolution=resolution)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if hasattr(self.cam, "release"):
            self.cam.release()

    def get_frame(self) -> Optional[np.ndarray]:
        """Return a BGR frame (numpy array)."""
        if Camera is None:
            ret, frame = self.cam.read()
            if not ret:
                return None
        else:
            frame = self.cam.get_frame()
            if frame is None:
                return None
        frame = np.asarray(frame)
        if frame.ndim == 3 and frame.shape[2] == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame

    async def stream_frames(self, interval: float = 0.05):
        """Async generator yielding frames at approximately `interval` seconds."""
        while True:
            frame = self.get_frame()
            if frame is not None:
                yield frame
            await aio.sleep(interval)

    def record(
        self,
        duration: float = 5.0,
        filename: str = "output.mp4",
        codec_preferences=("mp4v", "XVID", "MJPG"),
        fps: float = 20.0,
        resize_frames: bool = True,
    ) -> None:
        """Record video to a file for `duration` seconds."""
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
        try:
            while time.time() - start_time < duration:
                frame = self.get_frame()
                if frame is None:
                    time.sleep(0.01)
                    continue

                h, w = frame.shape[:2]
                target_w, target_h = self.resolution
                if resize_frames and (w, h) != (target_w, target_h):
                    frame = cv2.resize(frame, (target_w, target_h))

                try:
                    out.write(frame)
                except Exception as e:
                    print("Failed to write frame:", e)
                    break
        except KeyboardInterrupt:
            print("Recording interrupted.")
        finally:
            out.release()


class DriveControllerWrap:
    """Wrapper around pi-top DriveController with normalized speed."""

    def __init__(self, left_motor_port: str = "M2", right_motor_port: str = "M3"):
        if DriveController is None:
            raise RuntimeError("DriveController not available in this environment")
        self._drive = DriveController(left_motor_port=left_motor_port, right_motor_port=right_motor_port)
        # Verify methods exist
        for method in ["forward", "backward", "stop"]:
            if not hasattr(self._drive, method):
                raise RuntimeError(f"DriveController missing expected method: {method}")

    def move(self, speed: float = .5) -> None:
        """Move the robot. Speed range [-1, 1]."""
        if speed < -1 or speed > 1:
            raise ValueError("Speed must be between -1 and 1")
        if speed > 0:
            try:
                self._drive.forward(speed)
            except Exception:
                self._drive.forward(speed)
        elif speed < 0:
            try:
                self._drive.backward(-speed)
            except Exception:
                self._drive.backward(-speed)
        else:
            self._drive.stop()

    def stop(self) -> None:
        self._drive.stop()


class PanTiltController:
    """Simple pan-tilt control via servo motors."""

    def __init__(self, pan_port: str = "S0", tilt_port: str = "S1"):
        if ServoMotor is None:
            raise RuntimeError("ServoMotor not available in this environment")
        self.pan_servo = ServoMotor(pan_port)
        self.tilt_servo = ServoMotor(tilt_port)

    def pan(self, angle: float) -> None:
        self.pan_servo.target_angle = angle

    def tilt(self, angle: float) -> None:
        self.tilt_servo.target_angle = angle

async def run_color_iso_server():
    await isomain()

if __name__ == "__main__":
    aio.run(run_color_iso_server())