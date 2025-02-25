import socket
from collections import defaultdict

# -;-
def remove_all_commands():
    return b"-;-"

# id;*(if toggled)command
def send_command(command_id: int, command: str, is_toggled: bool): 
    message = f"{command_id};{'*' if is_toggled else ''}{command}"
    return bytes(message, "utf-8")

# id;-
def send_remove_command(command_id: int):
    message = f"{command_id};-"
    return bytes(message, "utf-8")

# id;data//id;data//...#
def get_commands_data(data: bytes):
    commands_data = defaultdict(str)

    data = data.decode()
    data = data[:data.find("#")]
    values = data.split("//")[:-1]
    for value in values:
        command_id, return_value = value.split(";", maxsplit=1)
        commands_data[command_id] = return_value
    return commands_data