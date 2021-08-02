from .delete_builder import DeleteBuilder
from .insert_builder import InsertBuilder
from .select_builder import SelectBuilder
from .update_builder import UpdateBuilder

class Query:
    """Provides utility methods for building executable queries."""

    @staticmethod
    def insert() -> InsertBuilder:
        return InsertBuilder()
    
    @staticmethod
    def select() -> SelectBuilder:
        return SelectBuilder()

    @staticmethod
    def update() -> UpdateBuilder:
        return UpdateBuilder()
    
    @staticmethod
    def delete() -> DeleteBuilder:
        return DeleteBuilder()
