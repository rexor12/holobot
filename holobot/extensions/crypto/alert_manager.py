from .alert_manager_interface import AlertManagerInterface
from .enums import FrequencyType, PriceDirection
from .models import Alert, SymbolUpdateEvent
from asyncpg.connection import Connection
from decimal import Decimal
from holobot.discord.sdk import IMessaging
from holobot.sdk.database import DatabaseManagerInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.reactive import IListener
from typing import List

@injectable(AlertManagerInterface)
@injectable(IListener[SymbolUpdateEvent])
class AlertManager(AlertManagerInterface, IListener[SymbolUpdateEvent]):
    def __init__(self, database_manager: DatabaseManagerInterface, messaging: IMessaging, log: LogInterface):
        self.__database_manager = database_manager
        self.__messaging = messaging
        self.__log = log.with_name("Crypto", "AlertManager")
    
    async def add(self, user_id: str, symbol: str, direction: PriceDirection, value: Decimal,
        frequency_type: FrequencyType = FrequencyType.DAYS, frequency: int = 1):
        self.__log.debug(f"Adding alert... {{ UserId = {user_id}, Symbol = {symbol} }}")
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                row_count = await connection.fetchval(
                    "SELECT COUNT(*) FROM crypto_alerts WHERE user_id = $1 AND symbol = $2 AND direction = $3",
                    user_id, symbol, direction
                )
                if row_count != 0:
                    await connection.execute(
                        "UPDATE crypto_alerts SET price = $1, frequency_type = $5, frequency = $6 WHERE user_id = $2 AND symbol = $3 AND direction = $4",
                        value, user_id, symbol, direction, frequency_type, frequency
                    )
                    return
                # TODO Limit the maximum number of alerts per user.
                await connection.execute(
                    "INSERT INTO crypto_alerts (user_id, symbol, direction, price, frequency_type, frequency) VALUES ($1, $2, $3, $4, $5, $6)",
                    user_id, symbol, direction, value, frequency_type, frequency
                )
        self.__log.debug(f"Added alert. {{ UserId = {user_id}, Symbol = {symbol} }}")

    async def get_many(self, user_id: str, start_offset: int, page_size: int) -> List[Alert]:
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                records = await connection.fetch("SELECT symbol, direction, price FROM crypto_alerts WHERE user_id = $1 LIMIT $3 OFFSET $2", str(user_id), start_offset, page_size)
                return [Alert(
                    record["symbol"],
                    PriceDirection(record["direction"]),
                    Decimal(record["price"])
                ) for record in records]

    async def remove_many(self, user_id: str, symbol: str) -> List[Alert]:
        self.__log.debug(f"Deleting alerts... {{ UserId = {user_id}, Symbol = {symbol} }}")
        deleted_alerts = []
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                records = await connection.fetch("DELETE FROM crypto_alerts WHERE user_id = $1 AND symbol = $2 RETURNING direction, price", user_id, symbol)
                for record in records:
                    deleted_alerts.append(Alert(symbol, PriceDirection(record["direction"]), Decimal(record["price"])))
        self.__log.debug(f"Deleted alerts. {{ UserId = {user_id}, Symbol = {symbol}, Count = {len(deleted_alerts)} }}")
        return deleted_alerts

    async def remove_all(self, user_id: str) -> List[Alert]:
        self.__log.debug(f"Deleting all alerts... {{ UserId = {user_id} }}")
        deleted_alerts = []
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                records = await connection.fetch("DELETE FROM crypto_alerts WHERE user_id = $1 RETURNING symbol, direction, price", user_id)
                for record in records:
                    deleted_alerts.append(Alert(record["symbol"], PriceDirection(record["direction"]), Decimal(record["price"])))
        self.__log.debug(f"Deleted all alerts. {{ UserId = {user_id}, Count = {len(deleted_alerts)} }}")
        return deleted_alerts

    # TODO Use an "INNER JOIN" instead of processing these events one by one.
    # So we can either implement deferred updates (collect events),
    # or refactor the event to contain all symbol updates (fire once).
    # The former is probably a better choice, because 1) it's reusable, and
    # 2) we'd like to batch these queries anyway.
    async def on_event(self, event: SymbolUpdateEvent):
        sent_notifications = set()
        record_ids = set()
        async with self.__database_manager.acquire_connection() as connection:
            connection: Connection
            async with connection.transaction():
                async for record in connection.cursor((
                        "SELECT id, user_id, direction"
                        " FROM crypto_alerts"
                        " WHERE symbol = $1"
                        " AND targethit($2, direction, price)"
                        " AND inrange(notified_at, frequency_type, frequency)"
                    ), event.symbol, event.price):
                    user_id: str = record["user_id"]
                    direction: PriceDirection = PriceDirection(record["direction"])
                    notification_id = f"{user_id}/{direction.value}"
                    if notification_id in sent_notifications:
                        continue
                    sent_notifications.add(notification_id)
                    record_ids.add(str(record["id"]))
                    await self.__try_notify(user_id, event)
                if len(record_ids) == 0:
                    return
                await connection.execute("UPDATE crypto_alerts SET notified_at = NOW() WHERE id IN ({})".format(
                    ",".join(record_ids)
                ))
                self.__log.debug(f"Notified users. {{ AlertCount = {len(record_ids)}, Symbol = {event.symbol} }}")
    
    async def __try_notify(self, user_id: str, event: SymbolUpdateEvent):
        try:
            await self.__messaging.send_private_message(user_id, f"{event.symbol} price is {event.price:,.8f}.")
        except Exception as error:
            self.__log.error(f"Failed to notify a user. {{ UserId = {user_id} }}", error)
