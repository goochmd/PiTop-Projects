import socket, struct, cv2, numpy as np
from pynput import keyboard
import threading

HOST = "10.0.17.80"  # Update as needed
VIDEO_PORT = 10000
# Video socket (Recieves Video Frames)
try:
    video_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    video_sock.connect((HOST, VIDEO_PORT))
    print(f"Connected to video server {HOST} at port {VIDEO_PORT}")
except TimeoutError as e:
    print(f"Connection to video server timed out!")


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