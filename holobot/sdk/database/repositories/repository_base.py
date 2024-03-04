import typing
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Generic, TypeVar, cast

import asyncpg

from holobot.sdk.database.entities import AggregateRoot, Identifier, PrimaryKey, Record
from holobot.sdk.database.exceptions import DatabaseError
from holobot.sdk.database.idatabase_manager import IDatabaseManager
from holobot.sdk.database.isession import ISession
from holobot.sdk.database.iunit_of_work_provider import IUnitOfWorkProvider
from holobot.sdk.database.queries import (
    CompiledQuery, ICompileableQueryPartBuilder, ISupportsExists, ISupportsPagination, Query,
    WhereBuilder, WhereConstraintBuilder
)
from holobot.sdk.database.queries.enums import Equality, Order
from holobot.sdk.database.statuses import CommandComplete
from holobot.sdk.database.statuses.command_tags import DeleteCommandTag, UpdateCommandTag
from holobot.sdk.queries import PaginationResult
from holobot.sdk.threading.utils import COMPLETED_TASK
from holobot.sdk.utils import set_time_zone
from holobot.sdk.utils.dataclass_utils import (
    ObjectTypeDescriptor, ParameterInfo, TypeDescriptor, get_parameter_infos
)
from .constants import MANUALLY_GENERATED_KEY_NAME
from .irepository import IRepository

TIdentifier = TypeVar("TIdentifier", bound=int | str | Identifier)
TRecord = TypeVar("TRecord", bound=Record)
TModel = TypeVar("TModel", bound=AggregateRoot)

@dataclass(kw_only=True, frozen=True)
class PrimaryKeyTypeDescriptor(TypeDescriptor):
    value_type: type

def __resolve_primary_key_type_descriptor(parameter_type: type) -> TypeDescriptor:
    args = typing.get_args(parameter_type)
    return PrimaryKeyTypeDescriptor(value_type=args[0])

_CUSTOM_RESOLVERS: dict[type, Callable[[type], TypeDescriptor]] = {
    PrimaryKey: __resolve_primary_key_type_descriptor
}

class _UnitOfWorkSession(ISession):
    def __init__(self, connection: asyncpg.Connection) -> None:
        super().__init__()
        self.__connection = connection

    @property
    def connection(self) -> asyncpg.Connection:
        return self.__connection

    def _on_dispose(self) -> Awaitable[None]:
        return COMPLETED_TASK

