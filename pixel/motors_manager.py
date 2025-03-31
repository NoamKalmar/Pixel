from pyfirmata import Arduino, ArduinoMega, PWM, OUTPUT
import time

class MotorsManager:
    def __init__(self, arduino: Arduino | ArduinoMega, pins: list):
        self.arduino = arduino
        self.pins = pins
        self.init_motors()

    def init_motors(self):
        for pins in self.pins:
            self.arduino.digital[pins[0]].mode = OUTPUT
            self.arduino.digital[pins[1]].mode = OUTPUT
            if len(pins) > 2:
                self.arduino.digital[pins[2]].mode = PWM

    def turn_motor(self, index: int, velocity: int = 255):
        velocity = max(min(velocity, 255), -255)
        pin1_value = 0 if velocity <= 0 else 1
        pin2_value = 0 if velocity >= 0 else 1
        self.arduino.digital[self.pins[index][0]].write(pin1_value)
        self.arduino.digital[self.pins[index][1]].write(pin2_value)
        if len(self.pins[index]) > 2:
            self.arduino.digital[self.pins[index][2]].write(abs(velocity) /  255)

    def turn_all_motors(self, velocity: int):
        for i in range(len(self.pins)):
            self.turn_motor(i, velocity)

    def stop_all_motors(self):
        self.turn_all_motors(0)

class RobotMotorsManager(MotorsManager):
    def __init__(
            self, 
            arduino: Arduino | ArduinoMega, 
            left_motor_pins: tuple,
            right_motor_pins: tuple,
            back_motor_pins: tuple, 
            front_motor_pins: tuple
        ):
        pins = [left_motor_pins, right_motor_pins, back_motor_pins, front_motor_pins]
        super().__init__(arduino, pins)
        self.status = 0 # 0 - Not moving, 1 - moving x, 2 - moving y
    
    def move_x(self, velocity: int = 255, stop_if_change: bool = False, stop_time: float = 1):
        self.turn_motor(0, 0)
        self.turn_motor(1, 0)
        if stop_if_change and self.status == 2:
            time.sleep(stop_time)
        self.turn_motor(2, velocity)
        self.turn_motor(3, velocity)
        self.status = 1

    def move_y(self, velocity: int = 255, stop_if_change: bool = False, stop_time: float = 1):
        self.turn_motor(2, 0)
        self.turn_motor(3, 0)
        if stop_if_change and self.status == 1:
            time.sleep(stop_time)
        self.turn_motor(0, velocity)
        self.turn_motor(1, velocity)
        self.status = 2
        
    def stop_moving(self):
        self.status = 0
        self.stop_all_motors()

    def turn(self, velocity: int = 255):
        self.turn_motor(0, velocity)
        self.turn_motor(1, -velocity)
        self.turn_motor(2, -velocity)
        self.turn_motor(3, velocity)

    def move_side(self, velocity: int = 255):
        self.move_x(velocity)
    
    def move_straight(self, velocity: int = 255):
        self.move_y(velocity)
    
    def turn_and_back(self, velocity: int = 200, turn_time: float = 1):
        self.turn(velocity)
        time.sleep(turn_time)
        self.turn(-velocity)
        time.sleep(turn_time)
        self.stop_moving()