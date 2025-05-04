from pyfirmata import Pin, Board, util
from typing import Optional, Literal

class MPU_z:
    def __init__(self, board: Board):
        self.board = board
        self.pin: Pin = board.get_pin("a:13:i")

    def init(self, start_iterator: bool) -> None:
        self.pin.enable_reporting()
        if start_iterator:
            self.iterator = util.Iterator(self.board)
            self.iterator.start()

    def get_angle(self) -> Optional[int]:
        value = self.pin.read()
        if value is None:
            return None
        return round(self.pin.read() * 1023)

    def distance_to(self, target_angle: int) -> tuple[int, Literal["left", "right"]]:
        angle = self.get_angle()
        distance1 = (target_angle - angle) % 360
        distance2 = (angle - target_angle) % 360
        if distance1 < distance2:
            return distance1, "left"
        return distance2, "right"