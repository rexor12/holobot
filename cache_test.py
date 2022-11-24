import asyncio
from datetime import datetime, timedelta, timezone

from holobot.sdk.caching import (
    AbsoluteExpirationCacheEntryPolicy, ConcurrentMemoryCache, NoExpirationCacheEntryPolicy,
    SlidingExpirationCacheEntryPolicy
)

class SomeState:
    def __init__(self, value: int) -> None:
        self.value = value

def now():
    return datetime.now(tz=timezone.utc)

async def main():
    cache = ConcurrentMemoryCache[str, SomeState]()

    print(f"[{now()}] Adding Item1 (absolute)")
    await cache.get_or_add(
        "Item1",
        lambda _: SomeState(1),
        AbsoluteExpirationCacheEntryPolicy(now() + timedelta(minutes=3))
    )
    print(f"[{now()}] Added Item1")

    print(f"[{now()}] Adding Item2 (sliding)")
    await cache.get_or_add(
        "Item2",
        lambda _: SomeState(2),
        SlidingExpirationCacheEntryPolicy(timedelta(minutes=3))
    )
    print(f"[{now()}] Added Item2")

    print(f"[{now()}] Adding Item3 (none)")
    await cache.get_or_add(
        "Item3",
        lambda _: SomeState(3),
        NoExpirationCacheEntryPolicy()
    )
    print(f"[{now()}] Added Item3")

    print(f"[{now()}] Waiting for 1 minute")
    await asyncio.sleep(60)
    print(f"[{now()}] Finished waiting, accessing Item2")
    item2 = await cache.get("Item2")
    print(item2)
    print(f"[{now()}] Accessed Item2")

    print(f"[{now()}] Waiting for 5 minutes")
    await asyncio.sleep(5 * 60)
    print(f"[{now()}] Finished waiting, stopping")

    await cache.dispose()

asyncio.run(main())
