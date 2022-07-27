from typing import Any

from structlog import DropEvent
from structlog.types import EventDict

def ignore_loggers_by_name(name: str, *names: str):
    filtered_names = [name, *names] if names else [name]
    def processor(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
        if (
            (logger_name := event_dict.get("logger_name", None))
            and logger_name in filtered_names
        ):
            raise DropEvent
        return event_dict
    return processor
