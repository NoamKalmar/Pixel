from dataclasses import dataclass
from collections.abc import Callable

@dataclass
class Show:
    name: str
    steps: list[Callable | tuple[Callable, float]] # Each value can be either the step function or a tuple of the function and many seconds to run it
    start_step_time: float = None