from holobot.sdk.identification import Holoflake

class InvalidItemTypeException(Exception):
    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def server_id(self) -> int:
        return self.__server_id

    @property
    def item_id1(self) -> int | None:
        return self.__item_id1

    @property
    def item_id2(self) -> int | None:
        return self.__item_id2

    @property
    def item_id3(self) -> int | None:
        return self.__item_id3

    def __init__(
        self,
        user_id: int,
        server_id: int,
        item_id1: int | None = None,
        item_id2: int | None = None,
        item_id3: int | None = None,
        message: str | None = None
    ) -> None:
        super().__init__(message)
        self.__user_id = user_id
        self.__server_id = server_id
        self.__item_id1 = item_id1
        self.__item_id2 = item_id2
        self.__item_id3 = item_id3
