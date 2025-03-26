from holobot.extensions.general.sdk.badges.models import BadgeId

class BadgeNotFoundException(Exception):
    @property
    def badge_id(self) -> BadgeId:
        return self.__badge_id

    def __init__(
        self,
        badge_id: BadgeId,
        message: str | None = None
    ) -> None:
        super().__init__(message)
        self.__badge_id = badge_id
