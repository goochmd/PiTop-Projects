import asyncio as aio
import cv2, numpy as np, struct
from pitop import Camera, ServoMotor
from pitop.robotics import DriveController
import sys

cam = Camera(resolution=(1920, 1080))
servo = ServoMotor("S0")
drive = DriveController(left_motor_port="M2", right_motor_port="M3")

state = {"keys": set(), "running": True, "send_video": True}

async def handle_client(reader, writer):
    async def send_frame():
        while state["running"]:
            if state["send_video"]:
                frame = cam.get_frame()  # PIL image
                frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
                _, jpeg = cv2.imencode(".jpg", frame)
                data = jpeg.tobytes()
                header = struct.pack(">BI", 0x01, len(data))  # type=1, size
                writer.write(header + data)
                await writer.drain()
            await aio.sleep(0.05)  # ~20 FPS

    aio.create_task(send_frame())

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

#region Variable Setting
async def variable_setter():
    while state["running"]:
        if "w" in state["keys"]:
            drive.forward(1)  # 80% of max speed
        elif "s" in state["keys"]:
            drive.backward(1)
        elif "a" in state["keys"]:
            drive.rotate(0.2)  # rotate left in place
        elif "d" in state["keys"]:
            drive.rotate(-0.2)  # rotate right in place
        else:
            drive.stop()

        # Servo control
        if 'left' in state["keys"]:
            state["servo_angle"] = max(-90, state["servo_angle"] - 5)
            servo.target_angle = state['servo_angle']
        elif 'right' in state["keys"]:
            state["servo_angle"] = min(90, state["servo_angle"] + 5)
            servo.target_angle = state['servo_angle']

        # Exit program
        if 'escape' in state["keys"]:
            state["running"] = False
            loop = aio.get_event_loop()
            loop.call_later(1, sys.exit, 0)

        await aio.sleep(0.1)  # keep looping


#endregion

#region Main

async def main():
    server = await aio.start_server(handle_client, "0.0.0.0", 9999)
    print("Server running on 9999")
    async with server:
        await aio.gather(
            variable_setter(),
            server.serve_forever(),
        )
    

aio.run(main())
