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

I use Regions to easily organize my code in Visual Studio Code,
so if you use anything else, dont think im crazy.
"""

#region Imports
"""Remove comments below before testing on pi-top"""
# from pitop import DriveController, EncoderMotor, BrakingType, ForwardDirection, ServoMotor, UltrasonicSensor, ServoMotorSetting, Camera, KeyboardButton

#Time.Sleep to stop program for any breaks.
import time

#Asyncio to run everything all together
import asyncio as aio

#endregion

#region Variables

#Pi-Top Variables (Uncomment the variables before testing with pitop)
#lm_motor = EncoderMotor("M1")
#rm_motor = EncoderMotor("M2")
#cam = Camera()
#camera_servo = ServoMotor("S1")
#ultrasonic_sensor = UltrasonicSensor("U1")
#w = KeyboardButton("W")
#a = KeyboardButton("A")
#s = KeyboardButton("S")
#d = KeyboardButton("D")
#left = KeyboardButton("left")
#right = KeyboardButton("right")
#c = KeyboardButton("C")
#v = KeyboardButton("V")
#escape = KeyboardButton("escape")

#Constant variables that don't need change, therefore don't need to be inside the Shared State

sleep = time.sleep
motorpower = .8
turnpower = 1.25

#Shared State (using a dictionary for easy access between async functions)
state = {
    "lm_speed" : 0.0,
    "rm_speed" : 0.0,
    "servo_angle" : 90,
    "take_picture" : False,
    "record_video" : False,
}

#endregion

#region Keyboard Handling
async def keyboard_listener(button):
    if button == "W":
        state["lm_speed"] = min(motorrpm, state["lm_speed"] + 0.1)
        state["rm_speed"] = min(motorrpm, state["rm_speed"] + 0.1)
    elif button == "S":
        state["lm_speed"] = max(-motorrpm, state["lm_speed"] - 0.1)
        state["rm_speed"] = max(-motorrpm, state["rm_speed"] - 0.1)
    elif button == "A":
        if w.is_pressed and not s.is_pressed:
            state["rm_speed"] = min(1, motorrpm * turnpower)
        elif s.is_pressed and not w.is_pressed:
            state["lm_speed"] = min(1, motorrpm * turnpower)
    elif button == "D":
        if w.is_pressed and not s.is_pressed:
            state["lm_speed"] = min(1, motorrpm * turnpower)
        elif s.is_pressed and not w.is_pressed:
            state["rm_speed"] = min(1, motorrpm * turnpower)
    else:
        state["lm_speed"] = max(0, state["lm_speed"] - 0.1)
        state["rm_speed"] = max(0, state["rm_speed"] - 0.1)
    """
    Listens for keyboard inputs and updates the shared state accordingly.
    """


    if button == "LEFT":
        state["servo_angle"] = max(0, state["servo_angle"] - 5)
    elif button == "RIGHT":
         state["servo_angle"] = min(180, state["servo_angle"] + 5)
    
    if button == "C":
        state["take_picture"] = True
    if button == "V":
        state["record_video"] = not state["record_video"]

    if button == "ESCAPE":
        quit()

    await aio.sleep(0.1)  # Small delay to prevent busy waiting

#endregion

#region Motor Control

async def motor_controller():
    """
    Controls the motors based on the shared state.
    """
    while True:
        lm_motor.power = state["lm_speed"]
        rm_motor.power = state["rm_speed"]
        await aio.sleep(0.1)  # Small delay to prevent busy waiting