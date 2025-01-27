import cv2
import time
import mediapipe as mp
from pyfirmata import Arduino

import detect_landmarks
from servos_manager import ServosManager
from motors_manager import RobotMotorsManager
from robot import Robot
import shows

WIDTH, HEIGHT = 600, 600

emotion_videos_foler_path = "emotion_videos"
emotion_video_paths = [f"{emotion_videos_foler_path}/happy.mp4", 
                       f"{emotion_videos_foler_path}/sad.mp4", 
                       f"{emotion_videos_foler_path}/neutral.mp4"]

BAUDRATE = 115200
PORT = "COM7"
board = Arduino(PORT)
HANDS_PINS = [i for i in range(7)]
LEFT_MOTOR_PINS = (8, 9)
RIGHT_MOTOR_PINS = (6, 7)
BACK_MOTOR_PINS = (3, 2)
FRONT_MOTOR_PINS = (4, 5)

mp_holistic = mp.solutions.holistic
mp_face_mesh = mp.solutions.face_mesh
mp_face_detection = mp.solutions.face_detection

def read_emotion_videos(paths: list) -> list:
    videos = []
    for path in paths:
        video = cv2.VideoCapture(path)
        videos.append(video)
    return videos


def main():
    print(1)
    videos = read_emotion_videos(emotion_video_paths)
    cap = cv2.VideoCapture(0)
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        print(2)
        with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
            print(3)
            # hands_manager = ServosManager(board, hand_pins, 0)
            motors_manager = RobotMotorsManager(board, 
                                                LEFT_MOTOR_PINS, 
                                                RIGHT_MOTOR_PINS, 
                                                BACK_MOTOR_PINS, 
                                                FRONT_MOTOR_PINS)
            print(4)
            pixel = Robot(holistic=holistic, face_detection=face_detection, arduino=board, motors_manager=motors_manager, name="Pixel")
            print(5)
            
            while cap.isOpened():
                print(6)
                key = cv2.waitKey(5)
                if key == ord("q"):
                    break
                success, image = cap.read()
                # shows.main_show(robot=pixel, frame=image)
                pixel.loop(image, True)
                # pixel.motors_manager.turn(255)
                shows.test(pixel)
            
    cap.release()


if __name__ == "__main__":
    main()