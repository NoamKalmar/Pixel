from pyfirmata import Arduino, ArduinoMega, SERVO
import time
import threading
from dataclasses import dataclass, field
from collections.abc import Iterable
from typing import Optional

PROGRESS_THRESHOLD = 0.5

@dataclass
class Servo:
    pin: int
    current_angle: int = 0
    is_moving: bool = False
    should_stop_moving: bool = False
    is_mirrored: bool = False
    last_progress: float = field(default_factory=time.time)
    stop_moving_event: threading.Event = field(default_factory=threading.Event) # Needed for thread synchronization
    movement_thread: Optional[threading.Thread] = None


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

    def write_servo(self, index: int, angle: int, part_of_move: bool = False) -> None:
        if not part_of_move:
            self.stop_moving(index)
        angle = max(min(angle, 180), 0) # Keep angle between 0 and 180
        writing_angle = angle
        if self.servos[index].is_mirrored:
            writing_angle = 180 - writing_angle
        self.arduino.digital[self.servos[index].pin].write(writing_angle)
        self.servos[index].current_angle = angle

    def write_all(self, angle: int) -> None:
        for i in range(len(self.servos)):
            self.write_servo(i, angle)

    def write_default(self) -> None:
        self.write_all(self.default_angle)

    def play_sequence(self, index: int, sequence: Iterable, rate: float = 0.01) -> None:
        if rate > PROGRESS_THRESHOLD - 0.1:
            rate = PROGRESS_THRESHOLD - 0.1
        self.stop_moving(index)
        self.servos[index].is_moving = True
        movement_thread = threading.Thread(target=self._play_sequence, args=(index, sequence, rate))
        self.servos[index].movement_thread = movement_thread
        movement_thread.start()

    def _play_sequence(self, index: int, sequence: Iterable, rate: float = 0.01) -> None:
        self.servos[index].stop_moving_event.clear()
        try:
            for angle in sequence:
                if self.servos[index].should_stop_moving:
                    break
                self.write_servo(index, angle, True)
                self.servos[index].last_progress = time.time()
                time.sleep(rate)
        finally:
            self.servos[index].is_moving = False
            self.servos[index].stop_moving_event.set()
            self.servos[index].movement_thread = None
    
    def move_servo(self, index: int, target_angle: int, rate: int = 0.01, step: int = 1):
        current_angle = self.servos[index].current_angle
        step = step if target_angle > current_angle else -step
        sequence = range(self.servos[index].current_angle, target_angle + 1, step)
        self.play_sequence(index, sequence, rate)

    def stop_moving(self, index: int) -> None:
        if not self.servos[index].is_moving:
            return
        self.servos[index].should_stop_moving = True
        while self.servos[index].is_moving:
            if self._check_fix_move:
                break
            self.servos[index].stop_moving_event.wait(0.1) # Wait until the moving thread got the message and stopped
        if self.servos[index].movement_thread is not None:
            self.servos[index].movement_thread.join()
            self.servos[index].movement_thread = None
        self.servos[index].should_stop_moving = False
    
    def wait_while_moving(self) -> None:
        for i, servo in enumerate(self.servos):
            while servo.is_moving:
                if self._check_fix_move(i):
                    break
                servo.stop_moving_event.wait(0.1)

    def _check_fix_move(self, index: int) -> bool:
        if time.time() - self.servos[index].last_progress > PROGRESS_THRESHOLD:
            self.servos[index].is_moving = False
            self.servos[index].stop_moving_event.set()
            return True
        return False

class RobotServosManager(ServosManager):
    def __init__(self, 
                 arduino: Arduino | ArduinoMega, 
                 right_hand_pins: tuple,
                 left_hand_pins: tuple,
                 head_pin: tuple
                 ):
        super().__init__(arduino, right_hand_pins + left_hand_pins + (head_pin,), 90)
        self.servos[3].is_mirrored = True
        self.servos[5].is_mirrored = True

    def set_right_hand(self, angle1: int, angle2: int, angle3: int) -> None:
        self.write_servo(0, angle1)
        self.write_servo(1, angle2)
        self.write_servo(2, angle3)

    def set_left_hand(self, angle1: int, angle2: int, angle3: int) -> None:
        self.write_servo(3, angle1)
        self.write_servo(4, angle2)
        self.write_servo(5, angle3)

    def set_hands(self, angle1: int, angle2: int, angle3: int) -> None:
        self.set_right_hand(angle1, angle2, angle3)
        self.set_left_hand(angle1, angle2, angle3)
    
    def set_head(self, angle: int) -> None:
        self.write_servo(6, angle)
        
    def move_right_hand(self, angle1: int, angle2: int, angle3: int, rate: float = 0.01) -> None:
        self.move_servo(0, angle1, rate)
        self.move_servo(1, angle2, rate)
        self.move_servo(2, angle3, rate)

    def move_left_hand(self, angle1: int, angle2: int, angle3: int, rate: float = 0.01) -> None:
        self.move_servo(3, angle1, rate)
        self.move_servo(4, angle2, rate)
        self.move_servo(5, angle3, rate)

    def move_hands(self, angle1: int, angle2: int, angle3: int, rate: float = 0.01) -> None:
        self.move_right_hand(angle1, angle2, angle3, rate)
        self.move_left_hand(angle1, angle2, angle3, rate)

    def move_head(self, angle: int, rate: float = 0.02):
        self.move_servo(6, angle, rate)