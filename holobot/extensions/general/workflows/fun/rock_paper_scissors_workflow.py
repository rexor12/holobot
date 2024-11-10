import datetime
from asyncio import Lock
from dataclasses import dataclass, field
from enum import IntEnum

from holobot.discord.sdk.data_providers import IUserDataProvider
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ButtonState, ComponentStyle, StackLayout
)
from holobot.discord.sdk.workflows.interactables.components.component_utils import get_custom_int
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.options import RockPaperScissorsOptions
from holobot.sdk.caching import IObjectCache, SlidingExpirationCacheEntryPolicy
from holobot.sdk.configs import IOptions
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.datetime_utils import utcnow

_MAX_ROUNDS: int = 3
_EXPIRY_TIME: datetime.timedelta = datetime.timedelta(minutes=5)
_DM_SERVER_ID: int = -1
_INITIATOR_KEY: str = "i"
_ACTION_TYPE_KEY: str = "a"

class _Action(IntEnum):
    ROCK = 0
    PAPER = 1
    SCISSORS = 2

class _GameStatus(IntEnum):
    CREATED = 0
    CHALLENGED = 1
    INITIATOR_ROUND = 2
    TARGET_ROUND = 3
    GAME_OVER = 4

class _ActionOutcome(IntEnum):
    DRAW = 0
    INITIATOR_WIN = 1
    TARGET_WIN = 2

@dataclass(kw_only=True)
class _GameState:
    started_at: datetime.datetime
    initiator_id: int
    initiator_name: str
    target_id: int
    target_name: str
    is_bot_target: bool = False
    initiator_action: _Action | None = None
    initiator_wins: int = 0
    target_wins: int = 0
    round_index: int = 0
    status: _GameStatus = _GameStatus.CREATED
    lock: Lock = field(default_factory=Lock)

