from pyfirmata import Arduino

class MotorsManager:
    def __init__(self, arduino: Arduino, pins: list):
        self.arduino = arduino
        self.pins = pins

    def turn_motor_by_index(self, index: int, velocity: int = 255):
        velocity = max(min(velocity, 255), -255)
        pin1_value = 0 if velocity < 0 else 1
        pin2_value = 0 if velocity > 0 else 1
        self.arduino.digital[self.pins[index][0]].write(pin1_value)
        self.arduino.digital[self.pins[index][1]].write(pin2_value)
        self.arduino.digital[self.pins[index][2]].write(abs(velocity) /  255)

    def turn_all_motors(self, velocity: int):
        for i in range(len(self.pins)):
            self.turn_motor_by_index(i, velocity)