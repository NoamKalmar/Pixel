import threading
import socket
import cv2
from robot import Robot
from robot_controller.command import Command
import robot_controller.server_protocol as protocol
import time

SERVER_PORT = 1989
SERVER_ADDRESS = ("0.0.0.0", SERVER_PORT)

BROADCAST_PORT = 1990
BROADCAST_ADDRESS = ("255.255.255.255", BROADCAST_PORT)

class RobotController:
    def __init__(self, robot: Robot, cap_index: int = 0, crash_if_error: bool = False):
        self.robot = robot
        self.cap_index = cap_index
        self.crash_if_error = crash_if_error
        self.cap: cv2.VideoCapture = None
        self.init_cap()
        self.running = True
        self.client_connected = False
        self.commands: list[Command] = []
        self.server_thread = threading.Thread(target=self.server_loop, daemon=True)
        self.broadcast_ip_thread = threading.Thread(target=self.broadcast_ip, daemon=True)
        self_ip = socket.gethostbyname(socket.gethostname())
        self.self_address = (self_ip, SERVER_PORT)

    def init_cap(self):
        if not self.cap is None:
            self.cap.release()
        self.cap = cv2.VideoCapture(self.cap_index, cv2.CAP_DSHOW)
    
    def start(self):
        self.server_thread.start()
        self.broadcast_ip_thread.start()
        self.robot_loop()

    def robot_loop(self):
        while self.cap.isOpened():
            key = cv2.waitKey(5)
            if key == ord("q"):
                break
            if key == ord("r"):
                self.init_cap()
            success, image = self.cap.read()
            self.robot.loop(image, True)
            self.exec_commands()
        self.running = False
        self.cap.release()

    def exec_commands(self):
        for command in self.commands:
            if not command.is_toggled and command.evaluated:
                continue
            if self.crash_if_error:
                value = eval(command.command)
            else:
                try:
                    value = eval(command.command)
                except:
                    value = "Error"
            command.evaluated = True
            command.return_value = value

    def broadcast_ip(self):
        while self.running:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as broadcast_socket:
                broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                while not self.client_connected:
                    message = protocol.broadcast_ip(self.self_address)
                    broadcast_socket.sendto(message, BROADCAST_ADDRESS)
                    time.sleep(1)

    def send_live_data(self, conn: socket.socket):
        while self.running and self.client_connected:
            if not isinstance(conn, socket.socket):
                break
            message = protocol.send_data(self.commands)
            conn.sendall(message)
            for command in self.commands:
                if not command.is_toggled and command.evaluated:
                    self.commands.remove(command)

            time.sleep(0.1)

    def handle_client(self, conn: socket.socket):
        while self.running:
            try:
                data = conn.recv(1024)
            except:
                print("Client disconnected")
                self.client_connected = False
                return
            if not data:
                print("Client disconnected")
                self.client_connected = False
                return

            protocol_data = protocol.get_command(data)
            print(protocol_data)
            if protocol_data == None:
                self.commands = []
                continue

            in_commands = False
            for command in self.commands:
                if isinstance(protocol_data, int):
                    if command.command_id == protocol_data:
                        self.commands.remove(command)
                        in_commands = True
                elif protocol_data.command == command.command:
                    in_commands = True
                    break
                
            if in_commands:
                continue
            
            if not isinstance(protocol_data, Command):
                continue

            self.commands.append(protocol_data)

    def server_loop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(SERVER_ADDRESS)
            server_socket.listen(1)
            while self.running:
                conn, addr = server_socket.accept()
                self.client_connected = True
                print(f"Connected by {addr}")
                self.commands = []
                with conn:
                    self.send_data_thread = threading.Thread(target=self.send_live_data, args=(conn,), daemon=True)
                    self.send_data_thread.start()
                    self.handle_client(conn)