from robot import Robot
from time import sleep

def main_show():
    def dance(robot: Robot):
        print("Dancing")
        return 1
    def interaction(robot: Robot):
        print("Interacting")
        return 1
    return [dance, interaction]

def square_show():
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

def showcase():
    def interaction(robot: Robot):
        following_status = robot.follow_human()
        if following_status != 3:
            return 0
        robot.mimic_movements()
        return 0
    return [interaction]