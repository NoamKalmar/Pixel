from pyfirmata import Pin, Board, util

class MPU_z:
    def __init__(self, board: Board):
        self.board = board
        self.pin: Pin = board.get_pin("a:13:i")

    def init(self, start_iterator: bool) -> None:
        self.pin.enable_reporting()
        if start_iterator:
            self.iterator = util.Iterator(self.board)
            self.iterator.start()

    def get_angle(self) -> int | None:
        value = self.pin.read()
        if value is None:
            return None
        return round(self.pin.read() * 1023)