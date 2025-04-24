import pandas as pd
import math
from landmarks import detect_landmarks

def save_face_landmarks(holistic, videos: list, y_column: str, path: str, landmarks_num: int=1404) -> None:
    face_data = []
    frame_number = 0
    for i, video in enumerate(videos):
        print(f"Current video index: {i}")
        while video.isOpened():
            ret, frame = video.read()
            frame_number += 1
            if frame == None:
                break
            landmarks, modified_image = detect_landmarks.holistic_detect(holistic, frame)
            if not landmarks["face"]:
                continue
            frame_data = [i]
            frame_data = frame_data + landmarks_to_list(landmarks["face"])
            face_data.append(frame_data)
            if frame_number % 100 == 0:
                print(frame_number)
    
    face_landmark_columns = [y_column]
    for i in range(landmarks_num):
        if i % 3 == 0:
            face_landmark_columns.append(f"{math.floor(i / 3)}_x")
        elif i % 3 == 1:
            face_landmark_columns.append(f"{math.floor(i / 3)}_y")
        else:
            face_landmark_columns.append(f"{math.floor(i / 3)}_z")
    df = pd.DataFrame(data=face_data, columns=face_landmark_columns)
    df.to_csv(path)

def landmarks_to_list(landmarks, relative_landmark=5) -> list:
    landmarks_list = []
    for landmark in landmarks:
        landmarks_list.append(landmark.x - landmarks[relative_landmark].x)
        landmarks_list.append(landmark.y - landmarks[relative_landmark].y)
        landmarks_list.append(landmark.z - landmarks[relative_landmark].z)
    return landmarks_list