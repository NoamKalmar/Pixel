from robot import Robot, Show
from time import sleep, time
from angle_consts import *

def test(robot: Robot):
    print("Hello, World!")

def setup(robot: Robot):
    robot.servos_manager.set_hands(HAND_DOWN)
    sleep(27)

def waking_up(robot: Robot):
    # Head move
    robot.servos_manager.move_head(0)
    sleep(3)
    robot.servos_manager.move_head(90)
    # Hands Move
    robot.servos_manager.move_hands_mirror(HAND_UP)
    sleep(1)
    robot.servos_manager.set_hands(MUSCLE)
    sleep(1)

def robot_move(robot: Robot):
    robot.servos_manager.switch_move((0, 0, 90), (0, 180, 90), 0.01)
    sleep(1)
    robot.servos_manager.move_right_hand((0, 180, 90), rate=0.005)
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
    while robot.get_emotion() != 0:
        pass

def wait_for_unsmile(robot: Robot):
    while robot.get_emotion() == 0:
        pass

def mimic_interaction(robot: Robot): # 40 s
    robot.move_human_x(stop=True)
    robot.add_to_loop(robot.mimic_movements)
    sleep(40)
    robot.remove_from_loop(robot.mimic_movements)

def full_follow(robot: Robot): # 27 s
    robot.servos_manager.set_hands((HAND_DOWN)) 
    robot.add_to_loop(robot.follow_human)
    sleep(27)
    robot.remove_from_loop(robot.remove_from_loop)

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

MAIN_SHOW = Show(name="main",
                 steps=[
                    setup,
                    waking_up,
                    robot_move,
                    turn,
                    one_by_one,
                    zombie_walk,
                    wind_turbine,
                    one_by_one,
                    move_one_by_one,
                    turn_to_mimic,
                    wait_for_smile,
                    wait_for_unsmile,
                    mimic_interaction,
                    full_follow,
                    dance,
                    chase,
                 ])

def wait2(robot):
    print("2 seconds")

def wait3(robot):
    print("3 seconds")

test_show = Show(name="test",
                 steps=[
                     (wait2, 2),
                     (wait3, 3)
                 ])