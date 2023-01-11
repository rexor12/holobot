import time
from datetime import datetime, timezone
from random import Random
from typing import NamedTuple

from holobot.discord.sdk.exceptions import (
    ChannelNotFoundError, ServerNotFoundError, UserNotFoundError
)
from holobot.discord.sdk.models import Embed, EmbedField, InteractionContext
from holobot.discord.sdk.models.embed_footer import EmbedFooter
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.servers.models import MemberData
from holobot.discord.sdk.utils import get_user_id
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.models import GeneralOptions
from holobot.sdk.configs import IOptions
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.datetime_utils import utcnow

class _TypeConstraints(NamedTuple):
    bar_min: int
    bar_max: int
    bar_split_at: int

class _Statistics(NamedTuple):
    chemistry: int
    communication: int
    trust: int
    commitment: int
    security: int
    love_type: int
    score: int
    is_max_score: bool

_SELF_STATISTICS = _Statistics(100, 100, 100, 100, 100, 5, 10, False)
_TYPE_CONSTRAINTS = {
    0: _TypeConstraints(0, 25, 15),
    1: _TypeConstraints(20, 45, 35),
    2: _TypeConstraints(35, 60, 45),
    3: _TypeConstraints(50, 75, 55),
    4: _TypeConstraints(65, 80, 70),
    5: _TypeConstraints(80, 100, 90)
}

