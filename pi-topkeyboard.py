"""
This is meant to be a simple starter program using pi-top,
along with time, keyboard, asyncio, to have basic control
over the robot using keybinds on a remote system.

Basic Idea:
Use asyncio to run functions all at once, make a function
to check for keyboard inputs, use encoder motors for 
movement (increase speed on one wheel for turning), use
servo motor to control angle of camera, and use c for a
picture and v for a video. If possible, put camera 
up on the main screen for easy live view.

Basic Controls:
Movement - WASD
Camera - Left and Right Arrow Keys
C - Take picture
V - Start/Stop Video
"""


"""Remove comment below before testing on pi-top"""
# from pitop.robotics import DriveController, EncoderMotor, BrakingType, ForwardDirection, ServoMotor, UltrasonicSensor

#Time.Sleep to stop program for any breaks.
import time.sleep as sleep

#Keyboard to register key presses for input
import keyboard as kb

#Asyncio to run everything all together
import asyncio as aio