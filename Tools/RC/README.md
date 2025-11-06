# Remote Control (RC)

This folder contains code for manual control and a small server component that can accept remote commands or provide telemetry.

## Files
### - `controller.py` — client-side controller logic
  - Purpose: read input from a human operator (gamepad, keyboard, or other input device), map inputs to motion commands (e.g., left/right motor speeds), and send commands either directly to motor controllers or to a remote server.
  - Typical features:
    - Input mapping and deadzone handling for joysticks.
    - Rate limiting and smoothing for motor commands to avoid abrupt changes.
    - Optional calibration routines for joysticks and control curves.

### - `server.py` — lightweight remote control server
  - Purpose: accept incoming control messages (e.g., via TCP, UDP, or WebSocket) and translate them into motor commands or internal events. It can also serve telemetry (sensor data) to remote clients.
  - Security note: if exposing a server to a network, add basic authentication or restrict access to a private network. Avoid running an open server on the internet without protections.

## Protocols & integration
- Simple JSON-over-TCP: clients send small JSON messages like `{ "throttle": 0.5, "steer": -0.1 }` and the server validates and forwards these to motor logic.
- WebSocket: useful for browser-based UIs to send commands and receive telemetry.
- Direct GPIO control: `controller.py` can map inputs to direct motor PWM output when the controller script runs on the robot.

## Examples & operation
- Local control (direct motors): run `controller.py` on the robot with the input device connected; it will write PWM outputs to the motor controller.
- Remote control (client/server): run `server.py` on the robot and run a remote client that connects and sends control messages. The server should sanitize inputs and clamp values to safe ranges before invoking motor commands.

## Safety & best practices
- Add an input timeout: if the server or controller stops receiving input for more than a configurable period, the motors should be commanded to brake or enter a safe state.
- Command clamping: clamp motor commands to [-1.0, 1.0] or a hardware-specific safe range.
- Emergency stop: always expose a hardware or software emergency-stop that halts the motors immediately.
