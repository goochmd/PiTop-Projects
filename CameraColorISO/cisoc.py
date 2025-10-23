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
import time
import threading

HOST = "10.0.17.80"  # Update as needed
VIDEO_PORT = 10000

# Start with no video socket and connect lazily/reconnect as needed
video_sock = None


def try_connect_video():
    global video_sock
    if video_sock:
        return True
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((HOST, VIDEO_PORT))
        s.settimeout(None)
        video_sock = s
        print(f"Connected to video server {HOST} at port {VIDEO_PORT}")
        return True
    except Exception:
        video_sock = None
        return False

# No keyboard/keybind logic - this client only shows video

# Thread for receiving video frames
def recv_exact(sock: socket.socket, n: int):
    """Receive exactly n bytes from socket or return None if connection closed."""
    data = b""
    try:
        while len(data) < n:
            chunk = sock.recv(n - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    except Exception:
        return None


def video_thread():
    """Continuously receive frames, reconnecting if the server closes the connection.

    The server (`cisos.py`) can close the writer after sending a frame; this client
    therefore must tolerate connection drops and reconnect.
    """
    global video_sock
    try:
        while True:
            if not try_connect_video():
                # wait and retry
                time.sleep(0.5)
                continue

            try:
                # take a local reference so static checkers know it's not None
                sock = video_sock
                if sock is None:
                    # connection dropped between checks; retry
                    time.sleep(0.05)
                    continue

                header = recv_exact(sock, 5)
                if not header:
                    # Server closed connection; cleanup and reconnect
                    try:
                        sock.close()
                    except Exception:
                        pass
                    video_sock = None
                    time.sleep(0.1)
                    continue
                msg_type, size = struct.unpack(">BI", header)
                data = recv_exact(sock, size)
                if data is None:
                    try:
                        sock.close()
                    except Exception:
                        pass
                    video_sock = None
                    time.sleep(0.1)
                    continue

                if msg_type == 0x01:  # JPEG frame
                    frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
                    if frame is not None:
                        cv2.imshow("Pi-top Camera", frame)
                        if cv2.waitKey(1) & 0xFF == 27:
                            break
            except Exception as e:
                # Something went wrong with this connection; drop and reconnect
                # print a short message and retry
                print("Video connection error:", str(e))
                try:
                    if video_sock:
                        video_sock.close()
                except Exception:
                    pass
                video_sock = None
                time.sleep(0.5)
                continue
    finally:
        try:
            if video_sock:
                video_sock.close()
        except Exception:
            pass
        cv2.destroyAllWindows()

video_t = threading.Thread(target=video_thread, daemon=True)
video_t.start()

# Keep main thread alive
try:
    while video_t.is_alive():
        video_t.join(1)
except KeyboardInterrupt:
    pass
