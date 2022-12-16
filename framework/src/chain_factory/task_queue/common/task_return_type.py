from typing import Union, Callable, Dict, Tuple
from ..models.mongodb_models import Task

CallbackType = Callable[..., "TaskReturnType"]
TaskReturnType = Union[
    None, str, Task, bool, CallbackType
]
ArgumentType = Dict[str, str]
NormalizedTaskReturnType = Tuple[
    TaskReturnType,
    ArgumentType
]
TaskRunnerReturnType = Union[None, NormalizedTaskReturnType]
