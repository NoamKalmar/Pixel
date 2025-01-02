import cv2
import mediapipe as mp
from pyfirmata import Arduino

import detect_landmarks
from servos_manager import ServosManager
from robot import Robot

WIDTH, HEIGHT = 600, 600

emotion_videos_foler_path = "emotion_videos"
emotion_video_paths = [f"{emotion_videos_foler_path}/happy.mp4", 
                       f"{emotion_videos_foler_path}/sad.mp4", 
                       f"{emotion_videos_foler_path}/neutral.mp4"]

PORT = "COM13"
BAUDRATE = 115200
# board = Arduino(PORT)
hands_pins = [i for i in range(7)]

mp_holistic = mp.solutions.holistic
mp_face_mesh = mp.solutions.face_mesh
mp_face_detection = mp.solutions.face_detection

def read_emotion_videos(paths):
    videos = []
    for path in paths:
        video = cv2.VideoCapture(path)
        videos.append(video)
    return videos

def main():
    videos = read_emotion_videos(emotion_video_paths)
    cap = cv2.VideoCapture(0)
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
            # hands_manager = ServosManager(hands_pins, arduino, 0)
            pixel = Robot(holistic=holistic, face_detection=face_detection, arduino=None, name="Pixel")

            while cap.isOpened():
                key = cv2.waitKey(5)
                if key == ord("q"):
                    break
                success, image = cap.read()
                if not success:
                    print("Empty camera frame")
                    continue
                    
                success = pixel.loop(image)
                if success[0] == 1:
                    print(success[1])
                    continue
                elif success[0] == 2:
                    print(success[1])
                    break
            
    cap.release()

if __name__ == "__main__":
    main()