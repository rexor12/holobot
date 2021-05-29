from holobot.discord.sdk import ExtensionProviderInterface
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable
from typing import Tuple

@injectable(ExtensionProviderInterface)
class GeneralExtensionProvider(ExtensionProviderInterface):
    def __init__(self, services: ServiceCollectionInterface) -> None:
        super().__init__()

    def get_packages(self) -> Tuple[str, ...]:
        return (
            "holobot.discord.cogs.general",
            "holobot.discord.cogs.google"
        )