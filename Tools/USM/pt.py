from pitop import UltrasonicSensor, Pitop, ServoMotor, Buzzer, LED
import asyncio as aio
from pitop.robotics import DriveController

ultrasonic = UltrasonicSensor("D2", threshold_distance=1)
drive = DriveController("M1", "M0")
panservo = ServoMotor("S0")
buzzer = Buzzer("D1")
led = LED("D0")
panservo.target_angle = 0
miniscreen = Pitop().miniscreen

async def main():
    msgchin = False
    msgchout = False
    while True:
        if ultrasonic.distance < 0.5:
            msgchout = False
            info = "Obstacle Detected! Stopping."
            if not msgchin:
                led.on()
                buzzer.on()
                time.sleep(0.5)
                buzzer.off()
                print(info)
                miniscreen.display_multiline_text(info, font_size=14)
                msgchin = True
            drive.stop()
            drive.rotate(angle=90)
        else:
            msgchin = False
            info = "Path Clear. Moving Forward."
            if not msgchout:
                led.off()
                print(info)
                miniscreen.display_multiline_text(info, font_size=14)
                msgchout = True
            drive.forward(50)