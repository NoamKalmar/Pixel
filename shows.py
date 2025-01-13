from robot import Robot
import numpy as np

def main_show(robot: Robot, frame: np.ndarray):
    robot.loop(frame, True)
    # robot.mimic_movements()