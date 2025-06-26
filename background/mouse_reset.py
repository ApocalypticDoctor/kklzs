import time

from pynput.mouse import Controller
import math
from threading import Event


def mouse_reset(e: Event):
    mouse = Controller()
    last_position = mouse.position
    last_check_time = time.time()
    while not e.is_set():
        current_position = mouse.position
        current_time = time.time()
        distance = math.sqrt(
            (current_position[0] - last_position[0]) ** 2
            + (current_position[1] - last_position[1]) ** 2
        )
        time_elapsed = current_time - last_check_time
        if distance > 200 and time_elapsed < 0.01:
            mouse.position = last_position
        else:
            last_check_time = current_time
            last_position = current_position