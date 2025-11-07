from pitop import UltrasonicSensor, Pitop, ServoMotor, Buzzer
import asyncio as aio
from pitop.robotics import DriveController

ultrasonic = UltrasonicSensor("D3", threshold_distance=1)
drive = DriveController("M2", "M3")
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
                buzzer.blink(1, 1, 2)
                led.on()
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

asyncio.run(main())