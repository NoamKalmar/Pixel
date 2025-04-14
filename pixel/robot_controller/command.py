from  dataclasses import dataclass

@dataclass
class Command:
    command_id: int
    command: str
    is_toggled: bool
    return_value: str = ""
    evaluated: bool = False