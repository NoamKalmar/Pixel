import time
import sys
import cv2
import mediapipe as mp
from pyfirmata import ArduinoMega

import detect_landmarks
from servos_manager import RobotServosManager
from motors_manager import RobotMotorsManager
from robot import Robot
from robot_controller import RobotController
import shows    

emotion_videos_foler_path = "emotion_videos"
emotion_video_paths = [f"{emotion_videos_foler_path}/happy.mp4", 
                       f"{emotion_videos_foler_path}/sad.mp4", 
                       f"{emotion_videos_foler_path}/neutral.mp4"]

PORT = 1989
SERVER_ADDRESS = ("0.0.0.0", PORT)

ROBOT_NAME = "pixel"

BAUDRATE = 115200
PORT = "COM3"

RIGHT_HAND_PINS = (2, 3, 4)
LEFT_HAND_PINS = (5, 6, 7)
HEAD_PIN = 8

LEFT_MOTOR_PINS = (28, 30, 11)
RIGHT_MOTOR_PINS = (40, 42, 13)
BACK_MOTOR_PINS = (34, 36, 12)
FRONT_MOTOR_PINS = (24, 22, 10)

SHOWS = {"main": shows.main_show, 
         "square": shows.square_show,
         "showcase": shows.showcase}

mp_holistic = mp.solutions.holistic

def read_emotion_videos(paths: list) -> list:
    videos = []
    for path in paths:
        video = cv2.VideoCapture(path)
        videos.append(video)
    return videos


def main():
    videos = read_emotion_videos(emotion_video_paths)
    hands_manager = None
    motors_manager = None
    if len(sys.argv) < 2 or sys.argv[1] != "sim":
        board = ArduinoMega(PORT)
        hands_manager = RobotServosManager(board, RIGHT_HAND_PINS, LEFT_HAND_PINS, HEAD_PIN)
        motors_manager = RobotMotorsManager(board, 
                                            LEFT_MOTOR_PINS, 
                                            RIGHT_MOTOR_PINS, 
                                            BACK_MOTOR_PINS, 
                                            FRONT_MOTOR_PINS)
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        pixel = Robot(
            holistic=holistic,
            motors_manager=motors_manager, 
            hands_manager=hands_manager, 
            name=ROBOT_NAME
        )

        pixel.load_shows(SHOWS)
        
        controller = RobotController(pixel, cap, SERVER_ADDRESS)
        controller.start()
            
    cap.release()

if __name__ == "__main__":
    main()