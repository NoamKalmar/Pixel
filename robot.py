import numpy as np
import cv2
from PIL import Image
import mediapipe as mp
# import face_recognition
import pandas as pd
from pyfirmata import Arduino, SERVO
import math
import numpy as np
import keras
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import pyttsx3
import speech_recognition as sr
import ollama
import time

import detect_landmarks
from servos_manager import ServosManager
from motors_manager import RobotMotorsManager
import pose_landmarks
import image_verification

BLACK = (0, 0, 0)

class Robot:
    def __init__(
            self, holistic, face_detection,
            arduino: Arduino=None,
            hands_manager: ServosManager=None,
            motors_manager: RobotMotorsManager=None,
            name="Robot"
    ):
        self.holistic = holistic
        self.face_detection = face_detection
        self.name = name
        self.arduino = arduino
        self.hands_manager = hands_manager
        self.motors_manager = motors_manager
        self.head_angle = 90
        self.angles = [i for i in range(7)]
        self.unwanted_boxes = []
        self.landmarks = {}
        self.human_x = None
        self.human_y = None
        self.human_z = None
        self.human_found = False
        
        # default_face_image = face_recognition.load_image_file("face.jpg")
        # self.default_face_encoing = face_recognition.face_encodings(default_face_image)[0]
        
    def loop(self, image: np.ndarray, display_frame: bool, max_distance: int = None) -> tuple:
        covered_image = image.copy()
        # covered_image = image_verification.cover_image(covered_image, self.unwanted_boxes)
        self.landmarks, modified_image = detect_landmarks.holistic_detect(self.holistic, covered_image)
        modified_image = cv2.flip(modified_image, 1)
        if display_frame:
            cv2.imshow(self.name, modified_image)
            
        if self.landmarks["pose"] is None:
            self.human_found = False
            return (0, None)
        self.human_found = True

        self.update_human_location()

        return (0, None)
    
    def update_human_location(self):
        self.human_x = self.landmarks["pose"][0].x
        self.human_y = self.landmarks["pose"][0].y
        self.human_z = self.landmarks["pose"][0].z

    def move_human_side(self, max_right: float = 0.3, max_left: float = 0.7, velocity: int = 255):
        if self.human_x > max_left:
            self.motors_manager.move_side(velocity)
        elif self.human_x < max_right:
            self.motors_manager.move_side(-velocity)
        else:
            return 1
        return 0

    def move_human_z(self, too_close: float = -1, too_far: float = -0.5, velocity: int = 255):
        if self.human_z > too_far:
            self.motors_manager.move_straight(velocity)
        elif self.human_z < too_close:
            self.motors_manager.move_straight(-velocity)
        else:
            return 1
        return 0
    
    def follow_human(self):
        if not self.human_found:
            self.motors_manager.turn(150)
            return
        finished_z = self.move_human_side()
        if finished_z:
            self.motors_manager.stop_all_motors()

    # def verify_face(self, image):
    #     img = image.copy()
    #     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #     im_pil = Image.fromarray(img)
    #     im_np = np.asarray(im_pil)
    #     img_encoding = face_recognition.face_encodings(im_np)
    #     results = face_recognition.compare_faces([self.default_face_encoing], img_encoding)
    #     face_indexes = [i for i, value in enumerate(results) if not value]
    #     face_locations = face_recognition.face_locations(img)
    #     print(face_locations[0])
    #     print(face_indexes)
    
    def calculate_distance(self, focal_length: int = 800) -> None:
        # left_shoulder = self.landmarks["pose"][11]
        # right_shoulder = self.landmarks["pose"][12]
        # shoulder_distance = np.sqrt(
        #     (left_shoulder.x - right_shoulder.x) ** 2 + 
        #     (left_shoulder.y - right_shoulder.y) ** 2 + 
        #     (left_shoulder.z - right_shoulder.z) ** 2
        # )
        # self.distance_to_human = focal_length / shoulder_distance
        self.distance_to_human = focal_length / -self.landmarks["pose"][0].z
        
    def get_human_box(self, image_shape: tuple):
        left_x = round((max(min(self.landmarks["pose"][12].x - 0.1, 1), 0)) * image_shape[1])
        right_x = round((max(min(self.landmarks["pose"][11].x + 0.1, 1), 0)) * image_shape[1])
        up_y = round(max(min(self.landmarks["pose"][1].y - 0.1, 1), 0) * image_shape[0])
        down_y = round(max(min(self.landmarks["pose"][30].y + 0.1, 1), 0) * image_shape[0])
        return (left_x, up_y), (right_x, down_y)

    def get_cropped_face(self, image: np.ndarray, detection) -> np.ndarray:
        x = max(math.floor((detection.location_data.relative_bounding_box.xmin - 0.1) * image.shape[1]), 0)
        y = max(math.floor((detection.location_data.relative_bounding_box.ymin - 0.1) * image.shape[0]), 0)
        width = min(math.floor((detection.location_data.relative_bounding_box.width + 0.2) * image.shape[1]), image.shape[1] - x)
        height = min(math.floor((detection.location_data.relative_bounding_box.height + 0.2) * image.shape[0]), image.shape[0] - y)
        modified_image = image.copy()
        modified_image = modified_image[y:y + height, x:x + width]
        return modified_image

    def calculate_angles(self) -> list:
        points = pose_landmarks.get_points([11, 13, 15, 12, 14, 16])
        a1 = points[0]
        b1 = points[1]
        c1 = points[2]
        c1["z"] += 0.2
        d1 = {"x": a1["x"], "y": a1["y"] - 0.1, "z": a1["z"]}
        e1 = {"x": a1["x"] - 0.1, "y": a1["y"], "z": a1["z"]}

        a2 = points[3]
        b2 = points[4]
        c2 = points[5]
        c2["z"] += 0.6
        
        d2 = {"x": a2["x"], "y": a2["y"] - 0.1, "z": a2["z"]}
        e2 = {"x": a2["x"] + 0.1, "y": a2["y"], "z": a2["z"]}

        angle1 = 180 - pose_landmarks.vectors_angle([a1, b1, e1])
        angle1 = (angle1 - 60) * 3
        angle2 = 180 - pose_landmarks.vectors_angle([a1, b1, d1])
        if angle2 > 120:
            angle2 = angle2 + ((angle2 - 120) * 3)
        angle3 = 180 - pose_landmarks.vectors_angle([b1, a1, c1]) + 30

        angle4 = pose_landmarks.vectors_angle([a2, b2, e2])
        angle4 = (angle4 - 60) * 3
        angle4 -= 70
        angle5 = pose_landmarks.vectors_angle([a2, b2, d2])
        if angle5 < 70:
            angle5 = angle5 - ((70 - angle5) * 3)
        angle6 = 180 - pose_landmarks.vectors_angle([b2, a2, c2])
        angle6 -= 45
        angle6 * 90 / 80
        angle6 = 90 - angle6

        if self.landmarks["pose"][0].x < 0.3:
            self.head_angle += 1
        elif self.landmarks["pose"][0].x > 0.7:
            self.head_angle -= 1

        return [angle1, angle2, angle3, angle4, angle5, angle6, self.head_angle]

    def mimic_movements(self, average_of: int=10) -> None:
        angles = self.calculate_angles()
        for i, angle in enumerate(angles):
            if angle < 1:
                angle = 1
            elif angle > 180:
                angle = 180
            self.angles[i].append(angle)
            self.angles[i] = self.angles[i][-average_of:]
            average_angle = sum(self.angles[i]) / len(self.angles[i])
            self.hands_manager.write_by_pin(i, average_angle)