class RepositoryBase(
    ABC,
    Generic[TIdentifier, TRecord, TModel],
    IRepository[TIdentifier, TModel]
):
    """Abstract base class for a repository."""

    _ID_FIELD_NAME = "id"

    @property
    def column_names(self) -> tuple[str, ...]:
        """Gets the names of the table's columns.

        This is a cached value.

        :return: The names of the table's columns.
        :rtype: tuple[str, ...]
        """

        # TODO "This is a cached value."
        return tuple(self.__columns.keys())

    @property
    @abstractmethod
    def record_type(self) -> type[TRecord]:
        """Gets the type of the record.

        This is required, because Python currently doesn't support
        the runtime resolution of generic type arguments.

        :return: The type of the record.
        :rtype: type[TRecord]
        """

    @property
    @abstractmethod
    def model_type(self) -> type[TModel]:
        """Gets the type of the model.

        This is required, because Python currently doesn't support
        the runtime resolution of generic type arguments.

        :return: The type of the model.
        :rtype: type[TModel]
        """

    @property
    @abstractmethod
    def identifier_type(self) -> type[TIdentifier]:
        """Gets the type of the identifier.

        This identifier is shared between the record and the model
        and may only consist of primitive fields.

        This is required, because Python currently doesn't support
        the runtime resolution of generic type arguments.

        :return: The type of the identifier.
        :rtype: type[TIdentifier]
        """

    @property
    @abstractmethod
    def table_name(self) -> str:
        """Gets the name of the table the repository operates on.

        :return: The name of the repository's table.
        :rtype: str
        """

    @property
    def _is_primitive_identifier(self) -> bool:
        return self.identifier_type is str or self.identifier_type is int

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__()
        self._database_manager = database_manager
        self.__unit_of_work_provider = unit_of_work_provider
        self.__columns = {
            parameter_info.name: parameter_info
            for parameter_info in get_parameter_infos(self.record_type, _CUSTOM_RESOLVERS)
        }
        self.__id_columns = {
            name: parameter_info
            for name, parameter_info in self.__columns.items()
            if isinstance(parameter_info.object_type, PrimaryKeyTypeDescriptor)
        }

    async def add(self, model: TModel) -> TIdentifier:
        record = self._map_model_to_record(model)
        is_manually_generated_key = getattr(record, MANUALLY_GENERATED_KEY_NAME, False)
        fields = self._get_fields(record, not is_manually_generated_key)
        async with (session := await self._get_session()):
            identifier_row = await (Query
                .insert()
                .in_table(self.table_name)
                .fields(*fields)
                .returning()
                .columns(*self.__id_columns.keys())
                .compile()
                .fetchrow(session.connection)
            )
            if identifier_row is None:
                raise DatabaseError("Failed to insert a new record.")

            identifier = self._map_query_result_to_identifier(identifier_row)
            model.identifier = identifier

            await self.__try_set_model(model)

            return identifier

    async def get(self, identifier: TIdentifier) -> TModel | None:
        if existing_model := await self.__try_get_model(identifier):
            return existing_model

        async with (session := await self._get_session()):
            builder = Query.select().columns(*self.column_names).from_table(self.table_name).where()
            result = await (self
                ._add_id_filter(builder, identifier)
                .compile()
                .fetchrow(session.connection)
            )

            return (
                self._map_record_to_model(self._map_query_result_to_record(result))
                if result is not None else None
            )

    async def count(self) -> int | None:
        async with (session := await self._get_session()):
            result = await (Query
                .select()
                .column("COUNT(*)")
                .from_table(self.table_name)
                .compile()
                .fetchval(session.connection)
            )

            return result

    async def update(self, model: TModel) -> bool:
        record = self._map_model_to_record(model)
        fields = self._get_fields(record, False)
        async with (session := await self._get_session()):
            builder = Query.update().table(self.table_name).fields(*fields).where()
            result = await (self
                ._add_id_filter(builder, model.identifier)
                .compile()
                .execute(session.connection)
            )
            if not isinstance(result, CommandComplete):
                raise DatabaseError("Failed to update an existing record.")

            await self.__try_set_model(model)

            return cast(CommandComplete[UpdateCommandTag], result).command_tag.rows != 0

    async def delete(self, identifier: TIdentifier) -> int:
        async with (session := await self._get_session()):
            builder = Query.delete().from_table(self.table_name).where()
            result = await (self
                ._add_id_filter(builder, identifier)
                .compile()
                .execute(session.connection)
            )
            if not isinstance(result, CommandComplete):
                raise DatabaseError("Failed to delete a record.")

            await self.__try_remove_model(identifier)

            return cast(CommandComplete[DeleteCommandTag], result).command_tag.rows

    @abstractmethod
    def _map_record_to_model(self, record: TRecord) -> TModel:
        """Maps a record to its domain model counterpart.

        :param record: The record to be mapped.
        :type record: TRecord
        :return: The new instance of the model.
        :rtype: TModel
        """

    @abstractmethod
    def _map_model_to_record(self, model: TModel) -> TRecord:
        """Maps a domain model to its record counterpart.

        :param model: The model to be mapped.
        :type model: TModel
        :return: The new instance of the record.
        :rtype: TRecord
        """

    async def _count_by_filter(
        self,
        filter_builder: Callable[[WhereBuilder], ICompileableQueryPartBuilder[CompiledQuery]]
    ) -> int:
        """Counts the entities matching the specified filter.

        :param filter_builder: A callback that attaches the filter to the query.
        :type filter_builder: Callable[[WhereBuilder], ICompileableQueryPartBuilder[CompiledQuery]]
        :return: The number of entities matching the specified filter.
        :rtype: int
        """

        async with (session := await self._get_session()):
            query = filter_builder(Query
                .select()
                .column("COUNT(*)")
                .from_table(self.table_name)
                .where()
            )
            result = await query.compile().fetchval(session.connection)

            return result or 0

    async def _get_many_by_filter(
        self,
        filter_builder: Callable[[WhereBuilder], ICompileableQueryPartBuilder[CompiledQuery]]
    ) -> tuple[TModel, ...]:
        """Gets multiple entities matching the specified filter.

        :param filter_builder: A callback that attaches the filter to the query.
        :type filter_builder: Callable[[WhereBuilder], ICompileableQueryPartBuilder[CompiledQuery]]
        :return: A sequence of matching models, if any.
        :rtype: tuple[TModel, ...]
        """

        async with (session := await self._get_session()):
            query = filter_builder(Query
                .select()
                .columns(*self.column_names)
                .from_table(self.table_name)
                .where()
            )
            results = await query.compile().fetch(session.connection)

            models = tuple(
                self._map_record_to_model(self._map_query_result_to_record(result))
                for result in results
            )

            for model in models:
                await self.__try_set_model(model)

            return models

    async def _get_by_filter(
        self,
        filter_builder: Callable[[WhereBuilder], ICompileableQueryPartBuilder[CompiledQuery]]
    ) -> TModel | None:
        """Gets an entity matching the specified filter.

        :param filter_builder: A callback that attaches the filter to the query.
        :type filter_builder: Callable[[WhereBuilder], ICompileableQueryPartBuilder[CompiledQuery]]
        :return: If exists, a matching model; otherwise, None.
        :rtype: TModel | None
        """

        async with (session := await self._get_session()):
            query = filter_builder(Query
                .select()
                .columns(*self.column_names)
                .from_table(self.table_name)
                .where()
            )
            result = await query.compile().fetchrow(session.connection)
            if result is None:
                return None

            model = self._map_record_to_model(self._map_query_result_to_record(result))
            await self.__try_set_model(model)

            return model

    async def _exists_by_filter(
        self,
        filter_builder: Callable[[WhereBuilder], ISupportsExists]
    ) -> bool:
        """Determines if an entity matching the specified filter exists.

        :param filter_builder: A callback that attaches the filter to the query.
        :type filter_builder: Callable[[WhereBuilder], ISupportsExists]
        :return: True, if exists.
        :rtype: bool
        """

        async with (session := await self._get_session()):
            query = filter_builder(Query
                .select()
                .column("id")
                .from_table(self.table_name)
                .where()
            )
            result = await query.exists().compile().fetchval(session.connection)

            return bool(result)

    async def _get_many_by_function(
        self,
        function_name: str,
        arguments: tuple[str, ...] = ()
    ) -> tuple[TModel, ...]:
        async with (session := await self._get_session()):
            query = (Query
                .select()
                .columns(*self.column_names)
                .from_function(function_name, arguments)
            )
            results = await query.compile().fetch(session.connection)
            models = tuple(
                self._map_record_to_model(self._map_query_result_to_record(result))
                for result in results
            )

            for model in models:
                await self.__try_set_model(model)

            return models

    async def _delete_by_filter(
        self,
        filter_builder: Callable[[WhereBuilder], WhereConstraintBuilder]
    ) -> int:
        """Deletes all entities matching the specified filter.

        :param filter_builder: A callback that attaches the filter to the query.
        :type filter_builder: Callable[[WhereBuilder], WhereConstraintBuilder]
        :return: The number of entities that have been deleted.
        :rtype: int
        """

        async with (session := await self._get_session()):
            query = filter_builder(Query
                .delete()
                .from_table(self.table_name)
                .where()
            )
            identifier_rows = await (query
                .returning()
                .columns(*self.__id_columns.keys())
                .compile()
                .fetch(session.connection)
            )

            for identifier_row in identifier_rows:
                identifier = self._map_query_result_to_identifier(identifier_row)
                await self.__try_remove_model(identifier)

            return len(identifier_rows)

    async def _update_by_filter(
        self,
        fields: tuple[tuple[str, Any | None, bool], ...],
        filter_builder: Callable[[WhereBuilder], WhereConstraintBuilder]
    ) -> int:
        """Updates all entities matching the specified filter.

        :param fields: The fields to be updated (name, value, is_raw_value).
        :type fields: tuple[tuple[str, Any | None, bool], ...]
        :param filter_builder: A callback that attaches the filter to the query.
        :type filter_builder: Callable[[WhereBuilder], WhereConstraintBuilder]
        :return: The number of entities that have been updated.
        :rtype: int
        """

        async with (session := await self._get_session()):
            query = Query.update().table(self.table_name)
            for column_name, value, is_raw_value in fields:
                query = query.field(column_name, value, is_raw_value)

            query = filter_builder(query.where())
            identifier_rows = await (query
                .returning()
                .columns(*self.__id_columns.keys())
                .compile()
                .fetch(session.connection)
            )

            for identifier_row in identifier_rows:
                identifier = self._map_query_result_to_identifier(identifier_row)
                await self.__try_remove_model(identifier)

            return len(identifier_rows)

    async def _paginate(
        self,
        ordering_columns: tuple[tuple[str, Order], ...],
        page_index: int,
        page_size: int,
        filter_builder: Callable[[WhereBuilder], ISupportsPagination] | None
    ) -> PaginationResult[TModel]:
        """Gets a sequence of models matching the specified filter in a paging manner.

        :param ordering_columns: The columns used for ordering the intermediary results.
        :type ordering_columns: tuple[tuple[str, Order]]
        :param page_index: The index of the page to fetch.
        :type page_index: int
        :param page_size: The size of the pages.
        :type page_size: int
        :param filter_builder: A callback that attaches the filter to the query.
        :type filter_builder: Callable[[WhereBuilder], ISupportsPagination]
        :return: A pagination result containing the matching models.
        :rtype: PaginationResult[TModel]
        """

        async with (session := await self._get_session()):
            query = Query.select().columns(*self.column_names).from_table(self.table_name)
            if filter_builder is not None:
                query = filter_builder(query.where())

            result = await query.paginate(ordering_columns, page_index, page_size).compile().fetch(session.connection)

            return PaginationResult[TModel](
                result.page_index,
                result.page_size,
                result.total_count,
                [
                    self._map_record_to_model(self._map_query_result_to_record(record))
                    for record in result.records
                ]
            )

    def _add_id_filter(self, where_builder: WhereBuilder, identifier: TIdentifier) -> WhereConstraintBuilder:
        """Adds the identifier filter to the query builder.

        This method correctly handles simple primary keys and composite keys.

        :param where_builder: The query builder to modify.
        :type where_builder: WhereBuilder
        :param identifier: The identifier to filter for.
        :type identifier: TIdentifier
        :return: The same query builder with the filter added.
        :rtype: WhereConstraintBuilder
        """

        if isinstance(identifier, Identifier):
            constraint_builder: WhereConstraintBuilder | None = None
            for column_name in self.__id_columns.keys():
                field_value = getattr(identifier, column_name)
                if constraint_builder:
                    constraint_builder = constraint_builder.and_field(
                        column_name, Equality.EQUAL, field_value
                    )
                else:
                    constraint_builder = where_builder.field(
                        column_name, Equality.EQUAL, field_value
                    )
            if not constraint_builder:
                raise ValueError("The specified composite key does not specify any columns.")

            return constraint_builder
        # TODO Make this dynamic instead of the magical _ID_FIELD_NAME.
        return where_builder.field(RepositoryBase._ID_FIELD_NAME, Equality.EQUAL, identifier)

    def _map_query_result_to_record(self, columns: dict[str, Any]) -> TRecord:
        """Maps the specified result of a query to a record.

        :param columns: The fieldsof the query's result.
        :type columns: dict[str, Any]
        :raises TypeError: Raised when the type of one of the values is incorrect.
        :return: A new, filled instance of the record.
        :rtype: TRecord
        """

        arguments = {
            column.name: self._map_query_result_column(column.name, columns, self.__columns)
            for column in self.__columns.values()
        }

        return self.record_type(**arguments)

    def _map_query_result_to_identifier(self, columns: dict[str, Any]) -> TIdentifier:
        arguments = {
            column_name: self._map_query_result_column(column_name, columns, self.__id_columns).value
            for column_name in self.__id_columns.keys()
        }

        return (
            next(iter(arguments.values()))
            if self._is_primitive_identifier
            else self.identifier_type(**arguments)
        )

    def _map_query_result_column(
        self,
        column_name: str,
        record_columns: dict[str, Any],
        model_columns: dict[str, ParameterInfo]
    ) -> Any:
        if not (column := model_columns.get(column_name, None)):
            raise TypeError(f"Cannot find the type descriptor of column '{column_name}'.")

        if isinstance(column.object_type, ObjectTypeDescriptor):
            object_type = column.object_type.value
        elif isinstance(column.object_type, PrimaryKeyTypeDescriptor):
            object_type = PrimaryKey
        else:
            raise TypeError(
                f"Expected the type descriptor of column {column.name} to be an"
                f" ObjectTypeDescriptor, but got {type(column.object_type).__name__}."
            )

        value = record_columns.get(column_name)
        record_value = RepositoryBase.__convert_field_to_model(value, object_type)
        if record_value is None and not column.allows_none:
            if column.default_value:
                record_value = column.default_value
            elif column.default_factory:
                record_value = column.default_factory()

        if (
            record_value is None and not column.allows_none
            or record_value is not None and not isinstance(record_value, object_type)
        ):
            raise TypeError((
                f"Expected '{object_type.__name__}',"
                f" but got '{type(record_value).__name__}'."
            ))

        return record_value

    def _get_fields(
        self,
        record: TRecord,
        ignore_identifier: bool
    ) -> Sequence[tuple[str, Any]]:
        """Gets the column name-value pairs for the specified record.

        :param record: The record to convert.
        :type record: TRecord
        :param ignore_identifier: Whether the identifier column should be ignored.
        :type ignore_identifier: bool
        :return: The column name-value pairs for the specified record.
        :rtype: Sequence[tuple[str, Any]]
        """

        return [
            (
                column.name,
                RepositoryBase.__convert_field_to_record(getattr(record, column.name))
            )
            for column in self.__columns.values()
            if not ignore_identifier or not isinstance(column.object_type, PrimaryKeyTypeDescriptor)
        ]

    async def _get_session(self) -> ISession:
        if unit_of_work := self.__unit_of_work_provider.current:
            return _UnitOfWorkSession(unit_of_work.connection)

        return await self._database_manager.acquire_connection()

    @staticmethod
    def __convert_field_to_model(
        value: Any,
        expected_type: type
    ) -> Any:
        if issubclass(expected_type, Enum):
            return expected_type(value)
        if isinstance(value, datetime):
            datetime_value = cast(datetime, value)
            if not datetime_value.tzinfo:
                return set_time_zone(value, timezone.utc)
        if expected_type is PrimaryKey:
            return PrimaryKey(value)
        return value

    @staticmethod
    def __convert_field_to_record(value: Any) -> Any:
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, datetime):
            datetime_value = cast(datetime, value)
            if datetime_value is not None:
                return set_time_zone(datetime_value, None)
        if isinstance(value, PrimaryKey):
            return value.value
        return value

    def __try_get_model(self, identifier: TIdentifier) -> Awaitable[TModel | None]:
        if not (unit_of_work := self.__unit_of_work_provider.current):
            return COMPLETED_TASK

        return unit_of_work.get(self.model_type, identifier)

    def __try_set_model(self, model: TModel) -> Awaitable[None]:
        if not (unit_of_work := self.__unit_of_work_provider.current):
            return COMPLETED_TASK

        return unit_of_work.set(model)

    def __try_remove_model(self, identifier: TIdentifier) -> Awaitable[None]:
        if unit_of_work := self.__unit_of_work_provider.current:
            return unit_of_work.remove(self.model_type, identifier)

        return COMPLETED_TASK
