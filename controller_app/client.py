import socket
import threading
import client_protocol
import time
from typing import Callable, Optional

BROADCAST_LISTENER_PORT = 1990
BROADCAST_LISTENER_ADDRESS = ("0.0.0.0", BROADCAST_LISTENER_PORT)

class CommandReturnValue:
    def __init__(self):
        self.value: Optional[str] = None
    
    def get_value(self):
        return str(self.value)

    def __repr__(self):
        return self.get_value()

class Client(threading.Thread):
    def __init__(self, ip: str = None, port: int = None):
        super().__init__(daemon=False)
        self.ip = ip
        self.port = port
        self.running = True
        self.commands_data = {}
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
    
    def got_command_response(self, command_id: int) -> bool:
        return command_id in self.commands_data.keys()

    def get_command_value(
            self, 
            command: str, 
            return_value_object: Optional[CommandReturnValue] = None, 
            on_return: Optional[Callable] = None
        ):
        command_return_thread = threading.Thread(
            target=self._get_command_value,
            args=(command, return_value_object, on_return)
        )
        command_return_thread.start()
    
    def _get_command_value(
            self, 
            command: str, 
            return_value_object: Optional[CommandReturnValue],
            on_return: Optional[Callable],
            timeout: float = 2
        ):
        command_id = self.send_command(command, False)
        start_time = time.time()
        while not self.got_command_response(command_id):
            if time.time() - start_time > timeout:
                break
        else:
            try:
                return_value = self.commands_data[command_id]
            except KeyError:
                return
            if return_value_object is not None:
                return_value_object.value = return_value
            if on_return is not None:
                on_return(return_value)
        return # If the return value was not sent back by the robot for some reason, do nothing
        

class IPFinder:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(BROADCAST_LISTENER_ADDRESS)
        self.socket.settimeout(0.1)

    def get_ip(self, max_time: float = 2) -> None | str:
        start_time = time.time()
        while time.time() - start_time < max_time:
            server_ip = self._find_ip()
            if server_ip:
                return server_ip
        return None

    def _find_ip(self) -> None | str:
        try:
            data = self.socket.recv(1024)
            server_ip = client_protocol.get_server_ip(data)
            return server_ip
        except TimeoutError:
            return None

    def close(self) -> None:
        self.socket.close()