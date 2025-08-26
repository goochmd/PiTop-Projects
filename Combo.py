from time import sleep
from PIL import ImageDraw
from pitop import BrakingType, EncoderMotor, ForwardDirection, UltrasonicSensor, ServoMotor, ServoMotorSetting, Camera

# Setup the motor

motor1 = EncoderMotor("M2", ForwardDirection.CLOCKWISE)
motor2 = EncoderMotor("M3", ForwardDirection.COUNTER_CLOCKWISE)
motor1.braking_type = BrakingType.COAST
motor2.braking_type = BrakingType.COAST


# Move in both directions

rpm_speed = 100
for _ in range(4):
    motor1.set_target_rpm(rpm_speed)
    sleep(2)
    motor1.set_target_rpm(-rpm_speed)
    sleep(2)

motor1.stop()
motor2.stop()

distance_sensor = UltrasonicSensor("D3", threshold_distance=0.2)

# Set up functions to print when an object crosses 'threshold_distance'
distance_sensor.when_in_range = lambda: print("in range")
distance_sensor.when_out_of_range = lambda: print("out of range")

while True:
    # Print the distance (in meters) to an object in front of the sensor
    print(distance_sensor.distance)
    sleep(0.1)

servo = ServoMotor("S0")

# Scan back and forward across a 180 degree angle range in 30 degree hops using default servo speed
for angle in range(90, -100, -30):
    print("Setting angle to", angle)
    servo.target_angle = angle
    sleep(0.5)

# you can also set angle with a different speed than the default
servo_settings = ServoMotorSetting()
servo_settings.speed = 25

cam = Camera()

def draw_red_cross_over_image(im):
    # Use Pillow to draw a red cross over the image
    draw = ImageDraw.Draw(im)
    draw.line((0, 0) + im.size, fill=128, width=5)
    draw.line((0, im.size[1], im.size[0], 0), fill=128, width=5)
    return im

im = draw_red_cross_over_image(cam.get_frame())
im.show()
