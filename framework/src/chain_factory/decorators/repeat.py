from functools import wraps
from logging import exception
from typing import Any, Tuple, Type


def repeat_async(
    errors: Tuple[Type[Exception]] = (Exception, ),
    on_error_return_value: Any = None,
    max_counter_value: int = 10
):
    def decorator(func):
        @wraps(func)
        async def new_func(*args, **kwargs):
            # used to temporarily store the current error counter
            counter: int = -1
            try:
                if "repeat_counter" in kwargs:
                    counter = kwargs["repeat_counter"]
                    # delete the error counter from kwargs so,
                    # that the value is not visible
                    # in the actual decorated function
                    del kwargs["repeat_counter"]
                return await func(*args, **kwargs)
            except errors as e:
                exception(e)
                if counter >= 0:
                    kwargs["repeat_counter"] = counter  # restore error counter
                if "repeat_counter" in kwargs:
                    kwargs["repeat_counter"] = kwargs["repeat_counter"] + 1
                else:
                    kwargs["repeat_counter"] = 0
                if kwargs["repeat_counter"] >= max_counter_value:
                    return on_error_return_value
                return new_func(*args, **kwargs)

        return new_func
    return decorator


def repeat(
    errors: Tuple[type[Exception]] = (Exception, ),
    on_error_return_value: Any = None,
    max_counter_value: int = 10
):
    def decorator(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            # used to temporarily store the current error counter
            counter: int = -1
            try:
                if "repeat_counter" in kwargs:
                    counter = kwargs["repeat_counter"]
                    # delete the error counter from kwargs so,
                    # that the value is not visible
                    # in the actual decorated function
                    del kwargs["repeat_counter"]
                return func(*args, **kwargs)
            except errors as e:
                exception(e)
                if counter >= 0:
                    kwargs["repeat_counter"] = counter  # restore error counter
                if "repeat_counter" in kwargs:
                    kwargs["repeat_counter"] = kwargs["repeat_counter"] + 1
                else:
                    kwargs["repeat_counter"] = 0
                if kwargs["repeat_counter"] >= max_counter_value:
                    return on_error_return_value
                return new_func(*args, **kwargs)

        return new_func
    return decorator
