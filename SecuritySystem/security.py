from pitop import Camera, Buzzer, LED, Button, Potentiometer
from time import sleep

# Example code for Camera
# Records videos of any motion captured by the camera

cam = Camera()
buzzer = Buzzer("A0")
red_led = LED("D0")
button = Button("D1")
pot = Potentiometer("A1")

def motion_detected():
    password_inputed = 0
    print("Motion detected!")
    while password_inputed != 2:
        buzzer.play_tone(440, 0.5)
        red_led.on()
        sleep(0.5)
        buzzer.stop()
        red_led.off()
        sleep(0.5)

def on_button_pressed():
    global password_inputed
    if password_inputed == 0:
        if pot.value >= 0.95:
            password_inputed = 1
            print("First part of password correct")
    elif password_inputed == 1:
        if pot.value <= 0.05:
            password_inputed = 2
            print("Second part of password correct")


print("Motion detector starting...")
cam.start_detecting_motion(
    callback_on_motion=motion_detected, moving_object_minimum_area=350
)
button.when_pressed = on_button_pressed