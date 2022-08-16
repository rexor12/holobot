from datetime import datetime

import tzlocal

from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.data_providers import IBotDataProvider
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.system import IEnvironment

@injectable(IWorkflow)
class ViewBotInfoWorkflow(WorkflowBase):
    def __init__(
        self,
        bot_data_provider: IBotDataProvider,
        environment: IEnvironment,
        i18n_provider: II18nProvider
    ) -> None:
        super().__init__()
        self.__bot_data_provider = bot_data_provider
        self.__environment = environment
        self.__i18n_provider = i18n_provider

    @command(description="Displays some information about the bot.", name="info")
    async def view_bot_info(
        self,
        context: ServerChatInteractionContext
    ) -> InteractionResponse:
        current_time = datetime.now(tzlocal.get_localzone())
        return InteractionResponse(
            action=ReplyAction(content=Embed(
                title=self.__i18n_provider.get(
                    "extensions.general.view_bot_info_workflow.embed_title"
                ),
                description=self.__i18n_provider.get(
                    "extensions.general.view_bot_info_workflow.embed_description"
                ),
                thumbnail_url=self.__bot_data_provider.get_avatar_url(),
                fields=[
                    EmbedField(
                        self.__i18n_provider.get(
                            "extensions.general.view_bot_info_workflow.general_field"
                        ),
                        self.__i18n_provider.get(
                            "extensions.general.view_bot_info_workflow.general_value",
                            {
                                "version": str(self.__environment.version),
                                "latency": self.__bot_data_provider.get_latency(),
                                "servers": self.__bot_data_provider.get_server_count(),
                                "server_time": current_time
                            }
                        ),
                        False
                    ),
                    EmbedField(
                        self.__i18n_provider.get(
                            "extensions.general.view_bot_info_workflow.project_home"
                        ),
                        "https://github.com/rexor12/holobot",
                        False
                    ),
                    EmbedField(
                        self.__i18n_provider.get(
                            "extensions.general.view_bot_info_workflow.bug_reports"
                        ),
                        "https://github.com/rexor12/holobot/issues",
                        False
                    )
                ],
                footer=EmbedFooter(
                    self.__i18n_provider.get(
                        "extensions.general.view_bot_info_workflow.embed_footer"
                    ),
                    "https://avatars.githubusercontent.com/u/15330052"
                )
            ))
        )
