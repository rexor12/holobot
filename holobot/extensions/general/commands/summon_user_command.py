from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import DoNothingAction, ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.enums import OptionType
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.exceptions import ChannelNotFoundError, ForbiddenError, ServerNotFoundError, UserNotFoundError
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.utils import get_user_id
from holobot.discord.sdk.utils.mention_utils import get_channel_id_or_default
from holobot.sdk.ioc.decorators import injectable
from typing import Optional

MESSAGE_LENGTH_MAX = 192

@injectable(CommandInterface)
class SummonUserCommand(CommandBase):
    def __init__(self, member_data_provider: IMemberDataProvider, messaging: IMessaging) -> None:
        super().__init__("summon")
        self.__member_data_provider: IMemberDataProvider = member_data_provider
        self.__messaging: IMessaging = messaging
        self.description = "Requests a user's presence via a direct message."
        self.options = [
            Option("name", "The name or mention of the user.", OptionType.STRING, True),
            Option("message", "An optional message the bot forwards to the user.", OptionType.STRING, False),
            Option("channel", "An optional mention of the channel where the user should be summoned.", OptionType.STRING, False)
        ]

    async def execute(self, context: ServerChatInteractionContext, name: str, message: Optional[str] = None, channel: Optional[str] = None) -> CommandResponse:
        if not name:
            return CommandResponse(
                action=ReplyAction(content="You must specify a user by their name or mention.")
            )
        
        try:
            name = name.strip()
            user_id = get_user_id(name)
            if not user_id:
                member = self.__member_data_provider.get_basic_data_by_name(context.server_id, name)
                if not member:
                    return CommandResponse(action=ReplyAction(content="I can't find the user you specified. Did you make a typo?"))
                user_id = member.user_id
            
            channel_id = get_channel_id_or_default(channel, context.channel_id) if channel else context.channel_id
            if message:
                message = message.strip()[:MESSAGE_LENGTH_MAX]
                target_message = "<@{}> is summoning you to <#{}> with the message '{}'."
            else: target_message = "<@{}> is summoning you to <#{}>."

            await self.__messaging.send_private_message(user_id, target_message.format(context.author_id, channel_id, message))
        except ForbiddenError:
            return CommandResponse(action=ReplyAction(content="I have no permission to send a DM to the specified user."))
        except UserNotFoundError:
            return CommandResponse(action=ReplyAction(content="I can't find the user you specified. Did you make a typo?"))
        except (ServerNotFoundError, ChannelNotFoundError):
            return CommandResponse(action=DoNothingAction())

        return CommandResponse(
            action=ReplyAction(content="I've notified the user of their presence being required.")
        )
