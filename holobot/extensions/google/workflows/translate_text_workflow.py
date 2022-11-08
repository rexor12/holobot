from itertools import islice

from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.data_providers import IUserDataProvider
from holobot.discord.sdk.exceptions import UserNotFoundError
from holobot.discord.sdk.models import (
    AutocompleteChoice, Embed, EmbedField, EmbedFooter, InteractionContext
)
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import autocomplete, command
from holobot.discord.sdk.workflows.interactables.models import (
    AutocompleteOption, Cooldown, InteractionResponse, Option
)
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.google.endpoints import IGoogleClient
from holobot.extensions.google.exceptions import QuotaExhaustedError
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.network.exceptions import HttpStatusError

@injectable(IWorkflow)
class TranslateTextWorkflow(WorkflowBase):
    _MAX_TEXT_LENGTH: int = 1000

    def __init__(
        self,
        google_client: IGoogleClient,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        member_data_provider: IMemberDataProvider,
        user_data_provider: IUserDataProvider
    ) -> None:
        super().__init__()
        self.__google_client = google_client
        self.__i18n_provider = i18n_provider
        self.__logger = logger_factory.create(TranslateTextWorkflow)
        self.__member_data_provider = member_data_provider
        self.__user_data_provider = user_data_provider

    @command(
        description="Translates text to another language.",
        name="translate",
        group_name="google",
        options=(
            Option("text", "The text to be translated."),
            Option("target", "The target language. Type to search.", is_autocomplete=True),
            Option("source", "The optional source language. Type to search.", is_autocomplete=True, is_mandatory=False)
        ),
        cooldown=Cooldown(duration=10),
        defer_type=DeferType.DEFER_MESSAGE_CREATION
    )
    async def translate_text(
        self,
        context: InteractionContext,
        text: str,
        target: str,
        source: str | None = None
    ) -> InteractionResponse:
        if not text or len(text) > TranslateTextWorkflow._MAX_TEXT_LENGTH:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.google.translate_text_workflow.invalid_text_length",
                    { "maxlength": TranslateTextWorkflow._MAX_TEXT_LENGTH }
                )
            )

        try:
            translation = await self.__google_client.translate_text(
                text,
                target,
                source
            )
            if not translation:
                return self._reply(
                    content=self.__i18n_provider.get(
                        "extensions.google.translate_text_workflow.no_result"
                    )
                )

            source_language = await self.__google_client.get_language_by_code(
                translation.source_language
            )
            target_language = await self.__google_client.get_language_by_code(
                translation.result_language
            )
            return self._reply(
                content=Embed(
                    title=self.__i18n_provider.get(
                        "extensions.google.translate_text_workflow.embed_title",
                        {
                            "source": source_language.name if source_language else translation.source_language,
                            "target": target_language.name if target_language else translation.result_language
                        }
                    ),
                    footer=EmbedFooter(
                        text=self.__i18n_provider.get(
                            "extensions.google.translate_text_workflow.embed_footer",
                            { "user": context.author_display_name }
                        ),
                        icon_url=await self.__get_user_avatar_url(context)
                    ),
                    fields=[
                        EmbedField(
                            name=self.__i18n_provider.get(
                                "extensions.google.translate_text_workflow.source_text"
                            ),
                            value=translation.source_text,
                            is_inline=False
                        ),
                        EmbedField(
                            name=self.__i18n_provider.get(
                                "extensions.google.translate_text_workflow.result_text"
                            ),
                            value=translation.result_text,
                            is_inline=False
                        )
                    ]
                )
            )
        except InvalidOperationError:
            return self._reply(content=self.__i18n_provider.get("feature_disabled_error"))
        except QuotaExhaustedError:
            return self._reply(content=self.__i18n_provider.get("feature_quota_exhausted_error"))
        except HttpStatusError as error:
            self.__logger.error(
                "An error has occurred during a Google translation HTTP request.",
                error
            )
            return self._reply(content=self.__i18n_provider.get("extensions.google.google_error"))

    @autocomplete(
        command_name="translate",
        group_name="google",
        options=("target", "source")
    )
    async def autocomplete_language(
        self,
        context: InteractionContext,
        options: tuple[AutocompleteOption, ...],
        target_option: AutocompleteOption
    ) -> InteractionResponse:
        try:
            languages = await self.__google_client.get_languages()
            if not isinstance(target_option.value, str) or not target_option.value:
                return self._autocomplete([
                    AutocompleteChoice(
                        name=language.name,
                        value=language.code
                    )
                    for language in islice(languages.values(), 10)
                ])

            target_value = target_option.value.lower()
            choices = []
            for language in languages.values():
                if target_value not in language.name.lower():
                    continue

                choices.append(AutocompleteChoice(
                    name=language.name,
                    value=language.code
                ))

                if len(choices) == 10:
                    break

            return self._autocomplete(choices)
        except:
            return self._autocomplete([])

    async def __get_user_avatar_url(
        self,
        context: InteractionContext
    ) -> str | None:
        try:
            if isinstance(context, ServerChatInteractionContext):
                user = await self.__member_data_provider.get_basic_data_by_id(
                    context.server_id,
                    context.author_id
                )
                return user.avatar_url

            user = await self.__user_data_provider.get_user_data_by_id(context.author_id)
            return user.avatar_url
        except UserNotFoundError:
            return None
