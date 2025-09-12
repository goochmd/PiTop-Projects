"""Pi-Top Remote Control Client (Controller)
This script connects to two servers running on the Pi-top:
1. Keybind Server: Sends keypress events to control the robot remotely.
2. Video Server: Receives and displays real-time video frames from the Pi-top camera.
Purposes for Libraries Used:
- socket: For TCP networking to communicate with the Pi-top servers.
- struct: For packing and unpacking binary data for video frame transmission.
- cv2 (OpenCV): For decoding and displaying video frames.
- numpy: For efficient array manipulations, especially for image data.
- pynput: For capturing keyboard events and sending them to the Pi-top.
- threading: For running the video receiver in a separate thread.

!!NOTE!!: This code is intended to be run on a client computer, not on the Pi-top itself.
It requires the Pi-top server code to be running and accessible on the specified network.
"""
import socket, struct, cv2, numpy as np
from pynput import keyboard
import threading

HOST = "10.0.17.80"  # Update as needed
KEYBIND_PORT = 9999
VIDEO_PORT = 10000

# Keybind socket (Sends Keybind Events)
try:
    keybind_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    keybind_sock.connect((HOST, KEYBIND_PORT))
    print(f"Connected to keybind server {HOST} at port {KEYBIND_PORT}")
except TimeoutError as e:
    print(f"Connection to keybind server timed out!")

# Video socket (Recieves Video Frames)
try:
    video_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    video_sock.connect((HOST, VIDEO_PORT))
    print(f"Connected to video server {HOST} at port {VIDEO_PORT}")
except TimeoutError as e:
    print(f"Connection to video server timed out!")

def send_cmd(msg: str):
    keybind_sock.sendall((msg + "\n").encode())

def on_press(key):
    try:
        if hasattr(key, "char") and key.char:
            send_cmd(f"PRESS_{key.char.upper()}")
        elif key == keyboard.Key.left:
            send_cmd("PRESS_LEFT")
        elif key == keyboard.Key.right:
            send_cmd("PRESS_RIGHT")
        elif key == keyboard.Key.up:
            send_cmd("PRESS_UP")
        elif key == keyboard.Key.down:
            send_cmd("PRESS_DOWN")
    except:
        pass

def on_release(key):
    try:
        if hasattr(key, "char") and key.char:
            send_cmd(f"RELEASE_{key.char.upper()}")
        elif key == keyboard.Key.left:
            send_cmd("RELEASE_LEFT")
        elif key == keyboard.Key.right:
            send_cmd("RELEASE_RIGHT")
        if key == keyboard.Key.esc:
            send_cmd("EXIT")
            keybind_sock.close()
            video_sock.close()
            listener.stop()
    except:
        pass

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# Thread for receiving video frames
def video_thread():
    while True:
        header = video_sock.recv(5)
        if not header:
            break
        msg_type, size = struct.unpack(">BI", header)
        data = b""
        while len(data) < size:
            packet = video_sock.recv(size - len(data))
            if not packet:
                break
            data += packet
        if msg_type == 0x01:  # JPEG frame
            frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
            if frame is not None:
                w,h,c = frame.shape
                cv2.namedWindow("Pi-top Camera")
                cv2.resizeWindow("Pi-top Camera", 1920, 1080)
                new_w = int(w*1.5)
                new_h = int(h*1.5)
                frame = cv2.resize(frame, (new_w, new_h))
                frame = cv2.copyMakeBorder(frame, 0, max(0, 1080-new_h), 0, max(0, 1920-new_w), 0)
                cv2.imshow("Pi-top Camera", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    break
    video_sock.close()
    cv2.destroyAllWindows()

video_t = threading.Thread(target=video_thread, daemon=True)
video_t.start()

# Keep main thread alive
try:
    while video_t.is_alive():
        video_t.join(1)
except KeyboardInterrupt:
    pass
