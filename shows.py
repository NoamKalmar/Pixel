from robot import Robot
import numpy as np

def main_show(robot: Robot, frame: np.ndarray) -> None:
    robot.loop(frame, True)
    robot.motors_manager.move_straight(255)
    # robot.mimic_movements()