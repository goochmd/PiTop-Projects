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

HOST = "10.0.21.21"  # Update as needed
KEYBIND_PORT = 9999
VIDEO_PORT = 10000

# module-level sockets so callbacks can access them
keybind_sock = None
video_sock = None

def send_cmd(msg: str):
    """Send a newline-terminated command to the keybind server (safe no-op if socket missing)."""
    try:
        if keybind_sock:
            keybind_sock.sendall((msg + "\n").encode())
    except Exception:
        pass

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
    except Exception:
        pass

def on_release(key):
    try:
        if hasattr(key, "char") and key.char:
            send_cmd(f"RELEASE_{key.char.upper()}")
        elif key == keyboard.Key.left:
            send_cmd("RELEASE_LEFT")
        elif key == keyboard.Key.right:
            send_cmd("RELEASE_RIGHT")
        elif key == keyboard.Key.up:
            send_cmd("RELEASE_UP")
        elif key == keyboard.Key.down:
            send_cmd("RELEASE_DOWN")
        if key == keyboard.Key.esc:
            send_cmd("EXIT")
            # Return False from on_release to stop the listener
            try:
                if keybind_sock:
                    keybind_sock.close()
            except Exception:
                pass
            try:
                if video_sock:
                    video_sock.close()
            except Exception:
                pass
            return False
    except Exception:
        pass

# Thread for receiving video frames
def video_thread():
    global video_sock
    try:
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
                    cv2.imshow("Pi-top Camera", frame)
                    if cv2.waitKey(1) & 0xFF == 27:
                        break
    except Exception:
        pass
    finally:
        try:
            if video_sock:
                video_sock.close()
        except Exception:
            pass
        cv2.destroyAllWindows()

def main():
    global keybind_sock, video_sock

    try:
        keybind_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        keybind_sock.connect((HOST, KEYBIND_PORT))
        print(f"Connected to keybind server {HOST} at port {KEYBIND_PORT}")
    except Exception:
        print(f"Connection to keybind server timed out or failed!")

    # Video socket (Receives Video Frames)
    try:
        video_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        video_sock.connect((HOST, VIDEO_PORT))
        print(f"Connected to video server {HOST} at port {VIDEO_PORT}")
    except Exception:
        print(f"Connection to video server timed out or failed!")

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    video_t = threading.Thread(target=video_thread, daemon=True)
    video_t.start()
    try:
        while video_t.is_alive():
            video_t.join(1)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            if keybind_sock:
                keybind_sock.close()
        except Exception:
            pass
        try:
            if video_sock:
                video_sock.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()