from time import sleep

from pitop import ServoMotor, ServoMotorSetting

servo = ServoMotor("S0")

# Scan back and forward across a 180 degree angle range in 30 degree hops using default servo speed
for angle in range(90, -100, -30):
    print("Setting angle to", angle)
    servo.target_angle = angle
    sleep(0.5)

# you can also set angle with a different speed than the default
servo_settings = ServoMotorSetting()
servo_settings.speed = 25
