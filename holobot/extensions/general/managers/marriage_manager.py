from collections.abc import Awaitable
from datetime import timedelta

from holobot.extensions.general.enums import RankingType, ReactionType
from holobot.extensions.general.exceptions import AlreadyMarriedError, NotMarriedError
from holobot.extensions.general.models import GeneralOptions, Marriage, RankingInfo
from holobot.extensions.general.repositories import IMarriageRepository
from holobot.sdk.configs import IOptions
from holobot.sdk.database.queries.enums.order import Order
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from holobot.sdk.utils import utcnow
from holobot.sdk.utils.string_utils import try_parse_int
from .imarriage_manager import IMarriageManager

_ONE_HOUR = timedelta(hours=1)

@injectable(IMarriageManager)
class MarriageManager(IMarriageManager):
    def __init__(
        self,
        marriage_repository: IMarriageRepository,
        options: IOptions[GeneralOptions]
    ) -> None:
        super().__init__()
        self.__marriage_repository = marriage_repository
        self.__options = options
        self.__match_bonuses = MarriageManager.__parse_match_bonuses(options.value.MatchMarriageBonusScore)

    async def get_spouse_id(
        self,
        server_id: str,
        user_id: str
    ) -> str | None:
        if not (marriage := await self.__marriage_repository.get_by_user(server_id, user_id)):
            return None

        return marriage.get_spouse(user_id)

    async def marry(
        self,
        server_id: str,
        user_id: str,
        target_user_id: str
    ) -> None:
        if marriage := await self.__marriage_repository.get_by_user(server_id, user_id):
            raise AlreadyMarriedError(user_id, marriage.get_spouse(user_id))

        if marriage := await self.__marriage_repository.get_by_user(server_id, target_user_id):
            raise AlreadyMarriedError(target_user_id, marriage.get_spouse(target_user_id))

        now = utcnow()
        await self.__marriage_repository.add(
            Marriage(
                server_id=server_id,
                user_id1=user_id,
                user_id2=target_user_id,
                married_at=now,
                activity_tier_reset_at=now
            )
        )

    async def divorce(
        self,
        server_id: str,
        user_id: str,
        spouse_id: str
    ) -> None:
        if await self.__marriage_repository.delete_by_user(server_id, user_id, spouse_id):
            return

        raise NotMarriedError(user_id)

    async def try_add_reaction(
        self,
        server_id: str,
        user_id1: str,
        user_id2: str,
        reaction_type: ReactionType
    ) -> bool:
        marriage = await self.__marriage_repository.get_by_users(server_id, user_id1, user_id2)
        if not marriage:
            return False

        now = utcnow()
        options = self.__options.value
        if now - marriage.activity_tier_reset_at >= _ONE_HOUR:
            # It's time to reset the activity tier.
            marriage.activity_tier = 0
            marriage.activity_tier_reset_at = now
        elif marriage.activity_tier >= len(options.MarriageActivityExpTiers) - 1:
            if (
                marriage.last_activity_at
                and (now - marriage.last_activity_at).total_seconds() < options.MarriageActivityLastTierCooldownSeconds
            ):
                # The marriage is in the last activity tier and the cooldown hasn't expired yet.
                return False

            self.__try_add_experience_points(marriage)
        else:
            self.__try_add_experience_points(marriage)
            marriage.activity_tier += 1

        marriage.last_activity_at = now
        match reaction_type:
            case ReactionType.HUG:
                marriage.hug_count += 1
            case ReactionType.KISS:
                marriage.kiss_count += 1
            case ReactionType.PAT:
                marriage.pat_count += 1
            case ReactionType.POKE:
                marriage.poke_count += 1
            case ReactionType.LICK:
                marriage.lick_count += 1
            case ReactionType.BITE:
                marriage.bite_count += 1
            case ReactionType.HANDHOLD:
                marriage.handhold_count += 1
            case ReactionType.CUDDLE:
                marriage.cuddle_count += 1
            case _:
                return False

        await self.__marriage_repository.update(marriage)

        return True

    async def get_react_score_bonus(
        self,
        server_id: str,
        user_id1: str,
        user_id2: str,
    ) -> int:
        marriage = await self.__marriage_repository.get_by_users(server_id, user_id1, user_id2)
        return marriage.match_bonus if marriage else 0

    def get_marriage(self, server_id: str, user_id: str) -> Awaitable[Marriage | None]:
        return self.__marriage_repository.get_by_user(server_id, user_id)

    def get_ranking_infos(
        self,
        server_id: str,
        ranking_type: RankingType,
        page_index: int,
        page_size: int
    ) -> Awaitable[PaginationResult[RankingInfo]]:
        return self.__marriage_repository.paginate_rankings(
            server_id,
            ranking_type,
            page_index,
            page_size
        )

    @staticmethod
    def __parse_match_bonuses(config: str) -> dict[int, int]:
        bonuses = {}
        if not config:
            return bonuses

        for item in config.split(";"):
            pair = item.split(":")
            if len(pair) != 2:
                continue

            level = try_parse_int(pair[0])
            bonus = try_parse_int(pair[1])
            if not level or not bonus:
                continue

            bonuses[level] = bonus

        return bonuses

    def __try_add_experience_points(
        self,
        marriage: Marriage
    ) -> None:
        options = self.__options.value
        while True:
            if marriage.level < 1 or marriage.level > len(options.MarriageActivityExpTable):
                # Already hit the level cap.
                return

            marriage.exp_points += options.MarriageActivityExpTiers[marriage.activity_tier]
            required_exp_points = options.MarriageActivityExpTable[marriage.level - 1]
            if marriage.exp_points < required_exp_points:
                return

            marriage.last_level_up_at = utcnow()
            marriage.level += 1
            marriage.exp_points = marriage.exp_points - required_exp_points
            if marriage.level in self.__match_bonuses:
                marriage.match_bonus += self.__match_bonuses[marriage.level]
