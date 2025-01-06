import math
import numpy as np
import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic
mp_face_mesh = mp.solutions.face_mesh


def check_landmark(landmark):
    try:
        checked_landmark = landmark.landmark
    except:
        checked_landmark = None
    return checked_landmark

def holistic_detect(holistic, image):
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = holistic.process(image)
    
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  
    mp_drawing.draw_landmarks(
        image=image, 
        landmark_list=results.face_landmarks, 
        connections=mp_holistic.FACEMESH_CONTOURS, 
        landmark_drawing_spec=None, 
        connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style())
    mp_drawing.draw_landmarks(
        image=image, 
        landmark_list=results.face_landmarks, 
        connections=mp_holistic.FACEMESH_TESSELATION, 
        landmark_drawing_spec=None, 
        connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())
    # mp_drawing.draw_landmarks(
    #       image=image,
    #       landmark_list=holistic_results.face_landmarks,
    #       connections=mp_face_mesh.FACEMESH_IRISES,
    #       landmark_drawing_spec=None,
    #       connection_drawing_spec=mp_drawing_styles
    #       .get_default_face_mesh_iris_connections_style())
    mp_drawing.draw_landmarks(
        image=image, 
        landmark_list=results.pose_landmarks, 
        connections=mp_holistic.POSE_CONNECTIONS, 
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
    mp_drawing.draw_landmarks(
        image=image, 
        landmark_list=results.right_hand_landmarks, 
        connections=mp_holistic.HAND_CONNECTIONS, 
        landmark_drawing_spec=mp_drawing_styles.get_default_hand_landmarks_style())
    mp_drawing.draw_landmarks(
        image=image, 
        landmark_list=results.left_hand_landmarks, 
        connections=mp_holistic.HAND_CONNECTIONS, 
        landmark_drawing_spec=mp_drawing_styles.get_default_hand_landmarks_style())

    landmarks = {
            "pose": check_landmark(results.pose_landmarks), 
            "face": check_landmark(results.face_landmarks),
            "right_hand": check_landmark(results.right_hand_landmarks), 
            "left_hand": check_landmark(results.left_hand_landmarks)}
    
    return landmarks, image

def face_detect(face_detection, image):
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_detection.process(image)

    image.flags.writeable = True
    if results.detections:
        for detection in results.detections:
            mp_drawing.draw_detection(image, detection)

    return results.detections, image