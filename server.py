"""Pi-Top Remote Control Server
This script sets up two servers:
1. Keybind Server: Listens for keypress events from a client and updates the robot's state.
2. Video Server: Streams video frames from the Pi-top camera to the client.
These servers are put together to allow remote control of a Pi-top robot with real-time video feedback.
Purposes for Libraries Used:
- asyncio: For asynchronous networking and handling multiple connections.
- cv2 (OpenCV): For image processing and encoding frames to JPEG.
- numpy: For efficient array manipulations, especially for image data.
- struct: For packing and unpacking binary data for network transmission.
- sys: Seamlessly exits the program when escape is pressed.
- pitop: To interface with Pi-top hardware components like Camera, ServoMotor, LED, and DriveController.
- pitop.robotics: Specifically for controlling the robot's drive system.

!!NOTE!!: This code is to ONLY be ran on the pi-top itself, and does not have any functionality on a normal computer.
This code also cannot be ran standalone, as it needs a client running the controller.py in the same directory to have proper functionality.
"""
import asyncio as aio, cv2, numpy as np, struct, sys
from pitop import Camera, ServoMotor, LED, UltrasonicSensor
from pitop.robotics import DriveController


cam = Camera(resolution=(1280, 720))
uss = UltrasonicSensor("D3", threshold_distance=1, max_distance=300)
brakelight = LED("D0")
panservo = ServoMotor("S0")
tiltservo = ServoMotor("S1")
drive = DriveController(left_motor_port="M2", right_motor_port="M3")

state = {"keys": set(), "running": True, "pan_angle": 0, "tilt_angle": 0}


# Keybind server: receives keybinds from controller
async def handle_keybinds(reader, writer):
    while state["running"]:
        line = await reader.readline()
        if not line:
            break
        msg = line.decode().strip().upper()

        # Key handling
        if msg.startswith("PRESS_"):
            key = msg[6:].lower()
            state["keys"].add(key)
        elif msg.startswith("RELEASE_"):
            key = msg[8:].lower()
            state["keys"].discard(key)
        elif msg == "EXIT":
            state["running"] = False

        # Send back confirmation
        response = f"OK {msg}".encode()
        header = struct.pack(">BI", 0x02, len(response))  # type=2
        writer.write(header + response)
        await writer.drain()

    writer.close()

# Video server: sends video frames to controller
async def handle_video(reader, writer):
    while state["running"]:
        frame = cam.get_frame()  # PIL image
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        cv2.putText(frame, f"Ultrasonic Sensor Distance: {uss.distance} m", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        _, jpeg = cv2.imencode(".jpg", frame)
        data = jpeg.tobytes()
        header = struct.pack(">BI", 0x01, len(data))  # type=1, size
        writer.write(header + data)
        await writer.drain()
        await aio.sleep(0.033)  # ~30 FPS
    writer.close()

#region Variable Setting
async def variable_setter():
    while state["running"]:
        if "w" in state["keys"]:
            drive.forward(1)  # 100% of max speed
            if brakelight.is_lit:
                brakelight.off()
        elif "s" in state["keys"]:
            drive.backward(1)
            if brakelight.is_lit:
                brakelight.off()
        elif "a" in state["keys"]:
            drive.rotate(0.2)  # rotate left in place
            if brakelight.is_lit:
                brakelight.off()
        elif "d" in state["keys"]:
            drive.rotate(-0.2)  # rotate right in place
            if not brakelight.is_lit:
                brakelight.on()
        else:
            drive.stop()
            if not brakelight.is_lit:
                brakelight.on()


        # Servo control
        if 'left' in state["keys"]:
            state["pan_angle"] = min(90, state["pan_angle"] + 10)
        elif 'right' in state["keys"]:
            state["pan_angle"] = max(-90, state["pan_angle"] - 10)
        panservo.target_angle = state['pan_angle']

        if 'up' in state["keys"]:
            state["tilt_angle"] = min(90, state["tilt_angle"] + 10)
        elif 'down' in state["keys"]:
            state["tilt_angle"] = max(-90, state["tilt_angle"] - 10)
        tiltservo.target_angle = state['tilt_angle']

        # Exit program
        if 'escape' in state["keys"]:
            state["running"] = False
            loop = aio.get_event_loop()
            loop.call_later(1, sys.exit, 0)

        await aio.sleep(0.1)  # keep looping


#endregion

#region Main

async def main():
    keybind_server = await aio.start_server(handle_keybinds, "0.0.0.0", 9999)
    video_server = await aio.start_server(handle_video, "0.0.0.0", 10000)
    print("Keybind server running on 9999")
    print("Video server running on 10000")
    async with keybind_server, video_server:
        await aio.gather(
            variable_setter(),
            keybind_server.serve_forever(),
            video_server.serve_forever(),
        )

aio.run(main())