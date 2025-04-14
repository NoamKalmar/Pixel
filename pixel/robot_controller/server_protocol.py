from robot_controller.command import Command

# Returns Command - Add new command
# Returns int - Remove command by id
# Returns None - Remove all commands
def get_command(data: bytes) -> Command | int | None:
    data = data.decode()
    command_id, command_data = data.split(";", maxsplit=1)
    if command_data == "-":
        if command_id == "-":
            return None
        return int(command_id)
    
    toggle_prefix = command_data.startswith("*")
    remove_prefix = command_data.startswith("-")
    if toggle_prefix or remove_prefix: command_data = command_data[1:]

    command = Command(
                command_id=int(command_id),
                command=f"self.robot.{command_data}",
                is_toggled=toggle_prefix
    )
    return command

# id;data//id;data//...#
def send_data(commands: list[Command]):
    message = ""
    for command in commands:
        if command.return_value == "":
            continue
        message += f"{command.command_id};{command.return_value}//"
    message += "#"
    return bytes(message, "utf-8")

# pixel-<self_ip>:<self_port>
def broadcast_ip(self_address: tuple):
    ip, port = self_address
    message = f"pixel-{ip}:{port}"
    return bytes(message, "utf-8")