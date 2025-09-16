from pitop import Camera, Buzzer, LED, Button, Potentiometer

# Example code for Camera
# Records videos of any motion captured by the camera

cam = Camera()


def motion_detected():
    print("Motion detected!")
    buzzer.play_tone(440, 60)
    for i in range(120):
        red_led.on()
        sleep(0.5)
        red_led.off()


print("Motion detector starting...")
cam.start_detecting_motion(
    callback_on_motion=motion_detected, moving_object_minimum_area=350
)

sleep(60)

cam.stop_detecting_motion()
print("Motion detector stopped")