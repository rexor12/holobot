from datetime import datetime, timedelta, timezone
from typing import cast

from holobot.extensions.reminders.enums import ReminderLocation
from holobot.sdk.configs import IOptions
from holobot.sdk.exceptions import ArgumentError, ArgumentOutOfRangeError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.queries import PaginationResult
from holobot.sdk.utils import utcnow
from .exceptions import InvalidReminderConfigError, InvalidReminderError, TooManyRemindersError
from .ireminder_manager import IReminderManager
from .models import Reminder, ReminderConfig, ReminderOptions
from .repositories import IReminderRepository

@injectable(IReminderManager)
class ReminderManager(IReminderManager):
    def __init__(
        self,
        logger_factory: ILoggerFactory,
        options: IOptions[ReminderOptions],
        reminder_repository: IReminderRepository
    ) -> None:
        super().__init__()
        self.__logger = logger_factory.create(ReminderManager)
        self.__reminder_repository = reminder_repository
        self.__options = options

    async def set_reminder(self, user_id: str, config: ReminderConfig) -> Reminder:
        options = self.__options.value
        ReminderManager.__assert_message(options, config.message)
        if config.every_interval is not None and config.in_time is not None:
            raise InvalidReminderConfigError("every", "in")
        if config.in_time is not None and config.at_time is not None:
            raise InvalidReminderConfigError("in", "at")

        await self.__assert_reminder_count(user_id)
        if config.every_interval is not None:
            reminder = await self.__set_recurring_reminder(user_id, config)
        elif config.in_time is not None:
            next_trigger = utcnow() + config.in_time
            reminder = await self.__set_single_reminder(
                user_id,
                config,
                next_trigger
            )
        elif config.at_time is not None:
            next_trigger = self.__calculate_single_trigger_at(config.at_time)
            reminder = await self.__set_single_reminder(
                user_id,
                config,
                next_trigger
            )
        else:
            raise ArgumentError("occurrence", "Either the frequency or the specific time of the occurrence must be specified.")

        self.__logger.debug("Set new reminder", user_id=user_id, next_trigger=reminder.next_trigger, base_trigger=reminder.base_trigger, repeats=reminder.is_repeating)
        return reminder

    async def delete_reminder(self, user_id: str, reminder_id: int) -> None:
        if not user_id:
            raise ArgumentError("user_id", "The user identifier must not be empty.")

        deleted_count = await self.__reminder_repository.delete_by_user(user_id, reminder_id)
        if deleted_count == 0:
            raise InvalidReminderError("The specified reminder doesn't exist or belong to the specified user.")

    async def get_by_user(self, user_id: str, page_index: int, page_size: int) -> PaginationResult[Reminder]:
        return await self.__reminder_repository.get_many(user_id, page_index, page_size)

    @staticmethod
    def __assert_message(
        options: ReminderOptions,
        message: str | None
    ) -> None:
        if options.MessageLengthMin == 0:
            return

        message_length = len(message) if message else 0
        if not (options.MessageLengthMin <= message_length <= options.MessageLengthMax):
            raise ArgumentOutOfRangeError(
                "message",
                str(options.MessageLengthMin),
                str(options.MessageLengthMax)
            )

    async def __assert_reminder_count(self, user_id: str) -> None:
        count = await self.__reminder_repository.count_by_user(user_id)
        if count >= self.__options.value.RemindersPerUserMax:
            raise TooManyRemindersError(count)

    async def __set_recurring_reminder(
        self,
        user_id: str,
        config: ReminderConfig
    ) -> Reminder:
        reminder = Reminder(
            user_id=user_id,
            server_id=config.server_id,
            channel_id=config.channel_id,
            message=config.message,
            location=config.location,
            is_repeating=True,
            frequency_time=cast(timedelta, config.every_interval),
            base_trigger=self.__calculate_recurring_base_trigger(
                cast(timedelta, config.every_interval),
                config.at_time
            )
        )
        reminder.recalculate_next_trigger()
        reminder.identifier = await self.__reminder_repository.add(reminder)
        return reminder

    async def __set_single_reminder(
        self,
        user_id: str,
        config: ReminderConfig,
        next_trigger: datetime
    ) -> Reminder:
        reminder = Reminder(
            user_id=user_id,
            server_id=config.server_id,
            channel_id=config.channel_id,
            message=config.message,
            location=config.location,
            next_trigger=next_trigger
        )
        reminder.identifier = await self.__reminder_repository.add(reminder)
        return reminder

    def __calculate_recurring_base_trigger(self, frequency_time: timedelta, at_time: timedelta | None):
        current_time = utcnow()
        if at_time is None:
            return current_time

        base_trigger = datetime(current_time.year, current_time.month, current_time.day, tzinfo=timezone.utc) + at_time
        return base_trigger - frequency_time if base_trigger > current_time else base_trigger

    def __calculate_single_trigger_at(self, at_time: timedelta) -> datetime:
        # TODO Make this aware of the user's locale. We can't expect random people to deal with UTC.
        # https://discordpy.readthedocs.io/en/stable/api.html#discord.ClientUser.locale
        current_time = utcnow()
        trigger_time = datetime(current_time.year, current_time.month, current_time.day, tzinfo=timezone.utc) + at_time
        return trigger_time + timedelta(1) if trigger_time < current_time else trigger_time
