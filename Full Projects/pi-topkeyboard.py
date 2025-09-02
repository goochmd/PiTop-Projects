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
import cv2, numpy as np, asyncio as aio, time, sys, sshkeyboard


#endregion

#region Variables

#Pi-Top Variables (Uncomment the variables before testing with pitop)
lm_motor = EncoderMotor("M2", ForwardDirection.CLOCKWISE)
rm_motor = EncoderMotor("M3", ForwardDirection.COUNTERCLOCKWISE)
cam = Camera()
camera_servo = ServoMotor("S0")
w = KeyboardButton("W")
a = KeyboardButton("A")
s = KeyboardButton("S")
d = KeyboardButton("D")
left = KeyboardButton("left")
right = KeyboardButton("right")
c = KeyboardButton("C")
v = KeyboardButton("V")
escape = KeyboardButton("escape")

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

#region Keyboard Handling
def keyboard_listener(button, event_type):
    if event_type == "press":
        if button == "w":
            state["lm_speed"] = min(motorpower, state["lm_speed"] + speedrate)
            state["rm_speed"] = min(motorpower, state["rm_speed"] + speedrate)
        elif button == "s":
            state["lm_speed"] = max(-motorpower, state["lm_speed"] - speedrate)
        state["rm_speed"] = max(-motorpower, state["rm_speed"] - speedrate)
    elif button == "a":
        if state["lm_speed"] > 0 and state["rm_speed"] > 0:
            state["lm_speed"] = state["lm_speed"] * turnpower
        elif state["lm_speed"] < 0 and state["rm_speed"] < 0:
            state["rm_speed"] = state["lm_speed"] * turnpower
    elif button == "d":
        if state["lm_speed"] > 0 and state["rm_speed"] > 0:
            state["rm_speed"] = state["rm_speed"] * turnpower
        elif state["lm_speed"] < 0 and state["rm_speed"] < 0:
            state["lm_speed"] = state["rm_speed"] * turnpower
    elif event_type == "release":
        if button == "w" or button == "s":
            state["lm_speed"] = max(0, state["lm_speed"] - slowrate) if state["lm_speed"] > 0 else min(0, state["lm_speed"] + slowrate)
            state["rm_speed"] = max(0, state["rm_speed"] - slowrate) if state["rm_speed"] > 0 else min(0, state["rm_speed"] + slowrate)
    """
    Listens for keyboard inputs and updates the shared state accordingly.
    """


    if button == "left":
        state["servo_angle"] = max(0, state["servo_angle"] - 5)
    elif button == "right":
         state["servo_angle"] = min(180, state["servo_angle"] + 5)
    
    if button == "c":
        state["take_picture"] = True

    if button == "escape":
        state["running"] = False
        loop = aio.get_event_loop()
        loop.call_later(1, sys.exit, 0)
  # Small delay to prevent busy waiting

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


#servo_settings = ServoMotorSetting()
#servo_settings.speed = 25

#endregion

#region Camera
async def camera_controller():
    """
    Controls the camera based on the shared state.
    """
    while state["running"]:
        if state["take_picture"]:
            cam.capture("image.jpg")
            state["take_picture"] = False
        await aio.sleep(0.1)  # Small delay to prevent busy waiting

#endregion

#region Live Footage
async def live_footage():
    print("Press 'escape' to quit live feed.")

    while state["running"]:
        # Get frame as PIL Image
        frame = cam.get_frame()

        # Convert PIL -> NumPy array (OpenCV uses BGR not RGB)
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)

        # Show in a window
        cv2.imshow("pi-top Camera Feed", frame)

        await aio.sleep(0.1)  # Small delay to prevent busy waiting

#region Main

async def main():
    await aio.gather(
        motor_controller(),
        servo_controller(),
        camera_controller(),
        live_footage(),
    )
    # Start keyboard listener with a lambda to pass event type
    listen_keyboard(
        on_press=lambda key: keyboard_listener(key, event_type="press"),
        on_release=lambda key: keyboard_listener(key, event_type="release")
    )

if __name__ == "__main__":
    aio.run(main())
#endregion