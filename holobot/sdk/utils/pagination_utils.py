from collections.abc import Awaitable
from typing import Callable, TypeVar, cast

from holobot.sdk.queries import PaginationResult

TState = TypeVar("TState")
TItem = TypeVar("TItem")

async def paginate_with_fallback(
    paginator: Callable[[int, int, TState], Awaitable[PaginationResult[TItem]]],
    page_index: int,
    page_size: int,
    state: TState
) -> PaginationResult[TItem]:
    """Performs pagination using the specified paginator function.

    If the specified page doesn't have any items, the first ("0th") page is returned.

    :param paginator: The function that performs the pagination.
    :type paginator: Callable[[int, int, TState], Awaitable[PaginationResult[TItem]]]
    :param page_index: The requested page index.
    :type page_index: int
    :param page_size: The requested page size.
    :type page_size: int
    :param state: An additional argument to be passed to the paginator.
    :type state: TState
    :return: If it contains at least one item, the requested page; otherwise, the first ("0th") page.
    :rtype: PaginationResult[TItem]
    """

    page_indexes = set((page_index, 0))
    result = None
    for page_index in sorted(page_indexes, reverse=True):
        result = await paginator(page_index, page_size, state)
        if result.items:
            return result

    # NOTE "result" is never unbound or None, because we add at least
    # one item to the set, hence the cast to silence the linter.
    return cast(PaginationResult[TItem], result)
