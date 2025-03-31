import numpy as np
import cv2
import math
import numpy as np
from collections import defaultdict
from collections.abc import Callable
import threading
import json
import time

import detect_landmarks
from servos_manager import RobotServosManager
from motors_manager import RobotMotorsManager
import pose_landmarks
import emotion_recognition_model
import face_landmarks

class Robot:
    def __init__(
            self, 
            holistic,
            servos_manager: RobotServosManager | None,
            motors_manager: RobotMotorsManager | None,
            name="Robot"
    ):
        self.holistic = holistic
        self.name = name
        self.servos_manager = servos_manager
        self.motors_manager = motors_manager
        self.head_angle = 90
        self.angles = [[] for _ in range(7)]
        self.unwanted_boxes = []
        self.landmarks = {}
        self.human_x = None
        self.human_y = None
        self.human_z = None
        self.human_found = False
        self.shows = defaultdict(dict) # {"name": {"steps": [show_step0, show_step1, ...], "current_step": current_step, "data": {}}}
        self.emotion_recognition_model = emotion_recognition_model.load_model()
        self.emotion = None
        
    def loop(self, image: np.ndarray, display_frame: bool, max_distance: int = None) -> tuple:
        covered_image = image.copy()
        self.landmarks, modified_image = detect_landmarks.holistic_detect(self.holistic, covered_image)
        modified_image = cv2.flip(modified_image, 1)
        if display_frame:
            cv2.imshow(self.name, modified_image)

        self.shows_loop()
            
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

    def update_human_emotion(self):
        if not self.landmarks["face"]:
            return
        self.emotion = emotion_recognition_model.predict_emotion(
            self.emotion_recognition_model, face_landmarks.landmarks_to_list(self.landmarks["face"])
        )[0]

    def get_emotion(self) -> int:
        self.update_human_emotion()
        return self.emotion

    def move_human_x(self, stop=False, max_right: float = 0.2, max_left: float = 0.8, velocity: int = 255):
        if self.human_x > max_left:
            self.motors_manager.move_x(velocity, True)
        elif self.human_x < max_right:
            self.motors_manager.move_x(-velocity, True)
        else:
            if stop:
                self.motors_manager.stop_all_motors()
            return 1
        return 0

    def move_human_y(self, stop=False, too_close: float = -1, too_far: float = -0.5, velocity: int = 255):
        if self.human_z > too_far:
            self.motors_manager.move_y(velocity, True)
        elif self.human_z < too_close:
            self.motors_manager.move_y(-velocity, True)
        else:
            if stop:
                self.motors_manager.stop_all_motors()
            return 1
        return 0
    
    def follow_human(self) -> int:
        # if not self.human_found:
        #     self.motors_manager.turn(150)
        #     return 0
        finished_x = self.move_human_x()
        if not finished_x:
            return 1
        finished_z = self.move_human_y()
        if not finished_z:
            return 2
        self.motors_manager.stop_all_motors()
        return 3
    
    def calculate_distance(self, focal_length: int = 800) -> None:
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
        points = pose_landmarks.get_points(self.landmarks["pose"], [11, 13, 15, 12, 14, 16])
        a1 = points[0]
        b1 = points[1]
        c1 = points[2]
        c1["z"] += 0.2
        d1 = {"x": a1["x"], "y": a1["y"] - 0.1, "z": a1["z"]}
        e1 = {"x": a1["x"] - 0.1, "y": a1["y"], "z": a1["z"]}

        a2 = points[3]
        b2 = points[4]
        c2 = points[5]
        c2["z"] += 0.2
        
        d2 = {"x": a2["x"], "y": a2["y"] - 0.1, "z": a2["z"]}
        e2 = {"x": a2["x"] + 0.1, "y": a2["y"], "z": a2["z"]}

        angle1 = 180 - pose_landmarks.vectors_angle([a1, b1, e1])
        angle1 = (angle1 - 60) * 3
        angle2 = 180 - pose_landmarks.vectors_angle([a1, b1, d1])
        angle3 = 180 - pose_landmarks.vectors_angle([b1, a1, c1])

        angle4 = 180 - pose_landmarks.vectors_angle([a2, b2, e2])
        angle4 = (angle4 - 60) * 3
        angle5 = 180 - pose_landmarks.vectors_angle([a2, b2, d2])
        angle6 = 180 - pose_landmarks.vectors_angle([b2, a2, c2])

        if self.landmarks["pose"][0].x < 0.3:
            self.head_angle += 1
        elif self.landmarks["pose"][0].x > 0.7:
            self.head_angle -= 1

        return [angle1, angle2, angle3, angle4, angle5, angle6, self.head_angle]

    def mimic_movements(self, average_of: int=10) -> None:
        if not self.landmarks["pose"]:
            return
        angles = self.calculate_angles()
        for i, angle in enumerate(angles):
            self.angles[i].append(angle)
            self.angles[i] = self.angles[i][-average_of:]
            average_angle = sum(self.angles[i]) / len(self.angles[i])
            self.servos_manager.write_servo(i, round(average_angle))

    def record_gesture(self, name: str, gestures_folder: str, is_right_human_hand: bool = True, rate: int = 0.01) -> None:
        recording_thread = threading.Thread(target=self._record_gesture, args=(name, gestures_folder, is_right_human_hand, rate))
        recording_thread.start()

    def _record_gesture(self, name: str, gestures_folder: str, is_right_human_hand: bool = True, rate: int = 0.01) -> None:
        while not self.landmarks["face"] and self.emotion != 0:
            pass
        time.sleep(3)
        gesture = {"rate": rate, "angle1": [], "angle2": [], "angle3": []}
        while self.emotion != 0:
            self.update_human_emotion()
            angles = self.calculate_angles()
            # Work for both hands
            for i in range(3):
                gesture[f"angle{i + 1}"].append(angles[i] if is_right_human_hand else angles[i + 3])
            time.sleep(rate)
        with open(f"{gestures_folder}/{name}.json", "w") as file:
            json.dump(gesture, file)

    def load_shows(self, shows: dict[str, Callable]) -> None:
        for show_name, show_function in shows.items():
            show_steps = show_function()
            self.shows[show_name]["steps"] = show_steps
            self.shows[show_name]["current_step"] = -1
            self.shows[show_name]["data"] = defaultdict(int)

    def shows_loop(self) -> None:
        for show in self.shows.values():
            show_steps, current_step, _ = show.values()
            if current_step == -1:
                continue
            next_step = show_steps[current_step](self)
            if next_step is None:
                show["current_step"] += 1
            elif next_step == -2:
                return
            else:
                show["current_step"] = next_step

    def run_show(self, name: str) -> None:
        self.set_show_step(name, 0)

    def set_show_step(self, name: str, step: int) -> None:
        self.shows[name]["current_step"] = step

    def end_shows(self) -> None:
        for show_name in self.shows.keys():
            self.set_show_step(show_name, -1)

    def end_show(self, name: str) -> None:
        self.set_show_step(name, -1)

    def next_step(self, name: str) -> None:
        self.set_show_step(name, self.shows[name]["current_step"] + 1)

    def last_step(self, name: str) -> None:
        self.set_show_step(name, self.shows[name]["current_step"] - 1)