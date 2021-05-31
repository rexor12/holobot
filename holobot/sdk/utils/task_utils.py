from ..exceptions import AggregateError
from asyncio.tasks import Task
from typing import List, Tuple

async def when_all(tasks: Tuple[Task, ...]) -> None:
    exceptions: List[Exception] = []
    for task in tasks:
        try:
            await task
        except Exception as error:
            exceptions.append(error)
    if len(exceptions) > 0:
        raise AggregateError(exceptions)
