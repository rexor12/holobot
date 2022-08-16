from datetime import datetime, timedelta

from .exceptions import InvalidReminderConfigError, InvalidReminderError, TooManyRemindersError
from .models import Reminder, ReminderConfig
from .reminder_manager_interface import ReminderManagerInterface
from .repositories import ReminderRepositoryInterface
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.exceptions import ArgumentError, ArgumentOutOfRangeError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.queries import PaginationResult

@injectable(ReminderManagerInterface)
class ReminderManager(ReminderManagerInterface):
    def __init__(
        self,
        logger_factory: ILoggerFactory,
        reminder_repository: ReminderRepositoryInterface,
        configurator: ConfiguratorInterface
    ) -> None:
        super().__init__()
        self.__logger = logger_factory.create(ReminderManager)
        self.__reminder_repository: ReminderRepositoryInterface = reminder_repository
        self.__reminders_per_user_max: int = configurator.get("Reminders", "RemindersPerUserMax", 5)
        self.__message_length_min: int = configurator.get("Reminders", "MessageLengthMin", 10)
        self.__message_length_max: int = configurator.get("Reminders", "MessageLengthMax", 120)

    async def set_reminder(self, user_id: str, config: ReminderConfig) -> Reminder:
        if not (self.__message_length_min <= len(config.message) <= self.__message_length_max):
            raise ArgumentOutOfRangeError(
                "message",
                str(self.__message_length_min),
                str(self.__message_length_max)
            )
        if config.every_interval is not None and config.in_time is not None:
            raise InvalidReminderConfigError("every", "in")
        if config.in_time is not None and config.at_time is not None:
            raise InvalidReminderConfigError("in", "at")

        await self.__assert_reminder_count(user_id)
        if config.every_interval is not None:
            reminder = await self.__set_recurring_reminder(user_id, config.message, config.every_interval, config.at_time)
        elif config.in_time is not None:
            next_trigger = datetime.utcnow() + config.in_time
            reminder = await self.__set_single_reminder(user_id, config.message, next_trigger)
        elif config.at_time is not None:
            next_trigger = self.__calculate_single_trigger_at(config.at_time)
            reminder = await self.__set_single_reminder(user_id, config.message, next_trigger)
        else:
            raise ArgumentError("occurrence", "Either the frequency or the specific time of the occurrence must be specified.")

        self.__logger.debug("Set new reminder", user_id=user_id, next_trigger=reminder.next_trigger, base_trigger=reminder.base_trigger, repeats=reminder.is_repeating)
        return reminder

    async def delete_reminder(self, user_id: str, reminder_id: int) -> None:
        if user_id is None or len(user_id) == 0:
            raise ArgumentError("user_id", "The user identifier must not be empty.")

        deleted_count = await self.__reminder_repository.delete_by_user(user_id, reminder_id)
        if deleted_count == 0:
            raise InvalidReminderError("The specified reminder doesn't exist or belong to the specified user.")

    async def get_by_user(self, user_id: str, page_index: int, page_size: int) -> PaginationResult[Reminder]:
        return await self.__reminder_repository.get_many(user_id, page_index, page_size)

    async def __assert_reminder_count(self, user_id: str) -> None:
        count = await self.__reminder_repository.count(user_id)
        if count >= self.__reminders_per_user_max:
            raise TooManyRemindersError(count)

    async def __set_recurring_reminder(self, user_id: str, message: str, frequency_time: timedelta, at_time: timedelta | None) -> Reminder:
        reminder = Reminder()
        reminder.user_id = user_id
        reminder.message = message
        reminder.is_repeating = True
        reminder.frequency_time = frequency_time
        reminder.base_trigger = self.__calculate_recurring_base_trigger(frequency_time, at_time)
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

    def __calculate_recurring_base_trigger(self, frequency_time: timedelta, at_time: timedelta | None):
        current_time = datetime.utcnow()
        if at_time is None:
            return current_time

        base_trigger = datetime(current_time.year, current_time.month, current_time.day) + at_time
        return base_trigger - frequency_time if base_trigger > current_time else base_trigger

    def __calculate_single_trigger_at(self, at_time: timedelta) -> datetime:
        # TODO Make this aware of the user's locale. We can't expect random people to deal with UTC.
        # https://discordpy.readthedocs.io/en/stable/api.html#discord.ClientUser.locale
        current_time = datetime.utcnow()
        trigger_time = datetime(current_time.year, current_time.month, current_time.day) + at_time
        return trigger_time + timedelta(1) if trigger_time < current_time else trigger_time
