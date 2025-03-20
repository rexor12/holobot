from hikari import PartialInteraction

class UnknownInteractionTypeException(Exception):
    @property
    def interaction_type(self) -> type[PartialInteraction]:
        return self.__interaction_type

    def __init__(
        self,
        interaction_type: type[PartialInteraction],
        message: str | None = None
    ) -> None:
        super().__init__(message)
        self.__interaction_type = interaction_type
