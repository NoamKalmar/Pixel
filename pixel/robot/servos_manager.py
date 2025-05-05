from pyfirmata import Arduino, ArduinoMega, SERVO
import time
import threading
from dataclasses import dataclass, field
from collections.abc import Iterable
from typing import Optional
import glob
import json
from itertools import zip_longest

@dataclass
class Servo:
    pin: int
    current_angle: int = 0
    is_mirrored: bool = False


class ServosManager:
    def __init__(self, arduino: Arduino | ArduinoMega, pins: tuple, default_angle: int = 0):
        self.servos: list[Servo] = []
        self.arduino = arduino
        self.default_angle = default_angle
        self.init_servos(pins)

    def init_servos(self, pins: tuple) -> None:
        for i, pin in enumerate(pins):
            servo = Servo(pin, self.default_angle)
            self.servos.append(servo)
            self.arduino.digital[pin].mode = SERVO
            self.write_servo(i, self.default_angle)

    def write_servo(self, index: int, angle: int) -> None:
        angle = max(min(angle, 180), 0) # Keep angle between 0 and 180
        writing_angle = angle
        if self.servos[index].is_mirrored:
            writing_angle = 180 - writing_angle
        self.arduino.digital[self.servos[index].pin].write(writing_angle)
        self.servos[index].current_angle = angle

    def write_servos(self, indexes: list[int], angles: tuple[int]):
        for index, angle in zip(indexes, angles):
            self.write_servo(index, angle)

    def write_all(self, angle: int) -> None:
        for i in range(len(self.servos)):
            self.write_servo(i, angle)

    def write_default(self) -> None:
        self.write_all(self.default_angle)

    def play_sequences(self, indexes: tuple[int], sequences: tuple[Iterable], rate: float = 0.01) -> None:
        for sequence in zip_longest(*sequences):
            for i, servo_index in enumerate(indexes):
                angle = sequence[i]
                if sequence[i] is None:
                    continue
                self.write_servo(servo_index, angle)
            time.sleep(rate)
    
    def move_servos(self, index_to_angle: dict[int, int], rate: int = 0.01, step: int = 1) -> None:
        sequences = []
        for index, angle in index_to_angle.items():
            current_angle = self.servos[index].current_angle
            sequence_step = step if angle > current_angle else -step
            to_angle = angle + 1 if sequence_step > 0 else angle -1
            sequence = range(current_angle, to_angle, sequence_step)
            sequences.append(sequence)
        self.play_sequences(index_to_angle.keys(), sequences, rate)

class RobotServosManager(ServosManager):
    RIGHT_HAND_INDEXES = (0, 1, 2)
    LEFT_HAND_INDEXES = (3, 4, 5)
    HEAD_INDEX = 6
    def __init__(self, 
                 arduino: Arduino | ArduinoMega, 
                 right_hand_pins: tuple,
                 left_hand_pins: tuple,
                 head_pin: tuple
                 ):
        super().__init__(arduino, right_hand_pins + left_hand_pins + (head_pin,), 90)
        self.servos[3].is_mirrored = True
        self.servos[5].is_mirrored = True
        self.gestures = {}

    def set_right_hand(self, angles: tuple[int]) -> None:
        self.write_servos(self.RIGHT_HAND_INDEXES, angles)

    def set_left_hand(self, angles: tuple[int]) -> None:
        self.write_servos(self.LEFT_HAND_INDEXES, angles)

    def set_hands(self, angles: tuple[int]) -> None:
        self.set_right_hand(angles)
        self.set_left_hand(angles)
    
    def set_head(self, angle: int) -> None:
        self.write_servo(self.HEAD_INDEX, angle)
        
    def move_right_hand(self, angles: tuple[int], rate: float = 0.01) -> None:
        self.move_servos(dict(zip(self.RIGHT_HAND_INDEXES, angles)), rate)

    def move_left_hand(self, angles: tuple[int], rate: float = 0.01) -> None:
        self.move_servos(dict(zip(self.LEFT_HAND_INDEXES, angles)), rate)
    
    def move_hands(self, right_angles: tuple[int], left_angles: tuple[int], rate: float = 0.01) -> None:
        self.move_servos(dict(zip(self.RIGHT_HAND_INDEXES + self.LEFT_HAND_INDEXES, right_angles + left_angles)), rate)

    def move_hands_same(self, angles: tuple[int], rate: float = 0.01) -> None:
        self.move_hands(angles, angles, rate)

    def move_head(self, angle: int, rate: float = 0.02) -> None:
        self.move_servos({self.HEAD_INDEX: angle}, rate)

    def load_gestures(self, gestures_folder_path: str) -> None:
        gesture_file_paths = glob.glob(f"{gestures_folder_path}/*.json")
        for file_path in gesture_file_paths:
            # convert {gestures_folder_path}/*.json to just the *
            gesture_name = file_path.split("\\")[-1].split(".")[0]
            with open(file_path) as file:
                gesture = json.load(file)
                self.gestures[gesture_name] = gesture
    
    def play_right_gesture(self, name: str) -> None:
        gesture = self.gestures[name]
        self.play_sequence(0, gesture["angle1"], gesture["rate"])
        self.play_sequence(1, gesture["angle2"], gesture["rate"])
        self.play_sequence(2, gesture["angle3"], gesture["rate"])
        
    def play_left_gesture(self, name: str) -> None:
        gesture = self.gestures[name]
        self.play_sequence(3, gesture["angle1"], gesture["rate"])
        self.play_sequence(4, gesture["angle2"], gesture["rate"])
        self.play_sequence(5, gesture["angle3"], gesture["rate"])
    
    def play_hands_gesture(self, name: str) -> None:
        self.play_right_gesture(name)
        self.play_left_gesture(name)
    
    def switch_move(self, angles1: tuple[int], angles2: tuple[int], rate: float = 0.01) -> None:
        self.move_hands(angles1, angles2, rate)
        self.move_hands(angles2, angles1, rate)

    def move_right_path(self, angles_path: tuple[tuple[int]], rate=0.01) -> None:
        for angles in angles_path:
            self.move_right_hand(angles, rate)
    
    def move_left_path(self, angles_path: tuple[tuple[int]], rate=0.01) -> None:
        for angles in angles_path:
            self.move_left_hand(angles, rate)