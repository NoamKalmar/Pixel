from robot import Robot
from time import sleep

def main_show() -> None:
    def dance(robot: Robot):
        print("Dancing")
        return 1
    def interaction(robot: Robot):
        print("Interacting")
        return 1
    return [dance, interaction]

def square_show() -> None:
    def square(robot: Robot):
        robot.motors_manager.move_straight(255)
        sleep(1)
        robot.motors_manager.move_side(255)
        sleep(1)
        robot.motors_manager.move_straight(-255)
        sleep(1)
        robot.motors_manager.move_side(-255)
        sleep(1)
        robot.motors_manager.stop_moving()
        return -1
    return [square]

def test(robot: Robot):
    robot.motors_manager.turn_all_motors(150)
    if robot.landmarks:
        angles = robot.calculate_angles()
        print(angles)