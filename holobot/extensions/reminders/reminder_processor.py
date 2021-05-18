from .repositories import ReminderRepositoryInterface
from asyncio.tasks import Task
from datetime import datetime
from holobot.configs.configurator_interface import ConfiguratorInterface
from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.display.display_interface import DisplayInterface
from holobot.lifecycle.startable_interface import StartableInterface
from holobot.logging.log_interface import LogInterface
from holobot.threading.async_loop import AsyncLoop
from typing import Optional

import asyncio

DEFAULT_RESOLUTION: int = 60
DEFAULT_DELAY: int = 30

class ReminderProcessor(StartableInterface):
    def __init__(self, service_collection: ServiceCollectionInterface) -> None:
        super().__init__()
        self.__configurator: ConfiguratorInterface = service_collection.get(ConfiguratorInterface)
        self.__display: DisplayInterface = service_collection.get(DisplayInterface)
        self.__log: LogInterface = service_collection.get(LogInterface)
        self.__reminder_repository: ReminderRepositoryInterface = service_collection.get(ReminderRepositoryInterface)
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
        self.__log.debug("[ReminderProcessor] Processing reminders...")
        try:
            reminders = await self.__reminder_repository.get_triggerable()
            for reminder in reminders:
                await self.__display.send_dm(int(reminder.user_id), f"Your reminder: {reminder.message}")

                if reminder.is_repeating:
                    reminder.last_trigger = datetime.utcnow()
                    reminder.recalculate_next_trigger()
                    await self.__reminder_repository.update_next_trigger(reminder.id, reminder.next_trigger)
                else:
                    await self.__reminder_repository.delete(reminder.id)
        except Exception as error:
            self.__log.error(f"[ReminderProcessor] Processing failed. Further processing will stop. {{ Reason = UnexpectedError }}", error)
            raise
