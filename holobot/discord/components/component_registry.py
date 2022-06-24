from .icomponent_registry import IComponentRegistry
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.components.models import ComponentRegistration
from holobot.sdk.ioc.decorators import injectable
from typing import Dict, Optional, Tuple

@injectable(IComponentRegistry)
class CommandRegistry(IComponentRegistry):
    def __init__(
        self,
        commands: Tuple[CommandInterface, ...]
    ) -> None:
        super().__init__()
        self.__registrations: Dict[str, ComponentRegistration] = CommandRegistry.__get_registrations(commands)

    def get_registration(self, identifier: str) -> Optional[ComponentRegistration]:
        return self.__registrations.get(identifier)

    @staticmethod
    def __get_registrations(
        commands: Tuple[CommandInterface, ...]
    ) -> Dict[str, ComponentRegistration]:
        registrations = {}
        for command in commands:
            for registration in command.components:
                registrations[registration.id] = registration

        return registrations
