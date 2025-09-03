"""
This is meant to be a simple starter program using pi-top,
along with time, numpy, asyncio, cv2, and sys, to have basic control
over the robot using keybinds on a remote system.

Basic Idea:
Use asyncio to run functions all at once, make a function
to check for keyboard inputs, use encoder motors for 
movement (increase speed on one wheel for turning), use
servo motor to control angle of camera, and use c for a
picture and. If possible, put camera 
up on the main screen for easy live view.

Basic Controls:
Movement - WASD
Camera - Left and Right Arrow Keys
Take Picture - C
Exit Program- Escape

I use Regions to easily organize my code in Visual Studio Code,
so if you use anything else, dont think im crazy.
"""

#region Imports
"""Remove comments below before testing on pi-top"""
from pitop import DriveController, EncoderMotor, BrakingType, ForwardDirection, ServoMotor, UltrasonicSensor, ServoMotorSetting, Camera, KeyboardButton

#cv2 to show live footage, numpy to help show live footage, Asyncio to run everything all together, Time.Sleep to stop program for any breaks, sys for clean exits
import cv2, numpy as np, asyncio as aio, time, sys
from sshkeyboard import listen_keyboard

print("running")


#endregion

#region Variables

#Pi-Top Variables (Uncomment the variables before testing with pitop)
lm_motor = EncoderMotor("M2", ForwardDirection.CLOCKWISE)
rm_motor = EncoderMotor("M3", ForwardDirection.COUNTER_CLOCKWISE)
cam = Camera()
camera_servo = ServoMotor("S0")
keys_held = set()  # To keep track of currently held keys

#Constant variables that don't need change, therefore don't need to be inside the Shared State
motorpower = .8
turnpower = 1.25
slowrate = .1
speedrate = .01

#Shared State (using a dictionary for easy access between async functions)
state = {
    "lm_speed" : 0.0,
    "rm_speed" : 0.0,
    "servo_angle" : 90,
    "take_picture" : False,
    "running" : True
}

#endregion

#Region Keyboard Handling

def keyboard_listener(button, event_type):
    if event_type == "press":
        keys_held.add(button)
    elif event_type == "release":
        keys_held.discard(button)

#region Variable Setting
async def variable_setter():
    while state["running"]:
        if ('w' not in keys_held and 's' not in keys_held) or ('w' in keys_held and 's' in keys_held):
            state["lm_speed"] = max(0, state["lm_speed"] - slowrate) if state["lm_speed"] > 0 else min(0, state["lm_speed"] + slowrate)
            state["rm_speed"] = max(0, state["rm_speed"] - slowrate) if state["rm_speed"] > 0 else min(0, state["rm_speed"] + slowrate)
        elif 'w' in keys_held:
            state["lm_speed"] = min(motorpower, state["lm_speed"] + speedrate)
            state["rm_speed"] = min(motorpower, state["rm_speed"] + speedrate)
        elif 's' in keys_held:
            state["lm_speed"] = max(-motorpower, state["lm_speed"] - speedrate)
            state["rm_speed"] = max(-motorpower, state["rm_speed"] - speedrate)
        elif 'a' in keys_held:
            if state["lm_speed"] > 0 and state["rm_speed"] > 0:
                state["lm_speed"] = state["lm_speed"] * turnpower
            elif state["lm_speed"] < 0 and state["rm_speed"] < 0:
                state["rm_speed"] = state["lm_speed"] * turnpower
        elif 'd' in keys_held:
            if state["lm_speed"] > 0 and state["rm_speed"] > 0:
                state["rm_speed"] = state["rm_speed"] * turnpower
            elif state["lm_speed"] < 0 and state["rm_speed"] < 0:
                state["lm_speed"] = state["rm_speed"] * turnpower

        # Servo control
        if 'left' in keys_held:
            state["servo_angle"] = max(0, state["servo_angle"] - 5)
        elif 'right' in keys_held:
            state["servo_angle"] = min(180, state["servo_angle"] + 5)

        # Take picture
        if 'c' in keys_held:
            state["take_picture"] = True

        # Exit program
        if 'escape' in keys_held:
            state["running"] = False
            loop = aio.get_event_loop()
            loop.call_later(1, sys.exit, 0)

        await aio.sleep(0.1)  # keep looping


#endregion

#region Motor Control

async def motor_controller():
    """
    Controls the motors based on the shared state.
    """
    while state["running"]:
        lm_motor.set_power(state["lm_speed"])
        rm_motor.set_power(state["rm_speed"])
        await aio.sleep(0.1)  # Small delay to prevent busy waiting

#endregion

#region Servo Control

async def servo_controller():
    """
    Controls the servo motor based on the shared state.
    """
    while state["running"]:
        camera_servo.angle = state["servo_angle"]
        await aio.sleep(0.1)  # Small delay to prevent busy waiting


servo_settings = ServoMotorSetting()
servo_settings.speed = 25

#endregion

#region Camera
async def camera_controller():
    """
    Controls the camera based on the shared state.
    """
    while state["running"]:
        if state["take_picture"]:
            cam.capture("Pictures/image.jpg")
            state["take_picture"] = False
        await aio.sleep(0.1)  # Small delay to prevent busy waiting

#endregion

#region Main

async def main():
    aio.create_task(aio.to_thread(listen_keyboard, on_press=lambda key: keyboard_listener(key, event_type="press"), on_release=lambda key: keyboard_listener(key, event_type="release")))
    await aio.gather(
        variable_setter(),
        motor_controller(),
        servo_controller(),
        camera_controller(),
    )

if __name__ == "__main__":
    aio.run(main())
#endregion