from asyncio.tasks import Task

from ..exceptions import AggregateError

async def when_all(tasks: tuple[Task, ...]) -> None:
    exceptions: list[Exception] = []
    for task in tasks:
        try:
            await task
        except Exception as error:
            exceptions.append(error)
    if len(exceptions) > 0:
        raise AggregateError(exceptions)
