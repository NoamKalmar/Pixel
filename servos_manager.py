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

    def set_right_hand(self, angle1: int, angle2: int, angle3: int) -> None:
        self.write_by_index(0, angle1)
        self.write_by_index(1, angle2)
        self.write_by_index(2, angle3)

    def set_left_hand(self, angle1: int, angle2: int, angle3: int) -> None:
        self.write_by_index(3, angle1)
        self.write_by_index(4, angle2)
        self.write_by_index(5, angle3)

    def set_hands(self, angle1: int, angle2: int, angle3: int, mirror: bool = True) -> None:
        self.set_right_hand(angle1, angle2, angle3)
        if mirror:
            self.set_left_hand(180 - angle1, angle2, 180 - angle3)
        else:
            self.set_left_hand(angle1, angle2, angle3)
            
    
    def set_angle(self, angle: int) -> None:
        self.write_by_index(6, angle)