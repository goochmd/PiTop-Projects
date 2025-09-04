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

#cv2 to show live footage, numpy to help show live footage, Asyncio to run everything all together, Time.Sleep to stop program for any breaks, sys for clean exits
import cv2, numpy as np, asyncio as aio, time, sys
from sshkeyboard import listen_keyboard
from drive_controller import DriveController

# Create the drive object
drive = DriveController()

print("running :)")


#endregion

#region Variables
#Drive Controller and Motors
servo = ServoMotor("S0")
keys_held = set()  # To keep track of currently held keys

#Constant variables that don't need change, therefore don't need to be inside the Shared State

#Shared State (using a dictionary for easy access between async functions)
state = {
    "servo_angle" : 90,
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
            state["servo_angle"] = max(0, state["servo_angle"] - 5)
        elif 'right' in keys_held:
            state["servo_angle"] = min(180, state["servo_angle"] + 5)

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
        servo.target_angle = state["servo_angle"]
        await aio.sleep(0.1)  # Small delay to prevent busy waiting

#endregion

#region Main

async def main():
    servo_settings = ServoMotorSetting()
    servo_settings.speed = 25
    aio.create_task(aio.to_thread(listen_keyboard, on_press=lambda key: keyboard_listener(key, event_type="press"), on_release=lambda key: keyboard_listener(key, event_type="release")))
    await aio.gather(
        variable_setter(),
        servo_controller(),
    )

if __name__ == "__main__":
    aio.run(main())
#endregion