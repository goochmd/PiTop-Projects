# ------------------------------------------------------
# Pi-Top [4] Robotics Kit - Example Integrated Script
# ------------------------------------------------------
# Features:
# 1. Drives forward using motor encoders.
# 2. Uses ultrasonic sensor to detect obstacles < 7 inches (≈ 18 cm).
#    -> Turns left if obstacle is detected.
# 3. Moves a servo motor back and forth (0° to 180°).
# 4. Uses the camera to detect red objects.
#    -> If a red object is found, snap a photo.
# 5. Runs for 60 seconds, then stops everything.
# ------------------------------------------------------

from pitop.robotics import DriveController, EncoderMotor, BrakingType, ForwardDirection, ServoMotor, UltrasonicSensor
from pitop.camera import Camera
from pitop.processing.vision import ColorDetector
import cv2
import time

# -----------------------------
# Setup Hardware
# -----------------------------

print("[DEBUG] Initializing hardware...")

# Encoders (drive motors) - left and right wheels
left_motor = EncoderMotor("M0", ForwardDirection.COUNTER_CLOCKWISE)
right_motor = EncoderMotor("M3", ForwardDirection.CLOCKWISE)
drive = DriveController(left_motor, right_motor)
left_motor.braking_type = BrakingType.COAST
right_motor.braking_type = BrakingType.COAST
print("[DEBUG] Motors initialized with COAST braking mode.")

# Ultrasonic sensor (distance detection)
ultrasonic = UltrasonicSensor("D0")   # D0 = digital port 0
print("[DEBUG] Ultrasonic sensor initialized on D0.")

# Servo motor (connected to S0)
servo = ServoMotor("S0")
print("[DEBUG] Servo motor initialized on S0.")

# Camera for object detection
camera = Camera()
color_detector = ColorDetector(hue=(0, 10))  # Hue range ~0-10 = red tones
print("[DEBUG] Camera and color detector initialized.")

# -----------------------------
# Helper Functions
# -----------------------------

def check_for_red(frame):
    """
    Checks camera frame for red object using ColorDetector.
    Returns True if red detected, else False.
    """
    mask = color_detector.create_mask(frame)
    red_pixels = cv2.countNonZero(mask)
    print(f"[DEBUG] Red pixel count: {red_pixels}")
    return red_pixels > 500  # threshold: enough red present


def sweep_servo():
    """
    Moves servo back and forth from 0° to 180°.
    """
    for angle in [0, 180]:
        print(f"[DEBUG] Moving servo to {angle}°")
        servo.target_angle = angle
        time.sleep(1)


# -----------------------------
# Main Program Loop
# -----------------------------
start_time = time.time()
stop_time = 60  # seconds

print("Starting robot program...")

with camera:
    while time.time() - start_time < stop_time:
        elapsed = round(time.time() - start_time, 2)
        print(f"\n[DEBUG] Loop time elapsed: {elapsed}s")

        # 1. Drive forward slowly
        print("[DEBUG] Driving forward at 30% speed.")
        drive.forward(0.3)  # speed (0 to 1)

        # 2. Check ultrasonic sensor (convert cm → inches)
        distance_cm = ultrasonic.distance
        distance_in = distance_cm / 2.54
        print(f"[DEBUG] Distance measured: {distance_cm:.2f} cm / {distance_in:.2f} in")

        if distance_in < 7:
            print("[DEBUG] Obstacle detected within 7 inches!")
            drive.stop()
            print("[DEBUG] Backing up slightly...")
            drive.backward(0.3)
            time.sleep(0.5)
            drive.stop()
            print("[DEBUG] Turning left...")
            drive.left(0.5)
            time.sleep(1)
            drive.stop()
            print("[DEBUG] Turn complete.")

        # 3. Servo motion (sweep back and forth)
        sweep_servo()

        # 4. Camera check for red object
        frame = camera.get_frame()
        if check_for_red(frame):
            print("[DEBUG] Red object detected! Saving photo...")
            cv2.imwrite("red_object.jpg", frame)
            print("[DEBUG] Photo saved as red_object.jpg")

    # After loop finishes
    drive.stop()
    servo.target_angle = 90  # reset to center
    print("Program finished. Motors stopped. Servo reset to center.")
