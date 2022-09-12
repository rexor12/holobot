import asyncio
from collections import deque

from holobot.extensions.general.api_clients import IWaifuPicsClient
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.network.resilience.exceptions import RateLimitedError
from holobot.sdk.utils import add_or_update_async
from .ireaction_provider import IReactionProvider

@injectable(IReactionProvider)
class ReactionProvider(IReactionProvider):
    def __init__(
        self,
        waifu_pics_client: IWaifuPicsClient
    ) -> None:
        super().__init__()
        self.__api_client = waifu_pics_client
        self.__images_by_category = dict[str, deque[str]]()
        self.__lock = asyncio.Lock()

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

        for index in range(3):
            try:
                result = await self.__api_client.get_batch(category)
                return deque(result)
            except RateLimitedError:
                # After the last attempt, we propagate the exception.
                if index == 2:
                    raise
                else:
                    await asyncio.sleep(0.5)

        return deque()
