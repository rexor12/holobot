from .delete_builder import DeleteBuilder
from .insert_builder import InsertBuilder
from .select_builder import SelectBuilder
from .update_builder import UpdateBuilder

class Query:
    """Provides utility methods for building executable queries.

    Note
    ----
    As of the current version, in certain cases, the query builders may result
    in syntactically wrong queries, as syntactical rules between independent
    query parts aren't always enforced. Such may be the case when an `ORDER BY`
    query part is appended to an `INSERT` query part. This is due to performance
    reasons and the simplicity of the builder.
    It's the developer's responsibility to use the feature correctly.
    """

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
