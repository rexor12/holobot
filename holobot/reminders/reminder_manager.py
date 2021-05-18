from datetime import datetime, timedelta
from holobot.configs.configurator_interface import ConfiguratorInterface
from holobot.dependency_injection.service_collection_interface import ServiceCollectionInterface
from holobot.logging.log_interface import LogInterface
from holobot.reminders.enums.frequency_type import FrequencyType
from holobot.reminders.exceptions.ArgumentError import ArgumentError
from holobot.reminders.exceptions.TooManyRemindersError import TooManyRemindersError
from holobot.reminders.models.reminder import Reminder
from holobot.reminders.models.reminder_config import ReminderConfig
from holobot.reminders.reminder_manager_interface import ReminderManagerInterface
from holobot.reminders.repositories.reminder_repository_interface import ReminderRepositoryInterface

MAX_REMINDERS_PER_USER = 3

class ReminderManager(ReminderManagerInterface):
    def __init__(self, service_collection: ServiceCollectionInterface) -> None:
        super().__init__()
        self.__log: LogInterface = service_collection.get(LogInterface)
        self.__reminder_repository: ReminderRepositoryInterface = service_collection.get(ReminderRepositoryInterface)
        configurator: ConfiguratorInterface = service_collection.get(ConfiguratorInterface)
        self.__message_length_min: int = configurator.get("Reminders", "MessageLengthMin", 10)
        self.__message_length_max: int = configurator.get("Reminders", "MessageLengthMax", 120)
        
    async def set_reminder(self, user_id: str, config: ReminderConfig) -> Reminder:
        if not (self.__message_length_min <= len(config.message) <= self.__message_length_max):
            raise ArgumentError("message", f"The length of the message must be between {self.__message_length_min} and {self.__message_length_max} characters.")
        
        await self.__assert_reminder_count(user_id)
        if config.every_interval is not None:
            reminder = await self.__set_recurring_reminder(user_id, config.message, config.every_interval)
        elif config.in_time is not None:
            next_trigger = datetime.utcnow() + config.in_time
            reminder = await self.__set_single_reminder(user_id, config.message, next_trigger)
        elif config.at_time is not None:
            next_trigger = self.__calculate_single_trigger_at(config.at_time)
            reminder = await self.__set_single_reminder(user_id, config.message, next_trigger)
        else:
            raise ArgumentError("occurrence", "Either the frequency or the specific time of the occurrence must be specified.")

        self.__log.debug(f"[ReminderManager] Set new reminder. {{ UserId = {user_id}, NextTrigger = {reminder.next_trigger} }}")
        return reminder

    async def __assert_reminder_count(self, user_id: str) -> None:
        count = await self.__reminder_repository.count(user_id)
        if count >= MAX_REMINDERS_PER_USER:
            raise TooManyRemindersError(count)
    
    async def __set_recurring_reminder(self, user_id: str, message: str, frequency_time: timedelta) -> Reminder:
        reminder = Reminder()
        reminder.user_id = user_id
        reminder.message = message
        reminder.is_repeating = True
        reminder.frequency_type = FrequencyType.SPECIFIC
        reminder.frequency_time = frequency_time
        reminder.recalculate_next_trigger()
        await self.__reminder_repository.store(reminder)
        return reminder
    
    async def __set_single_reminder(self, user_id: str, message: str, next_trigger: datetime) -> Reminder:
        reminder = Reminder()
        reminder.user_id = user_id
        reminder.message = message
        reminder.next_trigger = next_trigger
        await self.__reminder_repository.store(reminder)
        return reminder
    
    def __calculate_single_trigger_at(self, time_at: timedelta) -> datetime:
        # TODO Make this aware of the user's locale. We can't expect random people to deal with UTC.
        # https://discordpy.readthedocs.io/en/stable/api.html#discord.ClientUser.locale
        current_time = datetime.utcnow()
        trigger_time = datetime(current_time.year, current_time.month, current_time.day) + time_at
        if trigger_time < current_time:
            return trigger_time + timedelta(1)
        return trigger_time
