import asyncio
import sys
from sshkeyboard import listen_keyboard

from drive_controller import DriveController  # import your class

# Create the drive object
drive = DriveController()

# State tracking
keys_held = set()
running = True


# Keyboard event handler
def keyboard_listener(button, event_type):
    global running
    if event_type == "press":
        keys_held.add(button)
    elif event_type == "release":
        keys_held.discard(button)

    if button == "escape" and event_type == "press":
        running = False
        asyncio.get_event_loop().call_later(1, sys.exit, 0)


# Movement loop
async def movement_loop():
    global running
    while running:
        if "w" in keys_held:
            drive.forward(0.8)  # 80% of max speed
        elif "s" in keys_held:
            drive.backward(0.8)
        elif "a" in keys_held:
            drive.left(0.8)  # rotate left in place
        elif "d" in keys_held:
            drive.right(0.8)
        else:
            drive.stop()

        await asyncio.sleep(0.1)


# Main entry
async def main():
    asyncio.create_task(
        asyncio.to_thread(
            listen_keyboard,
            on_press=lambda k: keyboard_listener(k, "press"),
            on_release=lambda k: keyboard_listener(k, "release"),
        )
    )
    await movement_loop()


if __name__ == "__main__":
    asyncio.run(main())
