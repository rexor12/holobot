from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.extensions.giveaways import IScraperManager
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class ResetScraperWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        scraper_manager : IScraperManager
    ) -> None:
        super().__init__(
            required_permissions=Permission.ADMINISTRATOR
        )
        self.__i18n_provider = i18n_provider
        self.__scraper_manager = scraper_manager

    @command(
        description="Forces a giveaway scraper to be run again on the next tick.",
        name="resetscraper",
        group_name="dev",
        options=(
            Option("scraper_name", "The name of the scraper.", OptionType.STRING),
        ),
        # TODO Provide development server ID dynamically. (#135)
        server_ids={"999259836439081030"}
    )
    async def set_maintenance_mode(
        self,
        context: InteractionContext,
        scraper_name: str
    ) -> InteractionResponse:
        await self.__scraper_manager.invalidate_scrape_time(scraper_name)
        return self._reply(
            content=self.__i18n_provider.get("extensions.giveaways.reset_scraper_workflow.done")
        )
