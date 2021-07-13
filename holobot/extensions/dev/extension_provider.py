from holobot.discord.sdk import ExtensionProviderInterface
from holobot.sdk.ioc.decorators import injectable
from typing import Tuple

@injectable(ExtensionProviderInterface)
class ExtensionProvider(ExtensionProviderInterface):
    def __init__(self) -> None:
        super().__init__()

    def get_packages(self) -> Tuple[str, ...]:
        return ("holobot.extensions.dev.cogs.main",)
