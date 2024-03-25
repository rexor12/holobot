import asyncio
from collections.abc import Awaitable
from datetime import timedelta

from holobot.extensions.general.models.channel_timer import ChannelTimer
from holobot.extensions.general.models.currency import Currency
from holobot.extensions.general.models.wallet import Wallet
from holobot.extensions.general.models.wallet_id import WalletId
from holobot.extensions.general.repositories import ChannelTimerRepository
from holobot.extensions.general.repositories.wallet_repository import WalletRepository
from holobot.extensions.todo_lists.models.todo_item import TodoItem
from holobot.extensions.todo_lists.repositories.todo_item_repository import TodoItemRepository
from holobot.framework.database import DatabaseManager
from holobot.framework.database.database_options import DatabaseOptions
from holobot.framework.database.unit_of_work_provider import UnitOfWorkProvider
from holobot.framework.logging import DefaultLogger
from holobot.sdk.configs import IOptions
from holobot.sdk.logging import ILogger, ILoggerFactory
from holobot.sdk.logging.enums import LogLevel
from holobot.sdk.utils.datetime_utils import utcnow

USER_ID = "401490060156862466"
SERVER_ID = "999259836439081030"
CHANNEL_ID = "1194764988980662372"
CURRENCY_ID1 = 1
CURRENCY_ID2 = 2
EMOJI_ID = "11111111111"
EMOJI_NAME = "test"

class TestOptionsProvider(IOptions[DatabaseOptions]):
    @property
    def value(self) -> DatabaseOptions:
        return DatabaseOptions(
            Host="127.0.0.1",
            Port=5432,
            Database="holobot",
            User="postgres",
            Password="password",
            IsSslEnabled=False,
            AutoCreateDatabase=False
        )

class TestLoggerFactory(ILoggerFactory):
    def create(self, target_type: type) -> ILogger:
        return DefaultLogger(target_type.__name__, lambda: LogLevel.DEBUG)

async def test_channel_timers():
    entity = ChannelTimer(
        user_id=USER_ID,
        server_id=SERVER_ID,
        channel_id=CHANNEL_ID,
        countdown_interval=timedelta(minutes=30),
        name_template="Hi %t",
        expiry_name_template="Bye %t"
    )
    identifier = await channel_timer_repository.add(entity)
    assert identifier != -1
    print(f"Added channel timer; ID={identifier}")

    entity = await channel_timer_repository.get(identifier)
    assert entity is not None
    print(f"Got channel timer; ID={entity.identifier}")

    entity.name_template = "Hi again %t"
    is_updated = await channel_timer_repository.update(entity)
    assert is_updated == True
    print(f"Updated channel timer; ID={entity.identifier}")

    entity = await channel_timer_repository.get(entity.identifier)
    assert entity is not None
    assert entity.name_template == "Hi again %t"
    print(f"Got updated channel timer; ID={entity.identifier}")

    deleted_count = await channel_timer_repository.delete(identifier)
    assert deleted_count == 1
    print(f"Deleted channel timer; ID={identifier}")

async def test_wallets():
    # currency1 = Currency(
    #     created_at=utcnow(),
    #     created_by=USER_ID,
    #     server_id=SERVER_ID,
    #     name="Test currency 1",
    #     emoji_id=EMOJI_ID,
    #     emoji_name=EMOJI_NAME
    # )
    # entity = Wallet(
    #     identifier=WalletId(user_id=USER_ID, server_id=SERVER_ID, currency_id=CURRENCY_ID1),
    #     amount=1000
    # )
    # entity2 = Wallet(
    #     identifier=WalletId(user_id=USER_ID, server_id=SERVER_ID, currency_id=CURRENCY_ID2),
    #     amount=5125
    # )
    wallets = await wallet_repository.get_wallets("401490060156862466", "1196136683037540362", include_global=True)
    for wallet in wallets:
        print(f"Wallet ID: {wallet.identifier}")

async def test_paginate_wallets_with_details():
    result = await wallet_repository.paginate_wallets_with_details(
        "401490060156862466",
        "999259836439081030",
        True,
        0,
        5
    )

    print(f"Pagination result count: {result.total_count}")
    for item in result.items:
        print(f"({item.wallet_id}) amount: {item.amount}, emoji: {item.currency_emoji_name}/{item.currency_emoji_id}")

async def test_todo_items():
    todo_item = TodoItem(
        user_id="401490060156862466",
        message="Test message, hello!"
    )

    identifier = await todo_item_repository.add(todo_item)
    print(f"Added to-do item with ID: {todo_item.identifier} ({identifier})")

    todo_item = await todo_item_repository.get(identifier)
    if not todo_item:
        print(f"Couldn't get to-do item with ID: {identifier}")
        return

    print(f"Got to-do item: {todo_item.identifier}")

    delete_count = await todo_item_repository.delete(identifier)
    print(f"Deleted to-do item with ID: {identifier}, delete count: {delete_count}")

    todo_item = await todo_item_repository.get(identifier)
    print(f"To-do item with ID: {identifier} exists: {todo_item is not None}")

async def main():
    try:
        await test_channel_timers()
        await test_wallets()
        await test_paginate_wallets_with_details()
        await test_todo_items()
    finally:
        await database_manager.stop()

event_loop = asyncio.get_event_loop()
task: Awaitable[None] | None = None
try:
    logger_factory = TestLoggerFactory()
    database_manager = DatabaseManager(
        TestOptionsProvider(),
        logger_factory,
        ()
    )
    unit_of_work_provider = UnitOfWorkProvider(database_manager)
    channel_timer_repository = ChannelTimerRepository(database_manager, unit_of_work_provider)
    wallet_repository = WalletRepository(database_manager, unit_of_work_provider)
    todo_item_repository = TodoItemRepository(database_manager, unit_of_work_provider)

    print("Starting database manager...")
    task = database_manager.start()
    print("Database manager started")

    # print("Press a key to continue...")
    # input()

    event_loop.run_until_complete(main())
    # event_loop.run_forever()
except KeyboardInterrupt:
    print("Stopping due to keyboard interrupt...")
finally:
    event_loop.stop()
    event_loop.close()
