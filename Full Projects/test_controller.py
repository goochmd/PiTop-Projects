import socket, struct, cv2, numpy as np
from pynput import keyboard

HOST = "10.0.17.80"
PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

def send_cmd(msg: str):
    sock.sendall((msg + "\n").encode())

def on_press(key):
    try:
        if hasattr(key, "char") and key.char:
            send_cmd(f"PRESS_{key.char.upper()}")
        elif key == keyboard.Key.left:
            send_cmd("PRESS_LEFT")
        elif key == keyboard.Key.right:
            send_cmd("PRESS_RIGHT")
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
            sock.close()
            listener.stop()
    except:
        pass

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

while True:
    # Read header
    header = sock.recv(5)
    if not header:
        break
    msg_type, size = struct.unpack(">BI", header)

    # Read payload
    data = b""
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            break
        data += packet

    if msg_type == 0x01:  # JPEG frame
        frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
        if frame is not None:
            cv2.imshow("Pi-top Camera", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    elif msg_type == 0x02:  # Text
        print("Response:", data.decode())
