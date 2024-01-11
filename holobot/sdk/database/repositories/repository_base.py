from abc import ABC, abstractmethod
from collections.abc import Awaitable, Sequence
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Generic, TypeVar, cast

import asyncpg

from holobot.sdk import Lazy
from holobot.sdk.database.aggregate_root import AggregateRoot
from holobot.sdk.database.exceptions import DatabaseError
from holobot.sdk.database.idatabase_manager import IDatabaseManager
from holobot.sdk.database.isession import ISession
from holobot.sdk.database.iunit_of_work_provider import IUnitOfWorkProvider
from holobot.sdk.database.queries import (
    CompiledQuery, ICompileableQueryPartBuilder, ISupportsPagination, Query, WhereBuilder,
    WhereConstraintBuilder
)
from holobot.sdk.database.queries.enums import Equality, Order
from holobot.sdk.database.statuses import CommandComplete
from holobot.sdk.database.statuses.command_tags import DeleteCommandTag, UpdateCommandTag
from holobot.sdk.queries import PaginationResult
from holobot.sdk.threading.utils import COMPLETED_TASK
from holobot.sdk.utils import set_time_zone
from holobot.sdk.utils.dataclass_utils import (
    ObjectTypeDescriptor, ParameterInfo, get_parameter_infos
)
from .constants import MANUALLY_GENERATED_KEY_NAME
from .irepository import IRepository
from .record import Record

TIdentifier = TypeVar("TIdentifier", int, str)
TRecord = TypeVar("TRecord", bound=Record)
TModel = TypeVar("TModel", bound=AggregateRoot)

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

        return self.__column_names.value

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
    def table_name(self) -> str:
        """Gets the name of the table the repository operates on.

        :return: The name of the repository's table.
        :rtype: str
        """

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__()
        self._database_manager = database_manager
        self.__unit_of_work_provider = unit_of_work_provider
        self.__columns = Lazy[tuple[ParameterInfo, ...]](
            lambda: tuple(get_parameter_infos(self.record_type))
        )
        self.__column_names = Lazy[tuple[str, ...]](
            lambda: self.__get_column_names()
        )

    async def add(self, model: TModel) -> TIdentifier:
        record = self._map_model_to_record(model)
        is_manually_generated_key = getattr(record, MANUALLY_GENERATED_KEY_NAME, False)
        fields = self._get_fields(record, not is_manually_generated_key)
        async with (session := await self._get_session()):
            identifier = await (Query
                .insert()
                .in_table(self.table_name)
                .fields(*fields)
                .returning()
                .column(RepositoryBase._ID_FIELD_NAME)
                .compile()
                .fetchval(session.connection)
            )
            if identifier is None:
                raise DatabaseError("Failed to insert a new record.")

            await self.__try_set_model(model)

            return identifier

    async def get(self, identifier: TIdentifier) -> TModel | None:
        if existing_model := await self.__try_get_model(identifier):
            return existing_model

        async with (session := await self._get_session()):
            result = await (Query
                .select()
                .columns(*self.column_names)
                .from_table(self.table_name)
                .where()
                .field(RepositoryBase._ID_FIELD_NAME, Equality.EQUAL, identifier)
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
            result = await (Query
                .update()
                .table(self.table_name)
                .fields(*fields)
                .where()
                .field(RepositoryBase._ID_FIELD_NAME, Equality.EQUAL, record.id)
                .compile()
                .execute(session.connection)
            )
            if not isinstance(result, CommandComplete):
                raise DatabaseError("Failed to update an existing record.")

            await self.__try_set_model(model)

            return cast(CommandComplete[UpdateCommandTag], result).command_tag.rows != 0

    async def delete(self, identifier: TIdentifier) -> int:
        async with (session := await self._get_session()):
            result = await (Query
                .delete()
                .from_table(self.table_name)
                .where()
                .field(RepositoryBase._ID_FIELD_NAME, Equality.EQUAL, identifier)
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
            results = await (query
                .returning()
                .column(RepositoryBase._ID_FIELD_NAME)
                .compile()
                .fetch(session.connection)
            )

            for result in results:
                await self.__try_remove_model(
                    cast(TIdentifier, result.get(RepositoryBase._ID_FIELD_NAME))
                )

            return len(results)

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

    def _map_query_result_to_record(self, columns: dict[str, Any]) -> TRecord:
        """Maps the specified result of a query to a record.

        :param columns: The fieldsof the query's result.
        :type columns: dict[str, Any]
        :raises TypeError: Raised when the type of one of the values is incorrect.
        :return: A new, filled instance of the record.
        :rtype: TRecord
        """

        arguments = dict[str, Any]()
        for column in self.__columns.value:
            if not isinstance(column.object_type, ObjectTypeDescriptor):
                raise TypeError(
                    f"Expected the type descriptor of column {column.name} to be an"
                    f"ObjectTypeDescriptor, but got {type(column.object_type).__name__}."
                )

            raw_value = columns.get(column.name)
            record_value = RepositoryBase.__convert_field_to_model(
                raw_value,
                column.object_type.value
            )
            if record_value is None and not column.allows_none:
                if column.default_value:
                    record_value = column.default_value
                elif column.default_factory:
                    record_value = column.default_factory()

            if (
                record_value is None and not column.allows_none
                or record_value is not None and not isinstance(record_value, column.object_type.value)
            ):
                raise TypeError((
                    f"Expected '{column.object_type.value.__name__}',"
                    f" but got '{type(record_value).__name__}'."
                ))

            arguments[column.name] = record_value

        return self.record_type(**arguments)

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
            for column in self.__columns.value
            if not ignore_identifier or column.name != RepositoryBase._ID_FIELD_NAME
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
        return value

    @staticmethod
    def __convert_field_to_record(value: Any) -> Any:
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, datetime):
            datetime_value = cast(datetime, value)
            if datetime_value is not None:
                return set_time_zone(datetime_value, None)
        return value

    def __get_column_names(self) -> tuple[str, ...]:
        return tuple(column.name for column in self.__columns.value)

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
