from robot import Robot
import numpy as np
from time import sleep

def main_show(robot: Robot, frame: np.ndarray) -> None:
    robot.loop(frame, True)
    # robot.mimic_movements()

def square_show(robot: Robot) -> None:
    robot.motors_manager.move_straight(255)
    sleep(1)
    robot.motors_manager.move_side(255)
    sleep(1)
    robot.motors_manager.move_straight(-255)
    sleep(1)
    robot.motors_manager.move_side(-255)
    sleep(1)

def test(robot: Robot):
    robot.follow_human()