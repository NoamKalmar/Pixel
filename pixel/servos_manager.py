from pyfirmata import Arduino, ArduinoMega, SERVO
import time
import threading

class ServosManager:
    def __init__(self, arduino: Arduino | ArduinoMega, pins: list, start_angle: int = 0, default_angles: dict = None):
        self.pins = pins
        self.arduino = arduino
        self.start_angle = start_angle
        self.default_angles = default_angles
        self.current_angles = [start_angle for _ in range(len(self.pins))]
        self.is_moving = [False for _ in range(len(self.pins))]
        self.should_stop_moving = [False for _ in range(len(self.pins))]
        self.init_servos()

    def init_servos(self) -> None:
        for i, pin in enumerate(self.pins):
            self.arduino.digital[pin].mode = SERVO
            self.write_servo(i, self.start_angle)
    
    def write_all(self, angle: list) -> None:
        for i in range(self.pins):
            if angle[i] is None:
                continue
            self.write_servo(i, angle)
    
    def write_servo(self, index: int, angle: int, part_of_move: bool = False) -> None:
        if not part_of_move:
            self.stop_moving(index)
        angle = max(min(angle, 180), 0) # Keep angle between 0 and 180
        self.arduino.digital[self.pins[index]].write(angle)
        self.current_angles[index] = angle

    def write_default(self) -> None:
        self.write_all(self.default_values)

    def move_servo(self, index: int, target_value: int, rate: float = 0.01) -> None:
        moving_thread = threading.Thread(target=self._move_servo, args=(index, target_value, rate))
        moving_thread.start()

    def _move_servo(self, index: int, target_angle: int, rate: float = 0.01) -> None:
        self.stop_moving(index)
        start_angle = self.current_angles[index]
        step = 1 if target_angle > start_angle else -1
        self.is_moving[index] = True
        for angle in range(self.current_angles[index], target_angle + 1, step):
            if self.should_stop_moving[index]:
                break
            self.write_servo(index, angle, True)
            time.sleep(rate)
        self.is_moving[index] = False

    def stop_moving(self, index: int) -> None:
        if not self.is_moving[index]:
            return
        self.should_stop_moving[index] = True
        while self.is_moving[index]: pass # Wait until the moving thread got the message and stopped
        self.should_stop_moving[index] = False

class RobotServosManager(ServosManager):
    def __init__(self, 
                 arduino: Arduino | ArduinoMega, 
                 right_hand_pins: tuple,
                 left_hand_pins: tuple,
                 head_pin: tuple
                 ):
        super().__init__(arduino, right_hand_pins + left_hand_pins + (head_pin,), 90)

    def set_right_hand(self, angle1: int, angle2: int, angle3: int) -> None:
        self.write_servo(0, angle1)
        self.write_servo(1, angle2)
        self.write_servo(2, angle3)

    def set_left_hand(self, angle1: int, angle2: int, angle3: int, mirror: bool = True) -> None:
        if mirror:
            angle1 = 180 - angle1
            angle3 = 180 - angle3
        self.write_servo(3, angle1)
        self.write_servo(4, angle2)
        self.write_servo(5, angle3)
    

    def set_hands(self, angle1: int, angle2: int, angle3: int, mirror: bool = True) -> None:
        self.set_right_hand(angle1, angle2, angle3)
        self.set_left_hand(angle1, angle2, angle3, mirror)
    
    def set_head(self, angle: int) -> None:
        self.write_servo(6, angle)
        
    def move_right_hand(self, angle1: int, angle2: int, angle3: int, rate: float = 0.01) -> None:
        self.move_servo(0, angle1, rate)
        self.move_servo(1, angle2, rate)
        self.move_servo(2, angle3, rate)

    def move_left_hand(self, angle1: int, angle2: int, angle3: int, rate: float = 0.01, mirror: bool = True) -> None:
        if mirror:
            angle1 = 180 - angle1
            angle3 = 180 - angle3
        self.move_servo(3, angle1, rate)
        self.move_servo(4, angle2, rate)
        self.move_servo(5, angle3, rate)

    def move_head(self, angle: int, rate: float = 0.01):
        self.move_servo(6, angle, rate)