from .insert_builder import InsertBuilder
from .update_builder import UpdateBuilder

class Query:
    @staticmethod
    def insert() -> InsertBuilder:
        return InsertBuilder()

    @staticmethod
    def update() -> UpdateBuilder:
        return UpdateBuilder()
