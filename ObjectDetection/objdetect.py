import asyncio as aio, numpy as np, cv2, struct
from pitop import Camera, ServoMotor, EncoderMotor, LED, UltrasonicSensor
from pitop.robotics import DriveController

cam = Camera(resolution=(1280, 720))
uss = UltrasonicSensor("D3", threshold_distance=1, max_distance=300)
brakelight = LED("D0")
panservo = ServoMotor("S0")
tiltservo = ServoMotor("S1")
drive = DriveController(left_motor_port="M2", right_motor_port="M3")
panservo.target_angle = 0
tiltservo.target_angle = 15

state = {"keys": set(), "running": True, "pan_angle": 0, "tilt_angle": 0}


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

async def main():
    video_server = await aio.start_server(handle_video, "0.0.0.0", 10000)
    print("Video server running on 10000")
    async with video_server:
        await aio.gather(
            video_server.serve_forever(),
        )
aio.run(main())