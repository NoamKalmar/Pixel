from pyfirmata import Pin, Board, util

class MPU_z(Pin):
    def __init__(self, board: Board):
        self.board = board
        super().__init__(board, 10)