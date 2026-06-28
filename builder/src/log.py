from enum import Enum
import inspect

class LogLevel(Enum):
    QUIET = 0 #no message should be sent on LogLevel.QUIET
    FATAL = 1
    WARNING = 2
    INFO = 3

class DebugLevel(Enum):
    NONE = 0
    SOME = 1
    MORE = 2
    ALL = 3

class Logger:
    def __init__(self):
        self.loglevel = LogLevel.WARNING
        self.debuglevel = DebugLevel.NONE
        pass

    def setLogLevel(self, loglevel: LogLevel):
        self.loglevel = loglevel

    def setDebugLevel(self, debuglevel: DebugLevel):
        self.debuglevel = debuglevel

    def print(self, msg, loglevel: LogLevel = LogLevel.INFO):
        caller_frame = inspect.stack()[1]
        if(loglevel.value <= self.loglevel.value):
            print(f'[{loglevel.name}] {msg}')

        if(self.debuglevel.value == DebugLevel.MORE.value):
            filename = caller_frame.filename
            print(f'[DEBUG]\t\t@{filename}')

        if(self.debuglevel.value == DebugLevel.ALL.value):
            filename = caller_frame.filename
            function_name = caller_frame.function
            line_number = caller_frame.lineno
            print(f'[DEBUG]\t\t@{filename}->[{function_name}]:line {line_number}')

    def debugprint(self, msg, debuglevel: DebugLevel = DebugLevel.SOME):
        if(self.debuglevel.value >= debuglevel.value):
            if(self.debuglevel.value > DebugLevel.NONE.value):
                print(f'[DEBUG] {msg}')
                if(self.debuglevel.value >= DebugLevel.MORE.value):
                    caller_frame = inspect.stack()[1]
                    print(f'[DEBUG]\t\t@ {caller_frame.filename}:{caller_frame.lineno}')

    def error(self, msg, T: type[BaseException] = ValueError):
        self.print(msg, LogLevel.FATAL)
        raise T(msg)