@injectable(IWorkflow)
class MatchUsersWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        member_data_provider: IMemberDataProvider,
        options: IOptions[GeneralOptions]
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__member_data_provider = member_data_provider
        self.__options = options

    @command(
        description="Shows how good a match two users are.",
        name="match",
        options=(
            Option("user", "The name or mention of the user.", OptionType.STRING, True),
            Option("user2", "The name or mention of the second user.", OptionType.STRING, False)
        ),
        cooldown=Cooldown(duration=10)
    )
    async def match_users(
        self,
        context: InteractionContext,
        user: str,
        user2: str | None = None
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        if not user:
            return self._reply(
                content=self.__i18n_provider.get(
                    "missing_required_argument_error", { "argname": "user" }
                )
            )

        try:
            member_data1 = await (
                self.__get_member_data(context.server_id, user.strip())
                if user2
                else self.__member_data_provider.get_basic_data_by_id(
                    context.server_id,
                    context.author_id
                )
            )
            member_data2 = await self.__get_member_data(
                context.server_id,
                user2.strip() if user2 else user.strip()
            )
            if not member_data1 or not member_data2:
                return self._reply(
                    content=self.__i18n_provider.get("user_not_found_error")
                )

            statistics, next_refresh_at = self.__get_statistics(member_data1, member_data2)
            if member_data1.user_id == member_data2.user_id:
                description = self.__i18n_provider.get(
                    "extensions.general.match_users_workflow.self_description",
                    { "user_id": member_data1.user_id }
                )
            else:
                description = "".join((
                    self.__i18n_provider.get(
                        "extensions.general.match_users_workflow.description_base",
                        {
                            "user_id1": member_data1.user_id,
                            "user_id2": member_data2.user_id
                        }
                    ),
                    self.__i18n_provider.get_list_item(
                        "extensions.general.match_users_workflow.descriptions",
                        statistics.love_type
                    )
                ))
            return self._reply(
                embed=Embed(
                    title=self.__i18n_provider.get(
                        "extensions.general.match_users_workflow.title"
                    ),
                    description=description,
                    fields=[
                        EmbedField(
                            self.__i18n_provider.get("extensions.general.match_users_workflow.chemistry"),
                            self.__get_quality_value(statistics.chemistry),
                            False
                        ),
                        EmbedField(
                            self.__i18n_provider.get("extensions.general.match_users_workflow.communication"),
                            self.__get_quality_value(statistics.communication),
                            False
                        ),
                        EmbedField(
                            self.__i18n_provider.get("extensions.general.match_users_workflow.trust"),
                            self.__get_quality_value(statistics.trust),
                            False
                        ),
                        EmbedField(
                            self.__i18n_provider.get("extensions.general.match_users_workflow.commitment"),
                            self.__get_quality_value(statistics.commitment),
                            False
                        ),
                        EmbedField(
                            self.__i18n_provider.get("extensions.general.match_users_workflow.security"),
                            self.__get_quality_value(statistics.security),
                            False
                        ),
                        EmbedField(
                            self.__i18n_provider.get("extensions.general.match_users_workflow.type"),
                            self.__i18n_provider.get(
                                "extensions.general.match_users_workflow.self_love_type"
                            ) if member_data1.user_id == member_data2.user_id
                            else self.__i18n_provider.get_list_item(
                                "extensions.general.match_users_workflow.love_types",
                                statistics.love_type
                            ),
                            False
                        ),
                        EmbedField(
                            self.__i18n_provider.get("extensions.general.match_users_workflow.overall_score"),
                            self.__i18n_provider.get(
                                "extensions.general.match_users_workflow.overall_score_value",
                                {
                                    "score": statistics.score,
                                    "emoji": self.__i18n_provider.get_list_item(
                                        "extensions.general.match_users_workflow.overall_score_emojis",
                                        (statistics.love_type + 1) if statistics.is_max_score else statistics.love_type
                                    )
                                }
                            ),
                            False
                        )
                    ],
                    footer=EmbedFooter(
                        self.__i18n_provider.get(
                            "extensions.general.match_users_workflow.footer",
                            { "refresh_in": int((next_refresh_at - utcnow()).total_seconds() / 60) }
                        )
                    )
                )
            )
        except UserNotFoundError:
            return self._reply(
                content=self.__i18n_provider.get("user_not_found_error")
            )
        except ServerNotFoundError:
            return self._reply(
                content=self.__i18n_provider.get("server_not_found_error")
            )
        except ChannelNotFoundError:
            return self._reply(
                content=self.__i18n_provider.get("channel_not_found_error")
            )

    @staticmethod
    def __generate_bar_values(rng: Random, score: int) -> list[int]:
        constraints = _TYPE_CONSTRAINTS[score]

        # Not DRY to avoid unnecessary memory allocation (loops, concatenations).
        values = [
            rng.randint(constraints.bar_min, constraints.bar_split_at),
            rng.randint(constraints.bar_min, constraints.bar_split_at),
            rng.randint(constraints.bar_split_at, constraints.bar_max),
            rng.randint(constraints.bar_split_at, constraints.bar_max),
            rng.randint(constraints.bar_split_at, constraints.bar_max)
        ]
        rng.shuffle(values)

        return values

    def __get_statistics(
        self,
        member_data1: MemberData,
        member_data2: MemberData
    ) -> tuple[_Statistics, datetime]:
        current_time = time.time()
        refresh_interval = self.__options.value.RefreshRelationshipsAfterMinutes * 60
        refresh_cycle = int(current_time / refresh_interval)
        next_refresh_at = datetime.fromtimestamp(
            (refresh_cycle + 1) * refresh_interval,
            tz=timezone.utc
        )
        if member_data1.user_id == member_data2.user_id:
            return (_SELF_STATISTICS, next_refresh_at)

        rng = Random(
            hash(member_data1.user_id)
            + hash(member_data2.user_id)
            + refresh_cycle
        )

        score = rng.randint(1, 10)
        love_type = int(score / 2)
        is_max_score = rng.random() < 0.001 if score == 10 else False
        bar_values = (
            (100, 100, 100, 100, 100)
            if is_max_score
            else MatchUsersWorkflow.__generate_bar_values(rng, love_type)
        )

        statistics = (
            _Statistics(
                bar_values[0],
                bar_values[1],
                bar_values[2],
                bar_values[3],
                bar_values[4],
                love_type,
                score,
                is_max_score
            ),
            next_refresh_at
        )

        return statistics

    def __get_quality_value(self, percentage: int) -> str:
        bar_count = int(percentage * 9 / 100) + 1
        if percentage <= 30:
            bar_emoji = self.__options.value.ProgressBarRedEmoji
        elif percentage <= 60:
            bar_emoji = self.__options.value.ProgressBarOrangeEmoji
        else:
            bar_emoji = self.__options.value.ProgressBarGreenEmoji

        return "".join([bar_emoji * bar_count, f" {percentage}%"])

    async def __get_member_data(self, server_id: str, name_or_mention: str) -> MemberData:
        user_id = get_user_id(name_or_mention)
        member_data = await (
            self.__member_data_provider.get_basic_data_by_id(server_id, user_id)
            if user_id
            else self.__member_data_provider.get_basic_data_by_name(server_id, name_or_mention)
        )
        return member_data