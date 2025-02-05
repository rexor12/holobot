from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import (
    Choice, InteractionResponse, Option, StringOption
)
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.sdk.currencies.data_providers import ICurrencyDataProvider
from holobot.extensions.general.sdk.currencies.models import ICurrency
from holobot.extensions.general.sdk.wallets.managers import IWalletManager
from holobot.extensions.mudada.configs import MudadaOptions
from holobot.extensions.mudada.constants import VALENTINES_2025_EVENT_TOGGLE_FEATURE_NAME
from holobot.extensions.mudada.factories import ChartData, IRatingChartFactory
from holobot.extensions.mudada.models import Valentine2025Rating, Valentine2025RatingId
from holobot.extensions.mudada.models.user_reward import UserReward
from holobot.extensions.mudada.repositories.valentine2025 import (
    IUserRewardRepository, IValentine2025RatingRepository
)
from holobot.extensions.mudada.workflows.decorators import requires_event
from holobot.sdk.configs import IOptions
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from .helpers import get_user_name_with_hex_color

_SCORES: tuple[Choice, ...] = tuple([
    Choice(
        name=str(score),
        value=score
    ) for score in range(1, 11)
])

@injectable(IWorkflow)
class RateUserWorkflow(WorkflowBase):
    def __init__(
        self,
        currency_data_provider: ICurrencyDataProvider,
        i18n_provider: II18nProvider,
        member_data_provider: IMemberDataProvider,
        options: IOptions[MudadaOptions],
        rating_chart_factory: IRatingChartFactory,
        rating_repository: IValentine2025RatingRepository,
        unit_of_work_provider: IUnitOfWorkProvider,
        user_reward_repository: IUserRewardRepository,
        wallet_manager: IWalletManager
    ) -> None:
        super().__init__()
        self.__currency_data_provider = currency_data_provider
        self.__i18n = i18n_provider
        self.__member_data_provider = member_data_provider
        self.__options = options
        self.__rating_chart_factory = rating_chart_factory
        self.__rating_repository = rating_repository
        self.__unit_of_work_provider = unit_of_work_provider
        self.__user_reward_repository = user_reward_repository
        self.__wallet_manager = wallet_manager

    @requires_event(VALENTINES_2025_EVENT_TOGGLE_FEATURE_NAME)
    @command(
        group_name="mudada",
        subgroup_name="valentine",
        name="rate",
        description="Rate a person's qualities.",
        options=(
            Option("user", "The user you'd like to rate.", OptionType.USER),
            Option("humor", "How amusing or comic do you think the person is?", OptionType.INTEGER, choices=_SCORES),
            Option("positivity", "How optimistic in attitude do you think the person is?", OptionType.INTEGER, choices=_SCORES),
            Option("trust", "How much can you trust this person?", OptionType.INTEGER, choices=_SCORES),
            Option("lewdness", "How lewd do you think the person is?", OptionType.INTEGER, choices=_SCORES),
            Option("creativity", "How creative do you think the person is?", OptionType.INTEGER, choices=_SCORES),
            Option("chemistry", "How well do you get along with the person?", OptionType.INTEGER, choices=_SCORES),
            StringOption("message", "An optional message for the person.", is_mandatory=False, max_length=250),
        )
    )
    async def rate_user(
        self,
        context: InteractionContext,
        user: int,
        humor: int,
        positivity: int,
        trust: int,
        lewdness: int,
        creativity: int,
        chemistry: int,
        message: str | None = None
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n.get("interactions.server_only_interaction_error")
            )

        if user == context.author_id:
            return self._reply(
                content=self.__i18n.get("extensions.mudada.rate_user_workflow.cannot_rate_self_error"),
                is_ephemeral=True
            )

        rating_id = Valentine2025RatingId(source_user_id=context.author_id, target_user_id=user)
        should_reward = False
        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            rating = await self.__rating_repository.get(rating_id)
            if rating:
                rating.score1 = humor
                rating.score2 = positivity
                rating.score3 = trust
                rating.score4 = lewdness
                rating.score5 = creativity
                rating.score6 = chemistry
                rating.message = message
                rating.is_deleted = False
                await self.__rating_repository.update(rating)
            else:
                should_reward = True
                await self.__rating_repository.add(Valentine2025Rating(
                    identifier=rating_id,
                    score1=humor,
                    score2=positivity,
                    score3=trust,
                    score4=lewdness,
                    score5=creativity,
                    score6=chemistry,
                    message=message
                ))

            granted_currency, granted_amount, granted_amount_left = await self.__try_grant_reward(
                context.server_id,
                context.author_id,
                should_reward
            )

            unit_of_work.complete()

        user_name, user_color = await get_user_name_with_hex_color(
            self.__member_data_provider,
            context.server_id,
            user
        )
        chart_url = self.__rating_chart_factory.get_chart_url(
            user_name[:15],
            user_color,
            ChartData(
                score1=humor,
                score2=positivity,
                score3=trust,
                score4=lewdness,
                score5=creativity,
                score6=chemistry
            )
        )

        if granted_currency and granted_amount > 0:
            return self._reply(
                content=self.__i18n.get(
                    "extensions.mudada.rate_user_workflow.rating_successful_with_reward",
                    {
                        "chart_url": chart_url,
                        "user_id": user,
                        "currency_emoji_id": granted_currency.emoji_id,
                        "currency_emoji_name": granted_currency.emoji_name,
                        "granted_amount": granted_amount,
                        "amount_left": granted_amount_left
                    }
                ),
                suppress_user_mentions=True,
                is_ephemeral=True
            )

        return self._reply(
            content=self.__i18n.get(
                "extensions.mudada.rate_user_workflow.rating_successful",
                {
                    "chart_url": chart_url,
                    "user_id": user
                }
            ),
            suppress_user_mentions=True,
            is_ephemeral=True
        )

    @requires_event(VALENTINES_2025_EVENT_TOGGLE_FEATURE_NAME)
    @command(
        group_name="mudada",
        subgroup_name="valentine",
        name="unrate",
        description="Removes your rating of a person's qualities.",
        options=(
            Option("user", "The user to clear the rating for.", OptionType.USER),
        )
    )
    async def unrate_user(
        self,
        context: InteractionContext,
        user: int
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n.get("interactions.server_only_interaction_error")
            )

        rating_id = Valentine2025RatingId(source_user_id=context.author_id, target_user_id=user)
        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            rating = await self.__rating_repository.get(rating_id)
            if rating:
                rating.is_deleted = True
                await self.__rating_repository.update(rating)
                unit_of_work.complete()

        return self._reply(
            content=self.__i18n.get(
                "extensions.mudada.rate_user_workflow.unrating_successful"
                if rating
                else "extensions.mudada.rate_user_workflow.not_rated_yet_error",
                {
                    "user_id": user
                }
            ),
            suppress_user_mentions=True,
            is_ephemeral=True
        )

    async def __try_grant_reward(
        self,
        server_id: int,
        user_id: int,
        should_reward: bool
    ) -> tuple[ICurrency | None, int, int]: # tuple[currency?, given amount, left amount]
        if not should_reward:
            return (None, 0, 0)

        options = self.__options.value
        amount_to_give = min(options.Valentine2025RewardPerRating, options.Valentine2025MaxReward)
        if amount_to_give <= 0:
            return (None, 0, 0)

        currency = await self.__currency_data_provider.get_currency_by_code(
            server_id,
            self.__options.value.Valentine2025RewardCurrencyCode
        )
        if not currency:
            return (None, 0, 0)

        given_amount, max_amount = await self.__update_user_rewards(user_id, amount_to_give)
        if given_amount <= 0:
            return (currency, given_amount, max_amount)

        await self.__wallet_manager.give_money(
            user_id,
            currency.identifier,
            server_id,
            given_amount
        )

        return (currency, given_amount, max_amount)

    async def __update_user_rewards(
        self,
        user_id: int,
        reward_amount: int
    ) -> tuple[int, int]: # tuple[given amount, left amount]
        # Must be guaranteed by the caller.
        assert reward_amount > 0

        options = self.__options.value
        if not (user_reward := await self.__user_reward_repository.get(user_id)):
            user_reward = UserReward(
                identifier=user_id,
                reward_amount=reward_amount
            )

            await self.__user_reward_repository.add(user_reward)

            return (
                reward_amount,
                options.Valentine2025MaxReward - reward_amount
            )

        current_amount = user_reward.reward_amount
        user_reward.reward_amount = min(
            user_reward.reward_amount + reward_amount,
            options.Valentine2025MaxReward
        )

        await self.__user_reward_repository.update(user_reward)

        return (
            user_reward.reward_amount - current_amount,
            options.Valentine2025MaxReward - user_reward.reward_amount
        )
