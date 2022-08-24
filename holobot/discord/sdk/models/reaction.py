class Reaction:
    def __init__(self, emoji_id: str, owner_id: str | None = None, message_id: str | None = None) -> None:
        """Initializes a new instance of `Reaction`.

        Initializes a new instance of `Reaction` with the associated properties.

        Parameters
        ----------
        emoji_id : str
            The identifier of the associated emoji.

        owner_id : str
            The identifier of the user the reaction belongs to.
        """

        self.emoji_id = emoji_id
        self.owner_id = owner_id
        self.message_id = message_id

    @property
    def emoji_id(self) -> str:
        """Gets the identifier of the emoji."""

        return self.__emoji_id

    @emoji_id.setter
    def emoji_id(self, value: str) -> None:
        """Sets the identifier of the emoji."""

        self.__emoji_id = value

    @property
    def owner_id(self) -> str | None:
        """Gets the identifier of the user the reaction belongs to."""

        return self.__owner_id

    @owner_id.setter
    def owner_id(self, value: str | None) -> None:
        """Sets the identifier of the user the reaction belongs to."""

        self.__owner_id = value

    @property
    def message_id(self) -> str | None:
        """Gets the identifier of the message the reaction belongs to."""

        return self.__message_id

    @message_id.setter
    def message_id(self, value: str | None) -> None:
        """Sets the identifier of the message the reaction belongs to."""

        self.__message_id = value
