from pyfirmata import Arduino, PWM

class MotorsManager:
    def __init__(self, arduino: Arduino, pins: list):
        self.arduino = arduino
        self.pins = pins
        self.init_motors()

    def init_motors(self):
        for pins in self.pins:
            if len(pins) > 2:
                self.arduino.digital[pins[2]].mode = PWM

    def turn_motor_by_index(self, index: int, velocity: int = 255):
        velocity = max(min(velocity, 255), -255)
        pin1_value = 0 if velocity < 0 else 1
        pin2_value = 0 if velocity > 0 else 1
        self.arduino.digital[self.pins[index][0]].write(pin1_value)
        self.arduino.digital[self.pins[index][1]].write(pin2_value)
        if len(self.pins[index]) > 2:
            self.arduino.digital[self.pins[index][2]].write(abs(velocity) /  255)

    def turn_all_motors(self, velocity: int):
        for i in range(len(self.pins)):
            self.turn_motor_by_index(i, velocity)

    def stop_all_motors(self):
        self.turn_all_motors(0)

class RobotMotorsManager(MotorsManager):
    def __init__(
            self, 
            arduino: Arduino, 
            left_motor_pins: tuple,
            right_motor_pins: tuple,
            back_motor_pins: tuple, 
            front_motor_pins: tuple
        ):
        pins = [left_motor_pins, right_motor_pins, back_motor_pins, front_motor_pins]
        super().__init__(arduino, pins)

    def move_straight(self, velocity: int = 255):
        self.turn_motor_by_index(0, velocity)
        self.turn_motor_by_index(1, velocity)
        self.turn_motor_by_index(2, 0)
        self.turn_motor_by_index(3, 0)

    def move_side(self, velocity: int = 255):
        self.turn_motor_by_index(0, 0)
        self.turn_motor_by_index(1, 0)
        self.turn_motor_by_index(2, velocity)
        self.turn_motor_by_index(3, velocity)

    def stop_moving(self):
        self.turn_motor_by_index(0, 0)
        self.turn_motor_by_index(1, 0)
        self.turn_motor_by_index(2, 0)
        self.turn_motor_by_index(3, 0)

    def turn(self, velocity: int = 255):
        self.turn_motor_by_index(0, velocity)
        self.turn_motor_by_index(1, -velocity)
        self.turn_motor_by_index(2, -velocity)
        self.turn_motor_by_index(3, velocity)