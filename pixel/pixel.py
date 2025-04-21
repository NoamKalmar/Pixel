import sys
import argparse
import cv2
import mediapipe as mp
from pyfirmata import ArduinoMega

from robot import Robot, RobotMotorsManager, RobotServosManager
from robot_controller import RobotController
import shows    

emotion_videos_foler_path = "emotion_videos"
emotion_video_paths = [f"{emotion_videos_foler_path}/happy.mp4", 
                       f"{emotion_videos_foler_path}/sad.mp4", 
                       f"{emotion_videos_foler_path}/neutral.mp4"]

ROBOT_NAME = "pixel"

BAUDRATE = 115200
PORT = "COM4"

RIGHT_HAND_PINS = (2, 3, 4)
LEFT_HAND_PINS = (5, 6, 7)
HEAD_PIN = 8

LEFT_MOTOR_PINS = (28, 30, 11)
RIGHT_MOTOR_PINS = (40, 42, 13)
BACK_MOTOR_PINS = (34, 36, 12)
FRONT_MOTOR_PINS = (24, 22, 10)

SHOWS = [shows.MAIN_SHOW, shows.test_show]

mp_holistic = mp.solutions.holistic

def read_emotion_videos(paths: list) -> list:
    videos = []
    for path in paths:
        video = cv2.VideoCapture(path)
        videos.append(video)
    return videos

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sim", 
        action="store_true", 
        help="Run without connecting a phyisical Arduino board"
    )
    parser.add_argument(
        "--crash", 
        action="store_true", 
        help="Crash the program in case an exception is raised when running a command sent by the controller app"
    )
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    videos = read_emotion_videos(emotion_video_paths)
    servos_manager = None
    motors_manager = None
    if not args.sim:
        board = ArduinoMega(PORT)
        servos_manager = RobotServosManager(board, RIGHT_HAND_PINS, LEFT_HAND_PINS, HEAD_PIN)
        motors_manager = RobotMotorsManager(board, 
                                            LEFT_MOTOR_PINS, 
                                            RIGHT_MOTOR_PINS, 
                                            BACK_MOTOR_PINS, 
                                            FRONT_MOTOR_PINS)
    
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        pixel = Robot(
            holistic=holistic,
            motors_manager=motors_manager, 
            servos_manager=servos_manager, 
            name=ROBOT_NAME
        )
        pixel.load_shows(SHOWS)
        
        controller = RobotController(pixel, crash_if_error=args.crash)
        controller.start()

if __name__ == "__main__":
    main()