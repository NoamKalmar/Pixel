from robot import Robot
import numpy as np
from time import sleep

def main_show(robot: Robot, frame: np.ndarray) -> None:
    robot.loop(frame, True)
    robot.motors_manager.move_straight(255)
    # robot.mimic_movements()

def square_show(robot: Robot, frame: np.ndarray) -> None:
    robot.loop(frame, True)
    robot.motors_manager.move_straight(255)
    sleep(1)
    robot.motors_manager.move_side(255)
    sleep(1)
    robot.motors_manager.move_straight(-255)
    sleep(1)
    robot.motors_manager.move_side(-255)
    sleep(1)