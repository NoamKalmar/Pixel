import numpy as np
import math

def get_points(landmarks: list, landmarks_numbers: list) -> list:
        points = []
        for landmark_number in landmarks_numbers:
            point = {"x": landmarks[landmark_number].x, 
                     "y": landmarks[landmark_number].y, 
                     "z": landmarks[landmark_number].z}
            points.append(point)
        return points

def vectors_angle(points):
    a = points[0]
    b = points[1]
    c = points[2]
    first_vector = np.array([b["x"] - a["x"], b["y"] - a["y"], b["z"] - a["z"]])
    second_vector = np.array([c["x"] - a["x"], c["y"] - a["y"], c["z"] - a["z"]])
    vectors_dot_product = np.dot(first_vector, second_vector)
    first_distance = math.sqrt((b["x"] - a["x"]) ** 2 + (b["y"] - a["y"]) ** 2 + (b["z"] - a["z"]) ** 2)
    second_distance = math.sqrt((c["x"] - a["x"]) ** 2 + (c["y"] - a["y"]) ** 2 + (c["z"] - a["z"]) ** 2)
    cosine = vectors_dot_product / first_distance / second_distance
    angle = math.degrees(math.acos(cosine))
    return angle