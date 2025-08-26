from time import sleep

from pitop import BrakingType, EncoderMotor, ForwardDirection

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
