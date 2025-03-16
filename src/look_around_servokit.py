# Set up libraries and overall settings
from time import sleep  # Imports sleep (aka wait or pause) into the program
import numpy as np
from adafruit_servokit import ServoKit, _Servo
import threading
from collections import deque

kit = ServoKit(channels=16)

horizontal_min = 45
horizontal_max = 120
horizontal_center = 82

vertical_min = 60
vertical_max = 140
vertical_center = 100

ph = kit.servo[0]
pv = kit.servo[1]

ph.angle = 90
pv.angle = 90

ph.angle = None
pv.angle = None


def limit_angle(angle: float, direction="horizontal"):
    if direction == "vertical":
        angle = max(angle, vertical_min)
        angle = min(angle, vertical_max)
    else:
        angle = max(angle, horizontal_min)
        angle = min(angle, horizontal_max)
    return angle


def angle_interpolation2d(
    start_angle_hor: float,
    end_angle_hor: float,
    ph: _Servo,
    start_angle_ver: float,
    end_angle_ver: float,
    pv: _Servo,
    steps: int = 50,
):
    for i in np.linspace(0, 1, steps):
        interpolated_angle_hor = (
            start_angle_hor
            + (end_angle_hor - start_angle_hor) * (1 - np.cos(i * np.pi)) / 2
        )
        interpolated_angle_ver = (
            start_angle_ver
            + (end_angle_ver - start_angle_ver) * (1 - np.cos(i * np.pi)) / 2
        )
        ph.angle = limit_angle(interpolated_angle_hor, "horizontal")
        pv.angle = limit_angle(interpolated_angle_ver, "vertical")
        sleep(0.01)


def look_up(cur_angle_hor, cur_angle_ver):
    angle_interpolation2d(
        cur_angle_hor, horizontal_center, ph, cur_angle_ver, vertical_min, pv
    )
    return horizontal_center, vertical_min


def look_down(cur_angle_hor, cur_angle_ver):
    angle_interpolation2d(
        cur_angle_hor, horizontal_center, ph, cur_angle_ver, vertical_max, pv
    )
    return horizontal_center, vertical_max


def look_right(cur_angle_hor, cur_angle_ver):
    angle_interpolation2d(
        cur_angle_hor, horizontal_min, ph, cur_angle_ver, vertical_center, pv
    )
    return horizontal_min, vertical_center


def look_left(cur_angle_hor, cur_angle_ver):
    angle_interpolation2d(
        cur_angle_hor, horizontal_max, ph, cur_angle_ver, vertical_center, pv
    )
    return horizontal_max, vertical_center


def look_center(cur_angle_hor, cur_angle_ver):
    angle_interpolation2d(
        cur_angle_hor, horizontal_center, ph, cur_angle_ver, vertical_center, pv
    )
    return horizontal_center, vertical_center


def look_up_left(cur_angle_hor, cur_angle_ver):
    angle_interpolation2d(
        cur_angle_hor, horizontal_max, ph, cur_angle_ver, vertical_min, pv
    )
    return horizontal_max, vertical_min


def look_up_right(cur_angle_hor, cur_angle_ver):
    angle_interpolation2d(
        cur_angle_hor, horizontal_min, ph, cur_angle_ver, vertical_min, pv
    )
    return horizontal_min, vertical_min


def look_down_left(cur_angle_hor, cur_angle_ver):
    angle_interpolation2d(
        cur_angle_hor, horizontal_max, ph, cur_angle_ver, vertical_max, pv
    )
    return horizontal_max, vertical_max


def look_down_right(cur_angle_hor, cur_angle_ver):
    angle_interpolation2d(
        cur_angle_hor, horizontal_min, ph, cur_angle_ver, vertical_max, pv
    )
    return horizontal_min, vertical_max


def clip_mode():
    from interpret_webcam import get_look_direction

    cah, cav = horizontal_center, vertical_center
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
                cah, cav = look_right(cah, cav)

        elif horizontal == "left":
            if vertical == "up":
                cah, cav = look_up_left(cah, cav)
            elif vertical == "down":
                cah, cav = look_down_left(cah, cav)
            else:
                cah, cav = look_left(cah, cav)

        else:
            if vertical == "up":
                cah, cav = look_up(cah, cav)
            elif vertical == "down":
                cah, cav = look_down(cah, cav)
            else:
                cah, cav = look_center(cah, cav)

        ph.angle = None
        pv.angle = None


