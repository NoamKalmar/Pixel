import numpy as np
import cv2
import math
import numpy as np
from collections import defaultdict
from collections.abc import Callable

import detect_landmarks
from servos_manager import ServosManager
from motors_manager import RobotMotorsManager
import pose_landmarks

class Robot:
    def __init__(
            self, 
            holistic,
            hands_manager: ServosManager=None,
            motors_manager: RobotMotorsManager=None,
            name="Robot"
    ):
        self.holistic = holistic
        self.name = name
        self.hands_manager = hands_manager
        self.motors_manager = motors_manager
        self.head_angle = 90
        self.angles = [[] for i in range(7)]
        self.unwanted_boxes = []
        self.landmarks = {}
        self.human_x = None
        self.human_y = None
        self.human_z = None
        self.human_found = False
        self.shows = defaultdict(dict) # {name: {"steps": [show_step0, show_step1, ...], "current_step": current_step}}
        
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

    def move_human_x(self, stop=False, max_right: float = 0.3, max_left: float = 0.7, velocity: int = 255):
        if self.human_x > max_left:
            self.motors_manager.move_side(-velocity)
        elif self.human_x < max_right:
            self.motors_manager.move_side(velocity)
        else:
            if stop:
                self.motors_manager.stop_all_motors()
            return 1
        return 0

    def move_human_z(self, stop=False, too_close: float = -1, too_far: float = -0.5, velocity: int = 255):
        if self.human_z > too_far:
            self.motors_manager.move_straight(velocity)
        elif self.human_z < too_close:
            self.motors_manager.move_straight(-velocity)
        else:
            if stop:
                self.motors_manager.stop_all_motors()
            return 1
        return 0
    
    def follow_human(self):
        finished_x = self.move_human_x()
        if not finished_x:
            return
        finished_z = self.move_human_z()
        if not finished_z:
            return
        self.motors_manager.stop_all_motors()
    
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
        c2["z"] += 0.6
        
        d2 = {"x": a2["x"], "y": a2["y"] - 0.1, "z": a2["z"]}
        e2 = {"x": a2["x"] + 0.1, "y": a2["y"], "z": a2["z"]}

        angle1 = 180 - pose_landmarks.vectors_angle([a1, b1, e1])
        angle1 = (angle1 - 60) * 3
        angle2 = 180 - pose_landmarks.vectors_angle([a1, b1, d1])
        angle3 = 180 - pose_landmarks.vectors_angle([b1, a1, c1])

        angle4 = pose_landmarks.vectors_angle([a2, b2, e2])
        angle4 = (angle4 - 60) * 3
        angle5 = 180 - pose_landmarks.vectors_angle([a2, b2, d2])
        angle6 = pose_landmarks.vectors_angle([b2, a2, c2])

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
            if angle < 0:
                angle = 0
            elif angle > 180:
                angle = 180
            self.angles[i].append(angle)
            self.angles[i] = self.angles[i][-average_of:]
            average_angle = sum(self.angles[i]) / len(self.angles[i])
            self.hands_manager.write_by_index(i, round(average_angle))

    def load_shows(self, shows: dict[str, Callable]) -> None:
        for show_name, show_function in shows.items():
            show_steps = show_function()
            self.shows[show_name]["steps"] = show_steps
            self.shows[show_name]["current_step"] = -1

    def shows_loop(self) -> None:
        for show in self.shows.values():
            show_steps, current_step = show.values()
            if current_step == -1:
                continue
            show["current_step"] = show_steps[current_step](self)

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