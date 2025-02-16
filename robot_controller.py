from dataclasses import dataclass
import threading
import socket
import cv2
from robot import Robot

@dataclass
class Command:
    command: str
    is_toggeled: bool
    command_id: int
    return_value: str = ""

class RobotController:
    def __init__(self, robot: Robot, cap: cv2.VideoCapture, server_address: tuple):
        self.robot = robot
        self.cap = cap
        self.server_address = server_address
        self.running = True
        self.commands = []
        self.robot_thread = threading.Thread(target=self.robot_loop, daemon=True)
        self.server_thread = threading.Thread()

    def robot_loop(self):
        while self.cap.isOpened():
            key = cv2.waitKey(5)
            if key == ord("q"):
                break
            success, image = self.cap.read()
            self.robot.loop(image, True)
            self.exec_commands()
        running = False

    def exec_commands(self):
        for command in self.commands:
            value = eval(command)
            command.return_value = value
            if not command.is_toggeled:
                self.commands.remove(command)

    def send_live_data(self, conn: socket.socket):
        pass

    def handle_client(self, conn: socket.socket):
        pass

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(self.server_address)
            server_socket.listen(1)
            conn, addr = server_socket.accept()
            print(f"Connected by {addr}")

            with conn:
                while self.running:
                    self.send_live_data()
                    self.handle_client()