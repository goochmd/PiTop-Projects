from pitop import UltrasonicSensor, Pitop, ServoMotor, Buzzer
import asyncio as aio
from pitop.robotics import DriveController

ultrasonic = UltrasonicSensor("D3", threshold_distance=1)
drive = DriveController("M2", "M3")
panservo = ServoMotor("S0")
buzzer = Buzzer("D2")
panservo.target_angle = 0
miniscreen = Pitop().miniscreen
global msgchin, msgchout
msgchin = False
msgchout = False

async def main():
    while True:
        if ultrasonic.in_range():
            msgchout = False
            info = "Obstacle Detected! Stopping."
            if not msgchin:
                buzzer.blink(0.1, 0.1, 5)
                print(info)
                miniscreen.display_multiline_text(info, font_size=14)
                msgchin = True
            drive.stop()
            drive.rotate(angle=90)
        else:
            msgchin = False
            info = "Path Clear. Moving Forward."
            if not msgchout:
                print(info)
                miniscreen.display_multiline_text(info, font_size=14)
                msgchout = True
            drive.forward(50)

