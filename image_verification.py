import numpy as np
import cv2

BLACK = (0, 0, 0)

def cover_image(image: np.ndarray, boxes: list):
    modified_image = image.copy()
    for box in boxes:
        modified_image = cv2.rectangle(modified_image, box[0], box[1], BLACK, -1)

    return modified_image