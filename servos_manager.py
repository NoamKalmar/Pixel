from pyfirmata import Arduino, ArduinoMega, SERVO

class ServosManager:
    def __init__(self, arduino: Arduino | ArduinoMega, pins: list, start_value: int = 0, default_values: dict = None):
        self.pins = pins
        self.arduino = arduino
        self.start_value = start_value
        self.default_values = default_values
        self.init_servos()

    def init_servos(self) -> None:
        for pin in self.pins:
            self.arduino.digital[pin].mode = SERVO
            self.arduino.digital[pin].write(self.start_value)
    
    def write_all(self, values: list) -> None:
        for i, pin in enumerate(self.pins):
            if values[i] is None:
                continue
            self.arduino.digital[pin].write(values[i])
    
    def write_by_index(self, index: int, value: int) -> None:
        self.arduino.digital[self.pins[index]].write(value)

    def write_default_values(self) -> None:
        self.write_all(self.default_values)

class RobotServosManager(ServosManager):
    def __init__(self, 
                 arduino: Arduino | ArduinoMega, 
                 right_hand_pins: tuple,
                 left_hand_pins: tuple,
                 head_pin: tuple
                 ):
        super().__init__(arduino, right_hand_pins + left_hand_pins + (head_pin,), 90)