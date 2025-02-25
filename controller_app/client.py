import socket
import threading
from collections import defaultdict
import client_protocol

class Client(threading.Thread):
    def __init__(self, ip: str = None, port: int = None):
        super().__init__(daemon=False)
        self.ip = ip
        self.port = port
        self.running = True
        self.commands_data = defaultdict(str)
        self.socket = None
        self.current_command_id = 0
        self.connection_error = False

    def set_address(self, ip, port):
        self.ip = ip
        self.port = port

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            try:
                self.socket.connect((self.ip, self.port))
                self.remove_all_commands()
            except:
                self.connection_error = True
            
            if self.connection_error:
                return
            socket.setdefaulttimeout(5)
            while self.running:
                data = self.socket.recv(1024)
                if data:
                    self.commands_data = client_protocol.get_commands_data(data)

    def send_command(self, command: str, is_toggled: bool):
        message = client_protocol.send_command(self.current_command_id, command, is_toggled)
        self.socket.sendall(message)
        self.current_command_id += 1
        return self.current_command_id - 1
    
    def remove_command(self, command_id: int):
        message = client_protocol.send_remove_command(command_id)
        self.socket.sendall(message)
    
    def remove_all_commands(self):
        message = client_protocol.remove_all_commands()
        self.socket.sendall(message)