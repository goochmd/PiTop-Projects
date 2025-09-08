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
from pitop import ServoMotor, ServoMotorSetting
from pitop.robotics import DriveController
from pynput.keyboard import Key, Controller

#cv2 to show live footage, numpy to help show live footage, Asyncio to run everything all together, Time.Sleep to stop program for any breaks, sys for clean exits
import cv2, numpy as np, asyncio as aio, time, sys

# Create the drive object
drive = DriveController(left_motor_port="M2", right_motor_port="M3")

print("running :)")


#endregion

#region Variables
#Drive Controller and Motors
servo = ServoMotor("S0")
keys_held = set()  # To keep track of currently held keys

#Constant variables that don't need change, therefore don't need to be inside the Shared State

#Shared State (using a dictionary for easy access between async functions)
state = {
    "servo_angle" : 0,
    "running" : True
}

#endregion

#Region Keyboard Handling

#region Keyboard Task (using pi-top KeyboardButton events)

async def keyboard_task():
    """
    Asyncio-compatible task that listens for pi-top KeyboardButton events
    and updates the shared `keys_held` set accordingly.
    """
    watched_keys = ["w", "a", "s", "d", "j", "l", "c", "escape"]

    while state["running"]:
        for key in watched_keys:
            button = KeyboardButton(key)

            if button.is_pressed:
                keys_held.add(key)
            else:
                keys_held.discard(key)

        print(f"Keys held: {keys_held}")
        await aio.sleep(0.05)

#endregion


#region Variable Setting
async def variable_setter():
    while state["running"]:
        if "w" in keys_held:
            drive.forward(1)  # 80% of max speed
        elif "s" in keys_held:
            drive.backward(1)
        elif "a" in keys_held:
            drive.rotate(0.2)  # rotate left in place
        elif "d" in keys_held:
            drive.rotate(-0.2)  # rotate right in place
        else:
            drive.stop()

        # Servo control
        if 'left' in keys_held:
            state["servo_angle"] = max(-90, state["servo_angle"] - 5)
        elif 'right' in keys_held:
            state["servo_angle"] = min(90, state["servo_angle"] + 5)

        # Exit program
        if 'escape' in keys_held:
            state["running"] = False
            loop = aio.get_event_loop()
            loop.call_later(1, sys.exit, 0)

        await aio.sleep(0.1)  # keep looping


#endregion

#region Servo Control

async def servo_controller():
    """
    Controls the servo motor based on the shared state.
    """
    while state["running"]:
        servo.target_angle = state['servo_angle']
        await aio.sleep(0.1)  # Small delay to prevent busy waiting

#endregion

#region Main

async def main():

    await aio.gather(
        variable_setter(),
        servo_controller(),
        keyboard_task(),
    )

if __name__ == "__main__":
    aio.run(main())
#endregion