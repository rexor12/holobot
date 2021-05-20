from datetime import datetime

class TodoItem:
    def __init__(self) -> None:
        self.id = -1
        self.user_id = ""
        self.created_at = datetime.utcnow()
        self.message = ""
    
    @property
    def id(self) -> int:
        return self.__id
    
    @id.setter
    def id(self, id: int) -> None:
        self.__id = id

    @property
    def user_id(self) -> str:
        return self.__user_id
    
    @user_id.setter
    def user_id(self, user_id: str) -> None:
        self.__user_id = user_id
    
    @property
    def created_at(self) -> datetime:
        return self.__created_at

    @created_at.setter
    def created_at(self, value: datetime) -> None:
        self.__created_at = value
    
    @property
    def message(self) -> str:
        return self.__message

    @message.setter
    def message(self, message: str) -> None:
        self.__message = message
