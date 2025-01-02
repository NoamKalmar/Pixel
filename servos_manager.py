from pyfirmata import Arduino, SERVO

class ServosManager():
    def __init__(self, pins, arduino: Arduino = None, start_value: int = 0, default_values: dict = None):
        self.pins = pins
        self.arduino = arduino
        self.start_value = start_value
        self.default_values = default_values
        self.init_servos()

    def init_servos(self):
        for pin in self.pins:
            self.arduino.digital[pin].mode = SERVO
            self.arduino.digital[pin].write(self.default_value)
    
    def write_all(self, values: list):
        for i, pin in enumerate(self.pins):
            if values[i] is None:
                continue
            self.arduino.digital[pin].write(values[i])
    
    def write_by_pin(self, pin, value: int):
        self.arduino.digital[pin].write(value)

    def write_by_pins(self, pins_values: dict):
        for pin in pins_values:
            if not pin in self.pins:
                print(f"{pin} is not in this Servos Manger's initalized pins")
                return -1
            self.arduino.digital[pin] = pins_values[pin]

    def write_default_values(self):
        self.write_all(self.default_values)