@injectable(IWorkflow)
class RockPaperScissorsWorkflow(WorkflowBase):
    def __init__(
        self,
        cache: IObjectCache,
        i18n_provider: II18nProvider,
        options: IOptions[RockPaperScissorsOptions],
        user_data_provider: IUserDataProvider
    ) -> None:
        super().__init__()
        self.__cache = cache.get_view(str, _GameState)
        self.__i18n = i18n_provider
        self.__options = options
        self.__user_data_provider = user_data_provider
        self.__emoji_by_actions = (
            options.value.RockEmojiId,
            options.value.PaperEmojiId,
            options.value.ScissorsEmojiId
        )

    @command(
        group_name="game",
        name="pst",
        description="Start a Plane-Ship-Tank game with someone!",
        options=(
            Option("user", "The user you'd like to play against.", OptionType.USER, True),
        )
    )
    async def start_rock_paper_scissors(
        self,
        context: InteractionContext,
        user: int | None = None
    ) -> InteractionResponse:
        target_id = (
            user
            if user is not None
            else self.__user_data_provider.get_self().user_id
        )
        if target_id == context.author_id:
            return self._reply(
                content=self.__i18n.get(
                    "extensions.general.rock_paper_scissors_workflow.cannot_challenge_self_error"
                ),
                is_ephemeral=True
            )

        # TODO Handle bot target for coop game.
        if target_id == self.__user_data_provider.get_self().user_id:
            return self._reply(
                content=self.__i18n.get(
                    "extensions.general.rock_paper_scissors_workflow.cannot_challenge_bot_error"
                ),
                is_ephemeral=True
            )

        server_id = RockPaperScissorsWorkflow.__get_server_id(context)
        cache_key = RockPaperScissorsWorkflow.__get_cache_key(server_id, context.author_id)
        game_state = await self.__cache.get_or_add(
            cache_key,
            lambda _: self.__create_new_game(context, target_id, user is None),
            SlidingExpirationCacheEntryPolicy(expires_after=_EXPIRY_TIME)
        )

        if not isinstance(game_state, _GameState):
            return self._reply(
                content=self.__i18n.get(
                    "extensions.general.rock_paper_scissors_workflow.already_started_a_match_error"
                ),
                is_ephemeral=True
            )

        async with game_state.lock:
            if game_state.status != _GameStatus.CREATED:
                return self._reply(
                    content=self.__i18n.get(
                        "extensions.general.rock_paper_scissors_workflow.already_started_a_match_error"
                    ),
                    is_ephemeral=True
                )
            game_state.status = _GameStatus.CHALLENGED

        return self._reply(
            content=self.__i18n.get(
                "extensions.general.rock_paper_scissors_workflow.challenge_message",
                {
                    "initiator_id": game_state.initiator_id,
                    "target_id": game_state.target_id
                }
            ),
            components=StackLayout(
                id="dummy",
                children=[
                    Button(
                        id="grps_ca",
                        owner_id=target_id,
                        text=self.__i18n.get("common.buttons.accept"),
                        custom_data={
                            _INITIATOR_KEY: str(game_state.initiator_id)
                        }
                    ),
                    Button(
                        id="grps_cd",
                        owner_id=target_id,
                        text=self.__i18n.get("common.buttons.decline"),
                        style=ComponentStyle.SECONDARY,
                        custom_data={
                            _INITIATOR_KEY: str(game_state.initiator_id)
                        }
                    ),
                    self.__create_help_button(),
                    self.__create_forfeit_button(game_state.initiator_id)
                ]
            )
        )

    @component(
        identifier="grps_ca",
        is_bound=True
    )
    async def accept_challenge(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (initiator_id := get_custom_int(state.custom_data, _INITIATOR_KEY)) is None:
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                is_ephemeral=True
            )

        server_id = RockPaperScissorsWorkflow.__get_server_id(context)
        cache_key = RockPaperScissorsWorkflow.__get_cache_key(server_id, initiator_id)
        game_state = await self.__cache.get(cache_key)
        if not isinstance(game_state, _GameState):
            return self._reply(
                content=self.__i18n.get(
                    "extensions.general.rock_paper_scissors_workflow.expired_game_error"
                ),
                is_ephemeral=True
            )

        async with game_state.lock:
            if game_state.status != _GameStatus.CHALLENGED:
                return self._reply(
                    content=self.__i18n.get(
                        "extensions.general.rock_paper_scissors_workflow.not_your_round_error"
                    ),
                    is_ephemeral=True
                )

            game_state.status = _GameStatus.INITIATOR_ROUND

        return self._edit_message(
            content=self.__i18n.get(
                "extensions.general.rock_paper_scissors_workflow.choose_first_action",
                {
                    "initiator_id": initiator_id
                }
            ),
            components=StackLayout(
                id="dummy",
                children=[
                    self.__create_action_button(initiator_id, initiator_id, _Action.ROCK),
                    self.__create_action_button(initiator_id, initiator_id, _Action.PAPER),
                    self.__create_action_button(initiator_id, initiator_id, _Action.SCISSORS),
                    self.__create_help_button(),
                    self.__create_forfeit_button(initiator_id)
                ]
            )
        )

    @component(
        identifier="grps_cd",
        is_bound=True
    )
    async def decline_challenge(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (initiator_id := get_custom_int(state.custom_data, _INITIATOR_KEY)) is None:
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                is_ephemeral=True
            )

        server_id = RockPaperScissorsWorkflow.__get_server_id(context)
        cache_key = RockPaperScissorsWorkflow.__get_cache_key(server_id, initiator_id)
        await self.__cache.remove(cache_key)

        return self._edit_message(
            content=self.__i18n.get(
                "extensions.general.rock_paper_scissors_workflow.challenge_declined",
                {
                    "initiator_id": initiator_id
                }
            ),
            components=None
        )

    @component(
        identifier="grps_sa",
        is_bound=True
    )
    async def action_selected(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            (initiator_id := get_custom_int(state.custom_data, _INITIATOR_KEY)) is None
            or (action_type := get_custom_int(state.custom_data, _ACTION_TYPE_KEY)) is None
        ):
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                is_ephemeral=True
            )

        action_type = _Action(action_type)
        server_id = RockPaperScissorsWorkflow.__get_server_id(context)
        cache_key = RockPaperScissorsWorkflow.__get_cache_key(server_id, initiator_id)
        game_state = await self.__cache.get(cache_key)
        if not isinstance(game_state, _GameState):
            return self._reply(
                content=self.__i18n.get(
                    "extensions.general.rock_paper_scissors_workflow.expired_game_error"
                ),
                is_ephemeral=True
            )

        is_initiator = context.author_id == initiator_id
        outcome: _ActionOutcome | None = None
        async with game_state.lock:
            if (
                (game_state.status != _GameStatus.INITIATOR_ROUND and is_initiator)
                or (game_state.status != _GameStatus.TARGET_ROUND and not is_initiator)
            ):
                return self._reply(
                    content=self.__i18n.get(
                        "extensions.general.rock_paper_scissors_workflow.not_your_round_error"
                    ),
                    is_ephemeral=True
                )

            if is_initiator:
                game_state.status = _GameStatus.TARGET_ROUND
                game_state.initiator_action = action_type
                outcome = None
            else:
                game_state.status = _GameStatus.INITIATOR_ROUND
                outcome = RockPaperScissorsWorkflow.__update_results(game_state, action_type)
                rounds_left = _MAX_ROUNDS - game_state.round_index
                is_hopeless = rounds_left < abs(game_state.target_wins - game_state.initiator_wins)
                if rounds_left <= 0 or is_hopeless:
                    game_state.status = _GameStatus.GAME_OVER
                    if game_state.initiator_wins == game_state.target_wins:
                        i18n_key = "extensions.general.rock_paper_scissors_workflow.game_over_draw"
                        winner_id = ""
                    elif game_state.initiator_wins > game_state.target_wins:
                        i18n_key = "extensions.general.rock_paper_scissors_workflow.game_over"
                        winner_id = game_state.initiator_id
                    else:
                        i18n_key = "extensions.general.rock_paper_scissors_workflow.game_over"
                        winner_id = game_state.target_id

                    await self.__cache.remove(cache_key)

                    return self._edit_message(
                        content=self.__i18n.get(
                            i18n_key,
                            {
                                "winner_id": winner_id,
                                "initiator_id": game_state.initiator_id,
                                "target_id": game_state.target_id,
                                "last_result": self.__get_round_result_i18n(
                                    game_state,
                                    action_type
                                )
                            }
                        ),
                        components=None
                    )

        if is_initiator:
            next_player_id = game_state.target_id
            round_result_i18n = None
            round_i18n_key = "extensions.general.rock_paper_scissors_workflow.choose_action_initiator"
            winner_name = None
        else:
            assert outcome is not None
            next_player_id = game_state.initiator_id
            round_result_i18n = self.__get_round_result_i18n(game_state, action_type)
            if outcome == _ActionOutcome.DRAW:
                round_i18n_key = "extensions.general.rock_paper_scissors_workflow.choose_action_draw"
                winner_name = None
            elif outcome == _ActionOutcome.INITIATOR_WIN:
                round_i18n_key = "extensions.general.rock_paper_scissors_workflow.choose_action_target"
                winner_name = game_state.initiator_name
            else:
                round_i18n_key = "extensions.general.rock_paper_scissors_workflow.choose_action_target"
                winner_name = game_state.target_name

        return self._edit_message(
            content=self.__i18n.get(
                round_i18n_key,
                {
                    "user_id": next_player_id,
                    "last_result": round_result_i18n,
                    "winner_name": winner_name
                }
            ),
            components=StackLayout(
                id="dummy",
                children=[
                    self.__create_action_button(initiator_id, next_player_id, _Action.ROCK),
                    self.__create_action_button(initiator_id, next_player_id, _Action.PAPER),
                    self.__create_action_button(initiator_id, next_player_id, _Action.SCISSORS),
                    self.__create_help_button(),
                    self.__create_forfeit_button(initiator_id)
                ]
            )
        )

    @component(identifier="grps_help")
    async def show_help(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        return self._reply(
            content=self.__i18n.get("extensions.general.rock_paper_scissors_workflow.help"),
            is_ephemeral=True
        )

    @component(identifier="grps_forfeit")
    async def forfeit_match(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (initiator_id := get_custom_int(state.custom_data, _INITIATOR_KEY)) is None:
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                is_ephemeral=True
            )

        server_id = RockPaperScissorsWorkflow.__get_server_id(context)
        cache_key = RockPaperScissorsWorkflow.__get_cache_key(server_id, initiator_id)
        game_state = await self.__cache.get(cache_key)
        if not isinstance(game_state, _GameState):
            return self._reply(
                content=self.__i18n.get(
                    "extensions.general.rock_paper_scissors_workflow.expired_game_error"
                ),
                is_ephemeral=True
            )

        async with game_state.lock:
            if game_state.status == _GameStatus.GAME_OVER:
                return self._reply(
                    content=self.__i18n.get(
                        "extensions.general.rock_paper_scissors_workflow.game_already_over_error"
                    ),
                    is_ephemeral=True
                )

            if context.author_id == game_state.initiator_id:
                is_initiator = True
            elif context.author_id == game_state.target_id:
                is_initiator = False
            else:
                return self._reply(
                    content=self.__i18n.get("interactions.unbound_interaction_user_error"),
                    is_ephemeral=True
                )

            await self.__cache.remove(cache_key)

        return self._edit_message(
            content=self.__i18n.get(
                "extensions.general.rock_paper_scissors_workflow.game_forfeited",
                {
                    "user_name": (
                        game_state.initiator_name
                        if is_initiator
                        else game_state.target_name
                    )
                }
            ),
            components=None
        )

    @staticmethod
    def __get_cache_key(server_id: int, user_id: int) -> str:
        return f"game-rps/{server_id}/{user_id}"

    @staticmethod
    def __get_server_id(context: InteractionContext) -> int:
        if isinstance(context, ServerChatInteractionContext):
            return context.server_id
        return _DM_SERVER_ID

    @staticmethod
    def __update_results(
        game_state: _GameState,
        target_action: _Action
    ) -> _ActionOutcome:
        game_state.round_index += 1
        initiator_action = game_state.initiator_action
        if initiator_action == target_action:
            return _ActionOutcome.DRAW

        if (
            target_action == _Action.ROCK and initiator_action == _Action.PAPER
            or target_action == _Action.PAPER and initiator_action == _Action.SCISSORS
            or target_action == _Action.SCISSORS and initiator_action == _Action.ROCK
        ):
            game_state.initiator_wins += 1
            return _ActionOutcome.INITIATOR_WIN
        else:
            game_state.target_wins += 1
            return _ActionOutcome.TARGET_WIN

    @staticmethod
    def __get_action_details(
        options: RockPaperScissorsOptions,
        action: _Action
    ) -> tuple[int, str, str]:
        match action:
            case _Action.ROCK:
                return (
                    options.RockEmojiId,
                    options.RockEmojiName,
                    "extensions.general.rock_paper_scissors_workflow.items.rock"
                )
            case _Action.PAPER:
                return (
                    options.PaperEmojiId,
                    options.PaperEmojiName,
                    "extensions.general.rock_paper_scissors_workflow.items.paper"
                )
            case _Action.SCISSORS:
                return (
                    options.ScissorsEmojiId,
                    options.ScissorsEmojiName,
                    "extensions.general.rock_paper_scissors_workflow.items.scissors"
                )
            case _:
                raise ArgumentError("action", action)

    async def __create_new_game(
        self,
        context: InteractionContext,
        target_id: int,
        is_bot_target: bool
    ) -> _GameState:
        target_user = await self.__user_data_provider.get_user_data_by_id(target_id)

        return _GameState(
            started_at=utcnow(),
            initiator_id=context.author_id,
            initiator_name=context.author_name,
            target_id=target_id,
            target_name=target_user.name,
            is_bot_target=is_bot_target
        )

    def __create_action_button(
        self,
        initiator_id: int,
        owner_id: int,
        action_type: _Action
    ) -> Button:
        return Button(
            id="grps_sa",
            owner_id=owner_id,
            emoji=self.__emoji_by_actions[action_type.value],
            style=ComponentStyle.SECONDARY,
            custom_data={
                _INITIATOR_KEY: str(initiator_id),
                _ACTION_TYPE_KEY: str(action_type.value)
            }
        )

    def __get_round_result_i18n(
        self,
        game_state: _GameState,
        target_action: _Action
    ) -> str:
        assert game_state.initiator_action is not None

        emoji_id1, emoji_name1, item1 = RockPaperScissorsWorkflow.__get_action_details(
            self.__options.value,
            game_state.initiator_action
        )
        emoji_id2, emoji_name2, item2 = RockPaperScissorsWorkflow.__get_action_details(
            self.__options.value,
            target_action
        )

        return  self.__i18n.get(
            "extensions.general.rock_paper_scissors_workflow.round_result",
            {
                "user_id1": game_state.initiator_id,
                "user_name1": game_state.initiator_name,
                "item1": self.__i18n.get_random_list_item(item1),
                "emoji_name1": emoji_name1,
                "emoji_id1": emoji_id1,
                "user_id2": game_state.target_id,
                "user_name2": game_state.target_name,
                "item2": self.__i18n.get_random_list_item(item2),
                "emoji_name2": emoji_name2,
                "emoji_id2": emoji_id2
            }
        )

    def __create_help_button(self) -> Button:
        return Button(
            id="grps_help",
            owner_id=0,
            text=self.__i18n.get("common.buttons.help"),
            style=ComponentStyle.SECONDARY
        )

    def __create_forfeit_button(self, initiator_id: int) -> Button:
        return Button(
            id="grps_forfeit",
            owner_id=0,
            text=self.__i18n.get("extensions.general.rock_paper_scissors_workflow.forfeit"),
            style=ComponentStyle.DANGER,
            custom_data={
                _INITIATOR_KEY: str(initiator_id)
            }
        )
