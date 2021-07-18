from .insert_builder import InsertBuilder
from .select_builder import SelectBuilder
from .update_builder import UpdateBuilder

class Query:
    @staticmethod
    def insert() -> InsertBuilder:
        return InsertBuilder()
    
    @staticmethod
    def select() -> SelectBuilder:
        return SelectBuilder()

    @staticmethod
    def update() -> UpdateBuilder:
        return UpdateBuilder()
