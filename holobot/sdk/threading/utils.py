from .cancellation_promise import CancellationPromise
from .cancellation_token import CancellationToken
from typing import Optional

import asyncio

def wait(
    timeout: int,
    cancellation_token: CancellationToken,
    loop: Optional[asyncio.BaseEventLoop] = None) -> asyncio.Task[None]:
    """Asynchronously waits for the specified duration.

    :param timeout: The time to wait for in seconds.
    :type timeout: int
    :param cancellation_token: An optional cancellation token used for cancelling the operation.
    :type cancellation_token: CancellationToken
    :param loop: An optional asyncio event loop, defaults to None.
    :type loop: Optional[asyncio.BaseEventLoop], optional
    :return: An awaitable that represents the operation.
    :rtype: Awaitable[None]
    """

    active_loop = loop or asyncio.get_event_loop()
    return CancellationPromise(
        active_loop.create_task(asyncio.sleep(timeout, None)),
        cancellation_token
    )()
