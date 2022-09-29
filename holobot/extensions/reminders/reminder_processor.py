import asyncio
from collections.abc import Awaitable

from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.exceptions import ForbiddenError, UserNotFoundError
from holobot.extensions.reminders.models import Reminder
from holobot.sdk.configs import IOptions
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import IStartable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.threading import CancellationToken, CancellationTokenSource
from holobot.sdk.threading.utils import wait
from holobot.sdk.utils import utcnow
from .models import ReminderProcessingOptions
from .repositories import IReminderRepository

@injectable(IStartable)
class ReminderProcessor(IStartable):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        messaging: IMessaging,
        options: IOptions[ReminderProcessingOptions],
        reminder_repository: IReminderRepository
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__logger = logger_factory.create(ReminderProcessor)
        self.__messaging: IMessaging = messaging
        self.__options = options
        self.__reminder_repository: IReminderRepository = reminder_repository
        self.__token_source: CancellationTokenSource | None = None
        self.__background_task: Awaitable[None] | None = None

    async def start(self):
        options = self.__options.value
        if not options.IsEnabled:
            self.__logger.info("Reminders are disabled by configuration")
            return

        self.__logger.info(
            "Reminders are enabled",
            delay=options.Delay,
            resolution=options.Resolution
        )
        self.__token_source = CancellationTokenSource()
        self.__background_task = asyncio.create_task(
            self.__process_reminders(self.__token_source.token)
        )

    async def stop(self):
        if self.__token_source: self.__token_source.cancel()
        if self.__background_task:
            try:
                await self.__background_task
            except asyncio.exceptions.CancelledError:
                pass
        self.__logger.debug("Stopped background task")

    async def __process_reminders(self, token: CancellationToken):
        await wait(self.__options.value.Delay, token)
        while not token.is_cancellation_requested:
            self.__logger.trace("Processing reminders...")
            processed_reminders: int = 0
            try:
                reminders = await self.__reminder_repository.get_triggerable()
                for reminder in reminders:
                    await self.__try_process_reminder(reminder)
                    processed_reminders += 1
            except Exception as error:
                self.__logger.error("Unexpected failure, processing will stop", error)
                raise
            finally:
                self.__logger.trace("Processed reminders", count=processed_reminders)
            await wait(self.__options.value.Resolution, token)

    async def __try_process_reminder(self, reminder: Reminder) -> None:
        try:
            await self.__process_reminder(reminder)
        except (ForbiddenError, UserNotFoundError) as error:
            self.__logger.debug(
                "Failed to send reminder DM, will not retry.",
                exception=error,
                reminder_id=reminder.identifier,
                user_id=reminder.user_id
            )
            await self.__reminder_repository.delete(reminder.identifier)

    async def __process_reminder(self, reminder: Reminder) -> None:
        await self.__messaging.send_private_message(
            reminder.user_id,
            self.__i18n_provider.get(
                (
                    "extensions.reminders.reminder_processor.reminder_dm"
                    if reminder.message
                    else "extensions.reminders.reminder_processor.reminder_dm_no_message"
                ),
                { "message": reminder.message }
            )
        )

        if not reminder.is_repeating:
            await self.__reminder_repository.delete(reminder.identifier)
            return

        reminder.last_trigger = utcnow()
        reminder.recalculate_next_trigger()
        await self.__reminder_repository.update(reminder)
        self.__logger.trace(
            "Processed reminder",
            reminder_id=reminder.identifier,
            next_trigger=reminder.next_trigger
        )
