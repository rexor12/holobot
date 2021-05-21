class TooManyTodoItemsError(Exception):
    def __init__(self, item_count: int, *args) -> None:
        super().__init__(*args)
        self.item_count = item_count
    
    @property
    def item_count(self) -> int:
        return self.__item_count

    @item_count.setter
    def item_count(self, value: int) -> None:
        self.__item_count = value
