from asyncio import Lock
from dataclasses import dataclass, field
from datetime import timedelta

from holobot.discord.sdk.models import Embed, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ButtonState, ComponentBase, ComponentStyle, StackLayout, TextBox, TextBoxState
)
from holobot.discord.sdk.workflows.interactables.decorators import command, component, modal
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse
from holobot.discord.sdk.workflows.interactables.views import Modal, ModalState
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.models import GeneralOptions
from holobot.sdk.caching import IObjectCache, SlidingExpirationCacheEntryPolicy
from holobot.sdk.configs import IOptions
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc import injectable
from holobot.sdk.utils.string_utils import try_parse_int
from holobot.sdk.utils.uuid_utils import random_uuid

_MAX_OPTION_COUNT = 5
_OPTION_TEXT_BOX_ID_FORMAT = "option{index}"
_POLL_EXPIRATION_TIME = 5 * 60
_BAR_COUNT = 10

@dataclass
class _PollState:
    id: str
    options: list[str] = field(default_factory=list)
    votes: list[int] = field(default_factory=list)
    total_votes: int = 0
    voters: set[str] = field(default_factory=set)
    lock: Lock = field(default_factory=Lock)

@injectable(IWorkflow)
class PollWorkflow(WorkflowBase):
    def __init__(
        self,
        cache: IObjectCache,
        i18n_provider: II18nProvider,
        options: IOptions[GeneralOptions]
    ) -> None:
        super().__init__()
        self.__cache = cache.get_view(str, _PollState)
        self.__i18n = i18n_provider
        self.__options = options

    @command(
        name="poll",
        description="Creates a new poll.",
        cooldown=Cooldown(duration=120)
    )
    async def show_poll_creation_modal(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n.get("interactions.server_only_interaction_error")
            )

        return self._show_modal(
            Modal(
                identifier="poll_modal",
                owner_id=context.author_id,
                title=self.__i18n.get(
                    "extensions.general.poll_workflow.modal_title"
                ),
                components=[
                    TextBox(
                        id=_OPTION_TEXT_BOX_ID_FORMAT.format(index=index),
                        owner_id=context.author_id,
                        label=self.__i18n.get(
                            "extensions.general.poll_workflow.modal_option_label",
                            {
                                "index": index + 1
                            }
                        ),
                        is_required=index < 2,
                        min_length=1,
                        max_length=120
                    ) for index in range(_MAX_OPTION_COUNT)
                ]
            )
        )

    @modal(
        identifier="poll_modal"
    )
    async def create_poll(
        self,
        context: InteractionContext,
        state: ModalState
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n.get("interactions.server_only_interaction_error")
            )

        poll_state = _PollState(random_uuid(8))
        await self.__cache.add_or_replace(
            PollWorkflow.__get_cache_key(context.server_id, context.author_id, poll_state.id),
            poll_state,
            SlidingExpirationCacheEntryPolicy(timedelta(seconds=_POLL_EXPIRATION_TIME))
        )

        for index in range(_MAX_OPTION_COUNT):
            text_box_id = _OPTION_TEXT_BOX_ID_FORMAT.format(index=index)
            text_box_state = state.try_get_component_state(TextBoxState, text_box_id)
            if not text_box_state or not text_box_state.value:
                continue

            poll_state.options.append(text_box_state.value)
            poll_state.votes.append(0)

        embed, components = self.__create_response_items(
            context.author_id,
            poll_state
        )

        return self._reply(
            embed=embed,
            components=components
        )

    @component(identifier="pvote")
    async def add_vote(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not (poll_id := state.custom_data.get("p"))
            or not (index_string := state.custom_data.get("i"))
            or (index := try_parse_int(index_string)) is None
            or index < 0
        ):
            return self._reply(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                is_ephemeral=True
            )

        cache_key = PollWorkflow.__get_cache_key(context.server_id, state.owner_id, poll_id)
        if not (poll_state := await self.__cache.get(cache_key)):
            return self._reply(
                content=self.__i18n.get("extensions.general.poll_workflow.poll_expired_error"),
                is_ephemeral=True
            )

        async with poll_state.lock:
            if context.author_id in poll_state.voters:
                return self._reply(
                    content=self.__i18n.get("extensions.general.poll_workflow.already_voted_error"),
                    is_ephemeral=True
                )

            poll_state.voters.add(context.author_id)
            poll_state.votes[index] += 1
            poll_state.total_votes += 1

            embed, components = self.__create_response_items(
                state.owner_id,
                poll_state
            )

            return self._edit_message(
                embed=embed,
                components=components
            )

    @staticmethod
    def __get_cache_key(server_id: str, user_id: str, poll_id: str) -> str:
        return f"poll/{server_id}/{user_id}/{poll_id}"

    def __create_response_items(
        self,
        owner_id: str,
        state: _PollState
    ) -> tuple[Embed, StackLayout]:
        buttons = list[ComponentBase]()
        description_parts = []
        for index, option in enumerate(state.options):
            buttons.append(Button(
                id="pvote",
                owner_id=owner_id,
                text=self.__i18n.get(
                    "extensions.general.poll_workflow.embed_vote_button",
                    {
                        "index": index + 1
                    }
                ),
                style=ComponentStyle.SECONDARY,
                custom_data={
                    "p": state.id,
                    "i": str(index)
                }
            ))
            description_parts.append(self.__i18n.get(
                "extensions.general.poll_workflow.description_option",
                {
                    "index": index + 1,
                    "option": option
                }
            ))
            if state.total_votes > 0:
                filled_bar_count = int(state.votes[index] / state.total_votes * _BAR_COUNT)
                description_parts.append("".join((
                    self.__options.value.ProgressBarGreenEmoji * filled_bar_count,
                    self.__options.value.ProgressBarEmptyEmoji * (_BAR_COUNT - filled_bar_count),
                    " ",
                    str(state.votes[index]),
                    "\n"
                )))
            else:
                description_parts.append("".join((
                    self.__options.value.ProgressBarEmptyEmoji * _BAR_COUNT,
                    " ",
                    str(state.votes[index]),
                    "\n"
                )))

        return (
            Embed(
                title=self.__i18n.get(
                    "extensions.general.poll_workflow.embed_title"
                ),
                description="\n".join(description_parts)
            ),
            StackLayout(
                id="poll_layout",
                children=buttons
            )
        )
