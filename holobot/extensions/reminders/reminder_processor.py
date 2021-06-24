from .repositories import ReminderRepositoryInterface
from asyncio.tasks import Task
from datetime import datetime
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.integration import MessagingInterface
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import StartableInterface
from holobot.sdk.logging import LogInterface
from holobot.sdk.threading import AsyncLoop
from typing import Optional

import asyncio

DEFAULT_RESOLUTION: int = 60
DEFAULT_DELAY: int = 30

@injectable(StartableInterface)
class ReminderProcessor(StartableInterface):
    def __init__(self, services: ServiceCollectionInterface) -> None:
        super().__init__()
        self.__configurator: ConfiguratorInterface = services.get(ConfiguratorInterface)
        self.__messaging: MessagingInterface = services.get(MessagingInterface)
        self.__log: LogInterface = services.get(LogInterface).with_name("Reminders", "ReminderProcessor")
        self.__reminder_repository: ReminderRepositoryInterface = services.get(ReminderRepositoryInterface)
        self.__background_loop: Optional[AsyncLoop] = None
        self.__background_task: Optional[Task] = None
        self.__process_resolution = self.__configurator.get("Reminders", "ProcessorResolution", DEFAULT_RESOLUTION)
        self.__process_delay = self.__configurator.get("Reminders", "ProcessorDelay", DEFAULT_DELAY)
    
    async def start(self):
        if not self.__configurator.get("Reminders", "Enable", True):
            self.__log.info("[ReminderProcessor] Reminders are disabled by configuration.")
            return
        
        self.__log.info(f"[ReminderProcessor] Reminders are enabled. {{ Delay = {self.__process_delay}, Resolution = {self.__process_resolution} }}")
        self.__background_loop = AsyncLoop(self.__process_reminders_async, self.__process_delay, self.__process_resolution)
        self.__background_task = asyncio.create_task(self.__background_loop())
    
    async def stop(self):
        loop = self.__background_loop
        if loop: loop.cancel()
        task = self.__background_task
        if task: await task
        self.__log.debug("[ReminderProcessor] Stopped background task.")
    
    async def __process_reminders_async(self):
        self.__log.trace("[ReminderProcessor] Processing reminders...")
        processed_reminders: int = 0
        try:
            reminders = await self.__reminder_repository.get_triggerable()
            for reminder in reminders:
                await self.__messaging.send_dm(reminder.user_id, f"Your reminder: {reminder.message}")

                if reminder.is_repeating:
                    reminder.last_trigger = datetime.utcnow()
                    reminder.recalculate_next_trigger()
                    await self.__reminder_repository.update_next_trigger(reminder.id, reminder.next_trigger)
                else:
                    await self.__reminder_repository.delete(reminder.id)
                processed_reminders += 1
        except Exception as error:
            self.__log.error(f"[ReminderProcessor] Processing failed. Further processing will stop. {{ Reason = UnexpectedError }}", error)
            raise
        finally:
            self.__log.trace(f"[ReminderProcessor] Processed reminders. {{ Count = {processed_reminders} }}")
