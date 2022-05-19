from .repositories import ReminderRepositoryInterface
from datetime import datetime
from holobot.discord.sdk import IMessaging
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import StartableInterface
from holobot.sdk.logging import LogInterface
from holobot.sdk.threading import CancellationToken, CancellationTokenSource
from holobot.sdk.threading.utils import wait
from typing import Awaitable, Optional

import asyncio

DEFAULT_RESOLUTION: int = 60
DEFAULT_DELAY: int = 30

@injectable(StartableInterface)
class ReminderProcessor(StartableInterface):
    def __init__(self,
        configurator: ConfiguratorInterface,
        messaging: IMessaging,
        log: LogInterface,
        reminder_repository: ReminderRepositoryInterface) -> None:
        super().__init__()
        self.__configurator: ConfiguratorInterface = configurator
        self.__messaging: IMessaging = messaging
        self.__log: LogInterface = log.with_name("Reminders", "ReminderProcessor")
        self.__reminder_repository: ReminderRepositoryInterface = reminder_repository
        self.__process_resolution = self.__configurator.get("Reminders", "ProcessorResolution", DEFAULT_RESOLUTION)
        self.__process_delay = self.__configurator.get("Reminders", "ProcessorDelay", DEFAULT_DELAY)
        self.__token_source: Optional[CancellationTokenSource] = None
        self.__background_task: Optional[Awaitable[None]] = None
    
    async def start(self):
        if not self.__configurator.get("Reminders", "Enable", True):
            self.__log.info("Reminders are disabled by configuration.")
            return
        
        self.__log.info(f"Reminders are enabled. {{ Delay = {self.__process_delay}, Resolution = {self.__process_resolution} }}")
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
        self.__log.debug("Stopped background task.")
    
    async def __process_reminders_async(self, token: CancellationToken):
        await wait(self.__process_delay, token)
        while not token.is_cancellation_requested:
            self.__log.trace("Processing reminders...")
            processed_reminders: int = 0
            try:
                reminders = await self.__reminder_repository.get_triggerable()
                for reminder in reminders:
                    await self.__messaging.send_private_message(reminder.user_id, f"Your reminder: {reminder.message}")

                    if reminder.is_repeating:
                        reminder.last_trigger = datetime.utcnow()
                        reminder.recalculate_next_trigger()
                        await self.__reminder_repository.update_next_trigger(reminder.id, reminder.next_trigger)
                        self.__log.trace(f"Processed reminder. {{ ReminderId = {reminder.id}, NextTrigger = {reminder.next_trigger} }}")
                    else:
                        await self.__reminder_repository.delete(reminder.id)
                    processed_reminders += 1
            except Exception as error:
                self.__log.error(f"Processing failed. Further processing will stop. {{ Reason = UnexpectedError }}", error)
                raise
            finally:
                self.__log.trace(f"Processed reminders. {{ Count = {processed_reminders} }}")
            await wait(self.__process_resolution, token)
