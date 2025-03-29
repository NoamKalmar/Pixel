from robot import Robot
from time import sleep

def main_show():
    def setup(robot: Robot):
        robot.servos_manager.move_hands(90, 0, 0)
        sleep(5)
        return 1
    def waking_up(robot: Robot):
        # Head move
        robot.servos_manager.move_head(0)
        robot.servos_manager.wait_while_moving()
        robot.servos_manager.move(90)
        robot.servos_manager.wait_while_moving()
        # Hands Move
        return 2
    def interaction(robot: Robot):
        print("Interacting")
        return -1
    return [setup, waking_up]

def square_show():
    def square(robot: Robot):
        robot.motors_manager.move_y(255)
        sleep(1)
        robot.motors_manager.move_x(255)
        sleep(1)
        robot.motors_manager.move_y(-255)
        sleep(1)
        robot.motors_manager.move_x(-255)
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

def show_muscle():
    def setup(robot: Robot):
        robot.servos_manager.set_hands(0, 90, 0)
        return 1
    def show_muscle(robot: Robot):
        robot.servos_manager.move_hands(0, 105, 180)
        robot.servos_manager.wait_while_moving()
        robot.servos_manager.move_hands(0, 75, 0)
        robot.servos_manager.wait_while_moving()
        return 1
    return [setup, show_muscle]