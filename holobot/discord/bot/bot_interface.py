from abc import ABCMeta, abstractmethod
from hikari import Snowflakeish, User
from typing import Optional

class BotInterface(metaclass=ABCMeta):
    @abstractmethod
    def get_user_by_id(self, user_id: Snowflakeish) -> Optional[User]:
        ...
