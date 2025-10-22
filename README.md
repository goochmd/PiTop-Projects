# Pi Top Projects
Websites to use:
https://github.com/pi-top/pi-top-Python-SDK/tree/master - PiTop SDK


##Remote Control:
The controller and server programs work together to enable remote control of a Pi-top robot with real-time video feedback. The server program runs on the Pi-top, managing two network servers: one receives keypress commands to control the robot’s movement and camera servos, while the other streams live video from the Pi-top’s camera to the client. The controller program, running on a separate computer, connects to these servers, sending keyboard events to direct the robot and displaying the incoming video stream for the user, allowing interactive and responsive remote operation.