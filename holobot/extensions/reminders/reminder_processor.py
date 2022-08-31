import asyncio
from collections.abc import Awaitable
from datetime import datetime

from holobot.discord.sdk import IMessaging
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import IStartable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.threading import CancellationToken, CancellationTokenSource
from holobot.sdk.threading.utils import wait
from .repositories import IReminderRepository

DEFAULT_RESOLUTION: int = 60
DEFAULT_DELAY: int = 30

@injectable(IStartable)
class ReminderProcessor(IStartable):
    def __init__(
        self,
        configurator: ConfiguratorInterface,
        messaging: IMessaging,
        logger_factory: ILoggerFactory,
        reminder_repository: IReminderRepository
    ) -> None:
        super().__init__()
        self.__configurator: ConfiguratorInterface = configurator
        self.__messaging: IMessaging = messaging
        self.__logger = logger_factory.create(ReminderProcessor)
        self.__reminder_repository: IReminderRepository = reminder_repository
        self.__process_resolution = self.__configurator.get("Reminders", "ProcessorResolution", DEFAULT_RESOLUTION)
        self.__process_delay = self.__configurator.get("Reminders", "ProcessorDelay", DEFAULT_DELAY)
        self.__token_source: CancellationTokenSource | None = None
        self.__background_task: Awaitable[None] | None = None

    async def start(self):
        if not self.__configurator.get("Reminders", "Enable", True):
            self.__logger.info("Reminders are disabled by configuration")
            return

        self.__logger.info(
            "Reminders are enabled",
            delay=self.__process_delay,
            resolution=self.__process_resolution
        )
        self.__token_source = CancellationTokenSource()
        self.__background_task = asyncio.create_task(
            self.__process_reminders_async(self.__token_source.token)
        )

    async def stop(self):
        if self.__token_source: self.__token_source.cancel()
        if self.__background_task:
            try:
                await self.__background_task
            except asyncio.exceptions.CancelledError:
                pass
        self.__logger.debug("Stopped background task")

    async def __process_reminders_async(self, token: CancellationToken):
        await wait(self.__process_delay, token)
        while not token.is_cancellation_requested:
            self.__logger.trace("Processing reminders...")
            processed_reminders: int = 0
            try:
                reminders = await self.__reminder_repository.get_triggerable()
                for reminder in reminders:
                    await self.__messaging.send_private_message(reminder.user_id, f"Your reminder: {reminder.message}")

                    if reminder.is_repeating:
                        reminder.last_trigger = datetime.utcnow()
                        reminder.recalculate_next_trigger()
                        await self.__reminder_repository.update(reminder)
                        self.__logger.trace(
                            "Processed reminder",
                            reminder_id=reminder.identifier,
                            next_trigger=reminder.next_trigger
                        )
                    else:
                        await self.__reminder_repository.delete(reminder.identifier)
                    processed_reminders += 1
            except Exception as error:
                self.__logger.error("Unexpected failure, processing will stop", error)
                raise
            finally:
                self.__logger.trace("Processed reminders", count=processed_reminders)
            await wait(self.__process_resolution, token)
