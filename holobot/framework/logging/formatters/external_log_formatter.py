from io import StringIO

import logging
import traceback

class ExternalLogFormatter(object):
    """A formatter used to format log records emitted by external libraries."""

    def format(self, record: logging.LogRecord) -> str:
        with StringIO(record.getMessage()) as buffer:
            if record.exc_info:
                buffer.write("\n")
                if record.exc_text:
                    buffer.writelines((record.exc_text,))
                else:
                    traceback.print_exception(
                        record.exc_info[0],
                        record.exc_info[1],
                        record.exc_info[2],
                        None,
                        buffer
                    )

            if record.stack_info:
                buffer.writelines((record.stack_info,))

            result = buffer.getvalue()
            return result if result[-1:] != "\n" else result[:-1]

DefaultInstance = ExternalLogFormatter()
