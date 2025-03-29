from collections.abc import Awaitable
from typing import cast

from holobot.extensions.general.enums import ItemType
from holobot.extensions.general.models.items import (
    BackgroundItem, BadgeItem, CurrencyItem, ItemBase, UserItem, WalletWithDetailsDto
)
from holobot.extensions.general.models.user_profiles import UserProfileBackgroundInfo
from holobot.extensions.general.repositories.records.items import (
    BackgroundItemStorageModel, BadgeItemStorageModel, CurrencyItemStorageModel,
    ItemStorageModelBase, UserItemRecord
)
from holobot.extensions.general.sdk.items.models import UserItemId
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.queries import WhereBuilder, WhereConstraintBuilder
from holobot.sdk.database.queries.constraints import column_expression, or_expression
from holobot.sdk.database.queries.enums import Connector, Equality, Order
from holobot.sdk.database.queries.query import Query
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.identification import Holoflake
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from holobot.sdk.serialization import JsonSerializer
from .iuser_item_repository import IUserItemRepository

_SERIALIZER = JsonSerializer({
    CurrencyItemStorageModel,
    BadgeItemStorageModel,
    BackgroundItemStorageModel
})

def get_item_info(item: ItemBase) -> tuple[ItemType, int | None, int | None, int | None]:
    if isinstance(item, CurrencyItem):
        return (ItemType.CURRENCY, item.currency_id, None, None)
    if isinstance(item, BadgeItem):
        return (ItemType.BADGE, item.badge_id.badge_id, None, None)
    if isinstance(item, BackgroundItem):
        return (ItemType.BACKGROUND, item.background_id, None, None)
    raise TypeError(f"Unknown item type '{type(item).__name__}'.")

def item_to_storage_model(item: ItemBase) -> ItemStorageModelBase:
    if isinstance(item, CurrencyItem):
        return CurrencyItemStorageModel(
            count=item.count,
            currency_id=item.currency_id
        )
    if isinstance(item, BadgeItem):
        return BadgeItemStorageModel(
            count=item.count,
            badge_id=item.badge_id,
            unlocked_at=item.unlocked_at
        )
    if isinstance(item, BackgroundItem):
        return BackgroundItemStorageModel(
            count=item.count,
            background_id=item.background_id
        )
    raise TypeError(f"Unknown item type '{type(item).__name__}'.")

def storage_model_to_item(item: ItemStorageModelBase) -> ItemBase:
    if isinstance(item, CurrencyItemStorageModel):
        return CurrencyItem(
            count=item.count,
            currency_id=item.currency_id
        )
    if isinstance(item, BadgeItemStorageModel):
        return BadgeItem(
            count=item.count,
            badge_id=item.badge_id,
            unlocked_at=item.unlocked_at
        )
    if isinstance(item, BackgroundItemStorageModel):
        return BackgroundItem(
            count=item.count,
            background_id=item.background_id
        )
    raise TypeError(f"Unknown item type '{type(item).__name__}'.")

