from typing import List

import traceback

ERROR_MESSAGE = "One or more errors occurred."

class AggregateError(Exception):
    def __init__(self, inner_exceptions: List[Exception] = [], *args):
        super().__init__(*args)
        self.inner_exceptions: List[Exception] = inner_exceptions
    
    def __str__(self) -> str:
        exception_string = f"{ERROR_MESSAGE}\n"
        exception_count = len(self.inner_exceptions)
        for index in range(0, exception_count):
            tb = "".join(traceback.TracebackException.from_exception(self.inner_exceptions[index]).format())
            exception_string += f"----- Inner Exception -----\n{tb}"
        return exception_string
