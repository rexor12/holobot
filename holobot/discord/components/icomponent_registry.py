from abc import ABCMeta, abstractmethod
from holobot.discord.sdk.components.models import ComponentRegistration
from typing import Optional

class IComponentRegistry(metaclass=ABCMeta):
    @abstractmethod
    def get_registration(self, identifier: str) -> Optional[ComponentRegistration]:
        ...
