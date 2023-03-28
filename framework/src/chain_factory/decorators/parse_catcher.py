from sys import stdout
from traceback import print_exc
from logging import exception
from typing import Tuple
from typing import Type


def parse_catcher(errors: Tuple[Type[Exception], ...] = (Exception, )):
    """
    Catches exceptions and prints them to stdout.
    Returns None if an exception is caught
    Used in QueueHandler and ListHandler
    """
    def decorator(func):
        def new_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except errors as e:
                print_exc(file=stdout)
                exception(e)
                return None

        return new_func
    return decorator
