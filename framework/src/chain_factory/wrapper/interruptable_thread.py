"""
Source:
https://stackoverflow.com/questions/14482230/why-does-the-python-threading
-thread-object-has-start-but-not-stop?noredirect=1&lq=1
"""

from _thread import interrupt_main
from _thread import exit as thread_exit
from ctypes import pythonapi
from ctypes import c_ulong
from ctypes import py_object
from ctypes import c_int
from logging import debug
from threading import Thread
from traceback import print_stack

_PyThreadState_SetAsyncExc = pythonapi.PyThreadState_SetAsyncExc
# noinspection SpellCheckingInspection
_PyThreadState_SetAsyncExc.argtypes = c_ulong, py_object
_PyThreadState_SetAsyncExc.restype = c_int

# noinspection PyUnreachableCode
if __debug__:
    # noinspection PyShadowingBuiltins
    def _set_async_exc(id, exc):
        if not isinstance(id, int):
            raise TypeError(f"{id!r} not an int instance")
        if not isinstance(exc, type):
            raise TypeError(f"{exc!r} not a type instance")
        if not issubclass(exc, BaseException):
            raise SystemError(f"{exc!r} not a BaseException subclass")
        return _PyThreadState_SetAsyncExc(id, exc)
else:
    _set_async_exc = _PyThreadState_SetAsyncExc


# noinspection PyShadowingBuiltins
def set_async_exc(id, exc, *args):
    if args:
        class StateInfo(exc):
            def __init__(self):
                super().__init__(*args)

        return _set_async_exc(id, StateInfo)
    return _set_async_exc(id, exc)


def interrupt(ident=None):
    if ident is None:
        interrupt_main()
    else:
        set_async_exc(ident, KeyboardInterrupt)


# noinspection PyShadowingBuiltins
def exit(ident=None):
    print("Exiting thread")
    if ident is None:
        thread_exit()
    else:
        set_async_exc(ident, SystemExit)


class ThreadAbortException(SystemExit):
    pass


class InterruptableThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def set_async_exc(self, exc, *args):
        """
        Set the thread to exit with the given exception,
        basically injecting an exception into the thread
        """
        debug(f"Setting thread {self.ident} to {exc} with args: {args}")
        return set_async_exc(self.ident, exc, *args)

    def interrupt(self):
        """
        Interrupt the thread with a KeyboardInterrupt exception,
        which is the same as pressing Ctrl+C or sending a SIGINT
        """
        self.set_async_exc(KeyboardInterrupt)

    def exit(self):
        """
        Exit the thread with a SystemExit exception,
        which is the same as calling sys.exit()
        """
        print("Exiting thread")
        debug(f"Exiting thread {self.ident}")
        self.set_async_exc(SystemExit)

    def abort(self, *args):
        """
        Abort the thread with a ThreadAbortException exception,
        which is the same as sending a SIGTERM
        """
        print("Aborting thread")
        print_stack()
        debug(f"Aborting thread {self.ident} with args: {args}")
        self.set_async_exc(ThreadAbortException, *args)
