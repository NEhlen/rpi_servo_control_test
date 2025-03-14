import time
from adafruit_servokit import ServoKit

# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
kit = ServoKit(channels=16)

horizontal_min = 45
horizontal_max = 130

vertical_min = 60
vertical_max = 145

kit.servo[0].angle = 90
kit.servo[1].angle = 90


kit.servo[0].angle = None
kit.servo[1].angle = None