@injectable(IUserItemRepository)
class UserItemRepository(
    RepositoryBase[UserItemId, UserItemRecord, UserItem],
    IUserItemRepository
):
    @property
    def record_type(self) -> type[UserItemRecord]:
        return UserItemRecord

    @property
    def model_type(self) -> type[UserItem]:
        return UserItem

    @property
    def identifier_type(self) -> type[UserItemId]:
        return UserItemId

    @property
    def table_name(self) -> str:
        return "user_items"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    #region Backgrounds

    def get_background(
        self,
        user_id: int,
        background_id: int
    ) -> Awaitable[UserItem | None]:
        return self._get_by_filter(lambda where: (where
            .fields(
                Connector.AND,
                ("item_type", Equality.EQUAL, ItemType.BACKGROUND),
                ("user_id", Equality.EQUAL, user_id),
                ("item_id1", Equality.EQUAL, background_id)
            )
        ))

    def paginate_backgrounds(
        self,
        user_id: int,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[UserItem]]:
        return self._paginate(
            (("serial_id", Order.ASCENDING),),
            page_index,
            page_size,
            lambda where: where.fields(
                Connector.AND,
                ("item_type", Equality.EQUAL, ItemType.BACKGROUND),
                ("user_id", Equality.EQUAL, user_id)
            )
        )

    def background_exists(
        self,
        user_id: int,
        background_id: int
    ) -> Awaitable[bool]:
        return self._exists_by_filter(
            lambda where: where.fields(
                Connector.AND,
                ("item_type", Equality.EQUAL, ItemType.BACKGROUND),
                ("user_id", Equality.EQUAL, user_id),
                ("item_id1", Equality.EQUAL, background_id)
            )
        )

    async def paginate_background_infos(
        self,
        user_id: int,
        page_index: int,
        page_size: int
    ) -> PaginationResult[UserProfileBackgroundInfo]:
        async with (session := await self._get_session()):
            query = (Query
                .select()
                .columns("ui.serial_id", "upb.code", "upb.name")
                .from_table(self.table_name, "ui")
                .join("user_profile_backgrounds", "ui.item_id1", "upb.id", "upb", "INNER")
                .where()
                .fields(
                    Connector.AND,
                    ("ui.item_type", Equality.EQUAL, ItemType.BACKGROUND),
                    ("ui.user_id", Equality.EQUAL, user_id)
                )
            )

            result = await query.paginate(
                (("serial_id", Order.ASCENDING),),
                page_index,
                page_size
            ).compile().fetch(session.connection)

            return PaginationResult[UserProfileBackgroundInfo](
                result.page_index,
                result.page_size,
                result.total_count,
                [
                    UserProfileBackgroundInfo(
                        code=record["code"],
                        name=record["name"]
                    )
                    for record in result.records
                ]
            )

    #endregion

    #region Badges

    def get_badge(
        self,
        server_id: int,
        user_id: int,
        badge_id: int
    ) -> Awaitable[UserItem | None]:
        return self._get_by_filter(lambda where: (where
            .fields(
                Connector.AND,
                ("item_type", Equality.EQUAL, ItemType.BADGE),
                ("server_id", Equality.EQUAL, server_id),
                ("user_id", Equality.EQUAL, user_id),
                ("item_id1", Equality.EQUAL, badge_id)
            )
        ))

    def paginate_badges(
        self,
        user_id: int,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[UserItem]]:
        return self._paginate(
            (("serial_id", Order.ASCENDING),),
            page_index,
            page_size,
            lambda where: where.fields(
                Connector.AND,
                ("item_type", Equality.EQUAL, ItemType.BADGE),
                ("user_id", Equality.EQUAL, user_id)
            )
        )

    def badge_exists(
        self,
        server_id: int,
        user_id: int,
        badge_id: int
    ) -> Awaitable[bool]:
        return self._exists_by_filter(
            lambda where: where.fields(
                Connector.AND,
                ("item_type", Equality.EQUAL, ItemType.BADGE),
                ("server_id", Equality.EQUAL, server_id),
                ("user_id", Equality.EQUAL, user_id),
                ("item_id1", Equality.EQUAL, badge_id)
            )
        )

    #endregion

    #region Currencies

    def get_wallet(
        self,
        user_id: int,
        server_id: int,
        currency_id: int
    ) -> Awaitable[UserItem | None]:
        return self._get_by_filter(lambda where: (where
            .fields(
                Connector.AND,
                ("item_type", Equality.EQUAL, ItemType.CURRENCY),
                ("server_id", Equality.EQUAL, server_id),
                ("user_id", Equality.EQUAL, user_id),
                ("item_id1", Equality.EQUAL, currency_id)
            )
        ))

    def get_wallets(
        self,
        user_id: int,
        server_id: int,
        include_global: bool = False
    ) -> Awaitable[tuple[UserItem, ...]]:
        return self._get_many_by_filter(lambda where: UserItemRepository.__build_wallet_constraint(
            where,
            user_id,
            server_id,
            include_global
        ))

    async def paginate_wallets_with_details(
        self,
        user_id: int,
        server_id: int,
        include_global: bool = False,
        page_index: int = 0,
        page_size: int = 5
    ) -> PaginationResult[WalletWithDetailsDto]:
        async with (session := await self._get_session()):
            query = (Query
                .select()
                .columns(
                    "user_items.user_id",
                    "user_items.item_id1",
                    "user_items.server_id",
                    "user_items.count",
                    "currencies.name",
                    "currencies.emoji_id",
                    "currencies.emoji_name"
                )
                .from_table("user_items")
                .join("currencies", "user_items.item_id1", "currencies.id", join_type="INNER")
            )
            query = UserItemRepository.__build_wallet_constraint(
                query.where(),
                user_id,
                server_id,
                include_global
            )
            result = await query.paginate(
                (("server_id", Order.ASCENDING),),
                page_index,
                page_size
            ).compile().fetch(session.connection)

            return PaginationResult(
                result.page_index,
                result.page_size,
                result.total_count,
                [
                    WalletWithDetailsDto(
                        user_id=int(record.get("user_id", 0)),
                        server_id=int(record.get("server_id", 0)),
                        currency_id=int(record.get("item_id1", 0)),
                        amount=int(record.get("count", "0")),
                        currency_name=record.get("name", ""),
                        currency_emoji_id=int(record.get("emoji_id", "0")),
                        currency_emoji_name=record.get("emoji_name", "")
                    )
                    for record in result.records
                ]
            )

    #endregion

    def _map_record_to_model(self, record: UserItemRecord) -> UserItem:
        return UserItem(
            identifier=UserItemId(
                user_id=record.user_id.value,
                server_id=record.server_id.value,
                serial_id=Holoflake(record.serial_id.value)
            ),
            item=cast(
                ItemBase,
                storage_model_to_item(
                    cast(
                        ItemStorageModelBase,
                        _SERIALIZER.deserialize2(record.item_data_json)
                    )
                )
            )
        )

    def _map_model_to_record(self, model: UserItem) -> UserItemRecord:
        item_type, item_id1, item_id2, item_id3 = get_item_info(model.item)

        return UserItemRecord(
            user_id=PrimaryKey(model.identifier.user_id),
            server_id=PrimaryKey(model.identifier.server_id),
            serial_id=PrimaryKey(model.identifier.serial_id),
            item_type=item_type,
            item_id1=item_id1,
            item_id2=item_id2,
            item_id3=item_id3,
            count=model.item.count,
            item_data_json=_SERIALIZER.serialize(
                item_to_storage_model(model.item)
            )
        )

    @staticmethod
    def __build_wallet_constraint(
        where: WhereBuilder,
        user_id: int,
        server_id: int | None,
        include_global: bool
    ) -> WhereConstraintBuilder:
        constraint = (where
            .field("user_items.item_type", Equality.EQUAL, ItemType.CURRENCY)
            .and_field("user_items.user_id", Equality.EQUAL, user_id)
            .and_field("user_items.count", Equality.GREATER, 0)
        )
        if server_id == 0:
            return constraint

        if include_global:
            constraint = constraint.and_expression(
                or_expression(
                    column_expression("user_items.server_id", Equality.EQUAL, server_id),
                    column_expression("user_items.server_id", Equality.EQUAL, 0)
                )
            )
        else:
            constraint = constraint.and_field("user_items.server_id", Equality.EQUAL, server_id)

        return constraint
