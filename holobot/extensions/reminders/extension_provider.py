from holobot.discord.sdk import ExtensionProviderInterface
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable
from typing import Tuple

@injectable(ExtensionProviderInterface)
class ExtensionProvider(ExtensionProviderInterface):
    def __init__(self, services: ServiceCollectionInterface) -> None:
        super().__init__()

    def get_packages(self) -> Tuple[str, ...]:
        return ("holobot.extensions.reminders.cogs.main",)
