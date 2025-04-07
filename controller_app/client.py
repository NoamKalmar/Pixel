import socket
import threading
from collections import defaultdict
import client_protocol
import time

BROADCAST_LISTENER_PORT = 1990
BROADCAST_LISTENER_ADDRESS = ("0.0.0.0", BROADCAST_LISTENER_PORT)

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
        self.got_data_time = None
        self.is_connected = False

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
            self.is_connected = True
            while self.running:
                if self.got_data_time and time.time() - self.got_data_time < 2:
                    self.is_connected = True
                else:
                    self.is_connected = False
                try:
                    data = self.socket.recv(1024)
                    if data:
                        self.commands_data = client_protocol.get_commands_data(data)
                        self.got_data_time = time.time()
                except:
                    pass

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


class IPFinder:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(BROADCAST_LISTENER_ADDRESS)
        self.socket.settimeout(0.1)
        self.last_ip = None
        self.last_ip_time = 0

    def get_ip(self, max_time: float = 2) -> None | str:
        self._update_ip()
        if time.time() - self.last_ip_time < max_time:
            return self.last_ip
        return None

    def _update_ip(self) -> None:
        try:
            data = self.socket.recv(1024)
            server_ip = client_protocol.get_server_ip(data)
            self.last_ip = server_ip
            self.last_ip_time = time.time()
        except TimeoutError:
            pass
        

    def close(self) -> None:
        self.socket.close()