# Set up libraries and overall settings
import RPi.GPIO as GPIO  # Imports the standard Raspberry Pi GPIO library
from time import sleep  # Imports sleep (aka wait or pause) into the program
import numpy as np


GPIO.setmode(GPIO.BOARD)  # Sets the pin numbering system to use the physical layout

# Set up pin 11 for PWM
GPIO.setup(11, GPIO.OUT)  # Sets up pin 11 to an output (instead of an input)
GPIO.setup(12, GPIO.OUT)  # Sets up pin 12 to an output (instead of an input)
ph = GPIO.PWM(11, 50)  # Sets up pin 11 as a PWM pin
pv = GPIO.PWM(12, 50)  # Sets up pin 12 as a PWM pin

ph.start(0)
pv.start(0)

back_pwm = 2
front_pwm = 12


def angle_to_duty_cyle(angle: float):
    return (angle / 180) * (front_pwm - back_pwm) + back_pwm


def duty_cycle_to_angle(duty_cycle: float):
    return (duty_cycle - back_pwm) / (front_pwm - back_pwm) * 180


# interpolates between two angles with a cosine like shape so that it
# starts slow and ends slow but is quick in-between
def angle_interpolation(
    start_angle: float, end_angle: float, p: GPIO.PWM, steps: int = 50
):
    start_duty_cycle = angle_to_duty_cyle(start_angle)
    end_duty_cycle = angle_to_duty_cyle(end_angle)
    for i in np.linspace(0, 1, steps):
        interpolated_duty_cycle = (
            start_duty_cycle
            + (end_duty_cycle - start_duty_cycle) * (1 - np.cos(i * np.pi)) / 2
        )
        p.ChangeDutyCycle(interpolated_duty_cycle)
        sleep(0.01)


def angle_interpolation2d(
    start_angle_hor: float,
    end_angle_hor: float,
    ph: GPIO.PWM,
    start_angle_ver: float,
    end_angle_ver: float,
    pv: GPIO.PWM,
    steps: int = 50,
):
    start_duty_cycle_hor = angle_to_duty_cyle(start_angle_hor)
    end_duty_cycle_hor = angle_to_duty_cyle(end_angle_hor)
    start_duty_cycle_ver = angle_to_duty_cyle(start_angle_ver)
    end_duty_cycle_ver = angle_to_duty_cyle(end_angle_ver)
    for i in np.linspace(0, 1, steps):
        interpolated_duty_cycle_hor = (
            start_duty_cycle_hor
            + (end_duty_cycle_hor - start_duty_cycle_hor) * (1 - np.cos(i * np.pi)) / 2
        )
        interpolated_duty_cycle_ver = (
            start_duty_cycle_ver
            + (end_duty_cycle_ver - start_duty_cycle_ver) * (1 - np.cos(i * np.pi)) / 2
        )
        ph.ChangeDutyCycle(interpolated_duty_cycle_hor)
        pv.ChangeDutyCycle(interpolated_duty_cycle_ver)
        sleep(0.01)


def look_up(cur_angle):
    angle_interpolation(cur_angle, 60, pv)
    return 60


def look_down(cur_angle):
    angle_interpolation(cur_angle, 130, pv)
    return 130


def look_right(cur_angle_hor):
    angle_interpolation(cur_angle_hor, 65, ph)
    return 65


def look_left(cur_angle_hor):
    angle_interpolation(cur_angle_hor, 130, ph)
    return 130


def look_center(cur_angle_hor, cur_angle_ver):
    angle_interpolation2d(cur_angle_hor, 90, ph, cur_angle_ver, 100, pv)
    return 90, 100


def look_up_left(cur_angle_hor, cur_angle_ver):
    angle_interpolation2d(cur_angle_hor, 130, ph, cur_angle_ver, 70, pv)
    return 130, 70


def look_up_right(cur_angle_hor, cur_angle_ver):
    angle_interpolation2d(cur_angle_hor, 70, ph, cur_angle_ver, 80, pv)
    return 70, 80


def look_down_left(cur_angle_hor, cur_angle_ver):
    angle_interpolation2d(cur_angle_hor, 130, ph, cur_angle_ver, 130, pv)
    return 130, 130


def look_down_right(cur_angle_hor, cur_angle_ver):
    angle_interpolation2d(cur_angle_hor, 80, ph, cur_angle_ver, 140, pv)
    return 80, 140


def clip_mode():
    from interpret_webcam import get_look_direction

    cah, cav = 90, 90
    look_for = ""
    while True:
        look_for = input("What do you want to look for? ")
        if look_for == "exit":
            break
        horizontal, vertical = get_look_direction(look_for)
        print("looking", horizontal, vertical)
        if horizontal == "right":
            if vertical == "up":
                cah, cav = look_up_right(cah, cav)
            elif vertical == "down":
                cah, cav = look_down_right(cah, cav)
            else:
                cah = look_right(cah)

        elif horizontal == "left":
            if vertical == "up":
                cah, cav = look_up_left(cah, cav)
            elif vertical == "down":
                cah, cav = look_down_left(cah, cav)
            else:
                cah = look_left(cah)

        else:
            if vertical == "up":
                cav = look_up(cav)
            elif vertical == "down":
                cav = look_down(cav)
            else:
                cah, cav = look_center(cah, cav)

        ph.ChangeDutyCycle(0)
        pv.ChangeDutyCycle(0)


def face_detection_mode():
    from face_tracking import detect_face

    cah, cav = 90, 90
    while True:
        px, py = detect_face()

        if px is not None and py is not None:
            pxa = (1 - px) * (150 - 45) + 45
            pya = py * (130 - 60) + 60
            print(pxa, pya)
            angle_interpolation2d(cah, pxa, ph, cav, pya, pv)
            cah = pxa
            cav = pya

        ph.ChangeDutyCycle(0)
        pv.ChangeDutyCycle(0)


mode = input("Choose Mode [CLIP, FACE]")
if mode.lower() == "clip":

    clip_mode()
elif mode.lower() == "face":
    face_detection_mode()
else:
    print("Invalid mode")

# Clean up everything
ph.stop()  # At the end of the program, stop the PWM
pv.stop()
GPIO.cleanup()  # Resets the GPIO pins back to defaults
