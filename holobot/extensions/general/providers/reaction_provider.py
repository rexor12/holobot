import asyncio
from collections import deque
from datetime import timedelta

from holobot.extensions.general.api_clients import IWaifuPicsClient
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.network.exceptions import TooManyRequestsError
from holobot.sdk.network.resilience import AsyncRetryPolicy
from holobot.sdk.utils import add_or_update_async
from holobot.sdk.utils.datetime_utils import utcnow
from .ireaction_provider import IReactionProvider

@injectable(IReactionProvider)
class ReactionProvider(IReactionProvider):
    __DEFAULT_RETRY_INTERVAL = timedelta(milliseconds=500)

    def __init__(
        self,
        waifu_pics_client: IWaifuPicsClient
    ) -> None:
        super().__init__()
        self.__api_client = waifu_pics_client
        self.__images_by_category = dict[str, deque[str]]()
        self.__lock = asyncio.Lock()
        self.__retry_policy = AsyncRetryPolicy[str, tuple[str, ...]](
            3,
            ReactionProvider.__on_retry_error
        )

    @staticmethod
    def __on_retry_error(
        policy: AsyncRetryPolicy[str, tuple[str, ...]],
        attempt_index: int,
        exception: Exception
    ) -> timedelta:
        if (
            not isinstance(exception, TooManyRequestsError)
            or exception.retry_after is None
        ):
            return ReactionProvider.__DEFAULT_RETRY_INTERVAL

        if isinstance(exception.retry_after, int):
            return timedelta(seconds=exception.retry_after)

        return exception.retry_after - utcnow()

    async def get(self, category: str) -> str | None:
        async with self.__lock:
            images = await add_or_update_async(
                self.__images_by_category,
                category,
                lambda k: self.__query_images(k),
                lambda k,i: self.__query_images(k, i)
            )

            return images.pop() if images else None

    async def __query_images(
        self,
        category: str,
        current_items: deque[str] | None = None
    ) -> deque[str]:
        if current_items:
            return current_items

        result = await self.__retry_policy.execute(
            lambda c: self.__api_client.get_batch(c),
            category
        )

        return deque(result)
