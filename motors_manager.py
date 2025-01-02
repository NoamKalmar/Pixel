from pyfirmata import Arduino

class MotorsManager:
    def __init__(self, arduino: Arduino, pins: list):
        self.arduino = arduino
        self.pins = pins

    def turn_motor_by_pin(self, pin: int, forward: bool):
        if forward:
            self.arduino.digital[pin[0]].write(1)
            self.arduino.digital[pin[1]].write(0)
        else:
            self.arduino.digital[pin[0]].write(0)
            self.arduino.digital[pin[1]].write(1)

    def stop_motor_by_pin(self, pin: int):
        self.arduino.digital[pin[0]].write(0)
        self.arduino.digital[pin[1]].write(0)

    def turn_all_motors(self, forward: bool):
        for pin in self.pins:
            self.turn_motor_by_pin(pin, forward)

    def stop_all_motors(self):
        for pin in self.pins:
            self.stop_motor_by_pin(pin)