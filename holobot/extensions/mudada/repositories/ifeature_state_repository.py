from typing import Protocol

from holobot.extensions.mudada.models import FeatureState
from holobot.sdk.database.repositories import IRepository

class IFeatureStateRepository(IRepository[str, FeatureState], Protocol):
    pass
