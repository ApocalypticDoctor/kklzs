from pynput.mouse import Controller
import math
from threading import Event


def mouse_reset(e: Event):
    mouse = Controller()
    last_position = mouse.position
    while not e.is_set():
        current_position = mouse.position
        distance = math.sqrt(
            (current_position[0] - last_position[0]) ** 2
            + (current_position[1] - last_position[1]) ** 2
        )
        if distance > 200:
            mouse.position = last_position
        else:
            last_position = current_position
