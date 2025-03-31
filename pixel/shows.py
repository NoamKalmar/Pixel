from robot import Robot
from time import sleep, time
from angle_consts import *

def main_show():
    def setup(robot: Robot):
        robot.servos_manager.set_hands(HAND_DOWN)
        sleep(27)
    def waking_up(robot: Robot):
        # Head move
        robot.servos_manager.move_head(0)
        robot.servos_manager.wait_while_moving()
        sleep(3)
        robot.servos_manager.move_head(90)
        robot.servos_manager.wait_while_moving()
        # Hands Move
        robot.servos_manager.move_left_hand(HAND_UP)
        robot.servos_manager.wait_while_moving()
        robot.servos_manager.move_right_hand(HAND_UP)
        robot.servos_manager.wait_while_moving()
        sleep(1)
        robot.servos_manager.set_hands(MUSCLE)
        sleep(1)
    def robot_move(robot: Robot):
        robot.servos_manager.switch_move((0, 0, 90), (0, 180, 90), 0.01)
        sleep(1)
        robot.servos_manager.move_right_hand((0, 180, 90), rate=0.005)
        robot.servos_manager.wait_while_moving()
        sleep(0.5)
    def turn(robot: Robot):
        robot.servos_manager.set_hands((0, 90, 0))
        robot.motors_manager.turn(200)
        sleep(1)
        robot.motors_manager.stop_moving()
        sleep(1)
        robot.motors_manager.turn(-200)
        sleep(1)
        robot.motors_manager.stop_moving()
    def one_by_one(robot: Robot):
        robot.servos_manager.switch_move((90, 90, 90), (90, 90, 0), rate=0.005)
        robot.servos_manager.switch_move((90, 90, 90), (90, 90, 0), rate=0.005)
    def zombie_walk(robot: Robot):
        robot.motors_manager.move_y(255)
        robot.servos_manager.switch_move(HAND_MIDDLE, HAND_DOWN)
        robot.motors_manager.move_y(-255)
        robot.servos_manager.switch_move(HAND_MIDDLE, HAND_DOWN)
        robot.motors_manager.stop_moving()
    def wind_turbine(robot: Robot):
        robot.servos_manager.set_hands(HAND_DOWN)
        robot.servos_manager.move_right_path(TURBINE_PATH, rate=0.007)
        robot.servos_manager.move_left_path(TURBINE_PATH, rate=0.007)
    def move_one_by_one(robot: Robot):
        robot.motors_manager.move_x(255)
        one_by_one(robot)
        robot.motors_manager.stop_moving()
        sleep(1)
        robot.motors_manager.move_x(-255)
        sleep(2)
        robot.motors_manager.stop_moving()
    def turn_to_mimic(robot: Robot):
        robot.motors_manager.turn(200)
        sleep(0.6)
        robot.motors_manager.stop_moving()
    def wait_for_smile(robot: Robot):
        if robot.get_emotion() == 0:
            return None
        return -2
    def wait_for_unsmile(robot: Robot):
        if robot.get_emotion() != 0:
            robot.shows["main"]["data"]["start_mimic_time"] = time()
            return None
        return -2
    def mimic_interaction(robot: Robot):
        robot.move_human_x(stop=True)
        robot.mimic_movements()
        if time() - robot.shows["main"]["data"]["start_mimic_time"] > 40:
            robot.shows["main"]["data"]["start_follow_time"] = time()
            return None
        return -2
    def full_follow(robot: Robot):
        robot.servos_manager.set_hands((HAND_DOWN)) 
        robot.follow_human()
        if time() - robot.shows["main"]["data"]["start_follow_time"] > 27:
            return None
        return -2
    def dance(robot: Robot):
        robot.servos_manager.set_hands(MUSCLE)
        sleep(2)
    def chase(robot: Robot):
        # robot.motors_manager.turn(-200)
        # sleep(0.6)
        robot.motors_manager.move_y(-255)
        sleep(1)
        robot.motors_manager.move_y(255)
        robot.servos_manager.switch_move((90, 90, 90), (90, 0, 90))
        robot.servos_manager.switch_move((90, 90, 90), (90, 0, 90))
        robot.motors_manager.stop_moving()
        return -1

    return [setup, # 0
            waking_up, # 1
            robot_move, # 2
            turn, # 3
            one_by_one, # 4
            zombie_walk, # 5
            wind_turbine, # 6
            one_by_one, # 7
            move_one_by_one, # 8
            turn_to_mimic, # 9
            wait_for_smile, # 10
            wait_for_unsmile, # 11
            mimic_interaction, # 12
            full_follow, # 13
            dance, # 14
            chase] # 15

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
        robot.servos_manager.set_hands((0, 90, 0))
        return 1
    def show_muscle(robot: Robot):
        robot.servos_manager.move_hands((0, 105, 180))
        robot.servos_manager.wait_while_moving()
        robot.servos_manager.move_hands((0, 75, 0))
        robot.servos_manager.wait_while_moving()
        return 1
    return [setup, show_muscle]