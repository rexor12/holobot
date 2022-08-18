
import traceback

class AggregateError(Exception):
    def __init__(self, inner_exceptions: list[Exception] | None = None, *args):
        super().__init__(*args)
        self.inner_exceptions: list[Exception] = inner_exceptions or []

    def __str__(self) -> str:
        exception_string = "One or more errors occurred.\n"
        for exception in self.inner_exceptions:
            tb = "".join(traceback.TracebackException.from_exception(exception).format())
            exception_string += f"----- Inner Exception -----\n{tb}"
        return exception_string
