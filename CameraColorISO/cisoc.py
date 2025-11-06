# cisoc.py
import socket, struct, cv2, numpy as np
import threading
import queue

VIDEO_HOST = "10.0.17.80"  # Pi-top video server
VIDEO_PORT = 10000
PROCESSOR_HOST = "127.0.0.1"  # Local processor
PROCESSOR_PORT = 11000

color = "purple"
detection_threshold = 500

# HSV ranges for colors
ranges = {
    "purple": [(125, 50, 50), (155, 255, 255), (150, 50, 50), (170, 255, 255)]
}
lower1 = np.array(ranges[color][0], np.uint8)
upper1 = np.array(ranges[color][1], np.uint8)
lower2 = np.array(ranges[color][2], np.uint8)
upper2 = np.array(ranges[color][3], np.uint8)

# Thread-safe queue for processed frames
processed_queue = queue.Queue()

def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data

def video_receiver():
    video_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    video_sock.connect((VIDEO_HOST, VIDEO_PORT))
    print("Connected to Pi-top video server")

    while True:
        header = recv_exact(video_sock, 5)
        if not header:
            break
        msg_type, size = struct.unpack(">BI", header)
        data = recv_exact(video_sock, size)
        if data is None:
            break

        frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            continue

        # Color detection and contour processing
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(frame_hsv, lower1, upper1)
        mask2 = cv2.inRange(frame_hsv, lower2, upper2)
        full_mask = cv2.bitwise_or(mask1, mask2)

        contours, _ = cv2.findContours(full_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > detection_threshold:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Push the processed frame to the queue
        processed_queue.put(frame)

    video_sock.close()

def processor_sender():
    processor_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    processor_sock.connect((PROCESSOR_HOST, PROCESSOR_PORT))
    print("Connected to processor")

    while True:
        frame = processed_queue.get()  # Blocks until a frame is available
        _, jpeg = cv2.imencode(".jpg", frame)
        data = jpeg.tobytes()
        header = struct.pack(">BI", 0x01, len(data))
        try:
            processor_sock.sendall(header + data)
        except ConnectionResetError:
            print("Processor disconnected")
            break

    processor_sock.close()

# Start threads
threading.Thread(target=video_receiver, daemon=True).start()
threading.Thread(target=processor_sender, daemon=True).start()

# Keep main thread alive
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Exiting cisoc.py")
