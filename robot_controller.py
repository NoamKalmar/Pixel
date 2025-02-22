from dataclasses import dataclass
import threading
import socket
import cv2
from robot import Robot
from command import Command
import server_protocol
import time
import numpy as np

class RobotController:
    def __init__(self, robot: Robot, cap: cv2.VideoCapture, server_address: tuple):
        self.robot = robot
        self.cap = cap
        self.server_address = server_address
        self.running = True
        self.client_connected = False
        self.commands = []
        self.server_thread = threading.Thread(target=self.server_loop, daemon=True)

    def start(self):
        self.server_thread.start()
        self.robot_loop()

    def robot_loop(self):
        while self.cap.isOpened():
            key = cv2.waitKey(5)
            if key == ord("q"):
                break
            success, image = self.cap.read()
            self.robot.loop(image, True)
            self.exec_commands()
        self.running = False
        self.cap.release()

    def exec_commands(self):
        for command in self.commands:
            if not command.is_toggled and command.evaluated:
                continue
            try:
                value = eval(command.command)
            except:
                value = "Error"

            command.evaluated = True
            command.return_value = value

            # print(command.return_value)

    def send_live_data(self, conn: socket.socket):
        while self.running and self.client_connected:
            message = server_protocol.send_data(self.commands)
            conn.sendall(message)
            for command in self.commands:
                if not command.is_toggled and command.evaluated:
                    self.commands.remove(command)

            time.sleep(0.1)

    def handle_client(self, conn: socket.socket):
        while self.running:
            data = conn.recv(1024)
            if not data:
                print("Client disconnected")
                self.client_connected = False
                return

            protocol_data = server_protocol.get_command(data)
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
            server_socket.bind(self.server_address)
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