target_cah = horizontal_center
target_cav = vertical_center


def bezier_interpolation(p0, p1, p2, p3, t):
    """Calculate the position on a cubic Bezier curve."""
    return (
        (1 - t) ** 3 * p0
        + 3 * (1 - t) ** 2 * t * p1
        + 3 * (1 - t) * t**2 * p2
        + t**3 * p3
    )


def face_detection_mode_smooth(plot: bool = False):
    from face_tracking import detect_face

    global target_cah, target_cav
    position_queue = deque(
        maxlen=1
    )  # Queue to store the last 4 positions for Bezier curve

    def detect_faces():
        while True:
            px, py = detect_face(plot)
            if px is not None and py is not None:
                px = 1 / (1 + np.exp(-10 * (px - 0.5)))
                py = 1 / (1 + np.exp(-15 * (py - 0.3)))
                pxa = (1 - px) * (horizontal_max - horizontal_min) + horizontal_min
                pya = py * (vertical_max - vertical_min) + vertical_min
                if len(position_queue) == 1:
                    position_queue.popleft()
                position_queue.append((pxa, pya))

    def move_servos():
        global target_cah, target_cav
        cah, cav = horizontal_center, vertical_center
        while True:
            if len(position_queue) >= 1:
                (p0,) = position_queue
                # for t in np.linspace(0, 1, 40):
                #    target_cah = bezier_interpolation(cah, p0[0], p1[0], p2[0], t)
                #    target_cav = bezier_interpolation(cav, p0[1], p1[1], p2[1], t)
                target_cah = cah + 0.005 * (p0[0] - cah)
                target_cav = cav + 0.005 * (p0[1] - cav)
                ph.angle = limit_angle(target_cah, "horizontal")
                pv.angle = limit_angle(target_cav, "vertical")
                cah = target_cah
                cav = target_cav
                # sleep(0.01)
                # position_queue.popleft()  # Remove the oldest position after interpolation
            else:
                sleep(0.01)

    # Start the face detection thread
    face_detection_thread = threading.Thread(target=detect_faces)
    face_detection_thread.daemon = True
    face_detection_thread.start()

    # Start the servo movement thread
    move_servos_thread = threading.Thread(target=move_servos)
    move_servos_thread.daemon = True
    move_servos_thread.start()

    # Keep the main thread alive
    while True:
        sleep(1)


def face_detection_mode(plot: bool = False):
    from face_tracking import detect_face

    cah, cav = horizontal_center, vertical_center
    while True:
        px, py = detect_face(plot)

        if px is not None and py is not None:
            px = 1 / (1 + np.exp(-10 * (px - 0.5)))
            py = 1 / (1 + np.exp(-15 * (py - 0.3)))
            print(px, py)
            pxa = (1 - px) * (horizontal_max - horizontal_min) + horizontal_min
            pya = py * (vertical_max - vertical_min) + vertical_min
            print(pxa, pya)
            angle_interpolation2d(cah, pxa, ph, cav, pya, pv, steps=20)
            cah = pxa
            cav = pya

        ph.angle = None
        pv.angle = None


def random_movement_mode():
    cah, cav = horizontal_center, vertical_center
    while True:
        new_cah = np.random.randint(horizontal_min, horizontal_max)
        new_cav = np.random.randint(vertical_min, vertical_max)
        angle_interpolation2d(
            cah,
            new_cah,
            ph,
            cav,
            new_cav,
            pv,
            steps=np.random.randint(40, 100),
        )
        cah = new_cah
        cav = new_cav
        ph.angle = None
        pv.angle = None
        sleep(np.random.random() * 0.5)


if __name__ == "__main__":
    try:
        mode = input("Choose Mode [CLIP, FACE, RANDOM] ")
        if mode.lower() == "clip":
            clip_mode()

        elif mode.lower() == "face":
            face_detection_mode_smooth(plot=False)

        elif mode.lower() == "random":
            random_movement_mode()

        else:
            print("Invalid mode")
    except KeyboardInterrupt:
        pass
    finally:
        # Clean up everything
        ph.angle = None  # At the end of the program, stop the PWM
        pv.angle = None
