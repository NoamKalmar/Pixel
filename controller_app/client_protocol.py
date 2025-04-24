# -;-
def remove_all_commands():
    return b"-;-#"

# id;*(if toggled)command#
def send_command(command_id: int, command: str, is_toggled: bool) -> str: 
    message = f"{command_id};{'*' if is_toggled else ''}{command}#"
    return bytes(message, "utf-8")

# id;-
def send_remove_command(command_id: int) -> str:
    message = f"{command_id};-#"
    return bytes(message, "utf-8")

# id;data//id;data//...#
def get_commands_data(data: bytes) -> dict:
    commands_data = {}

    data = data.decode()
    data = data[:data.find("#")]
    values = data.split("//")[:-1]
    for value in values:
        command_id, return_value = value.split(";", maxsplit=1)
        commands_data[int(command_id)] = return_value
    return commands_data

def get_server_ip(data: bytes) -> None | str:
    data = data.decode()
    if not "pixel-" in data:
        return None
    address = data.split("pixel-")[1]
    return address