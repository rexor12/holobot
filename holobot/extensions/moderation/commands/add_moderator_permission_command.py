from .moderation_command_base import ModerationCommandBase
from ..enums import ModeratorPermission
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_choice, create_option
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import reply
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class AddModeratorPermissionCommand(ModerationCommandBase):
    def __init__(self) -> None:
        super().__init__("add")
        self.group_name = "moderation"
        self.subgroup_name = "permissions"
        self.description = "Assign a moderator permission to a user."
        self.options = [
            create_option("user", "The mention of the user to modify.", SlashCommandOptionType.STRING, True),
            create_option("permission", "The permission to assign.", SlashCommandOptionType.INTEGER, True, [
                create_choice(ModeratorPermission.MUTE, "Mute users"),
                create_choice(ModeratorPermission.KICK, "Kick users"),
                create_choice(ModeratorPermission.BAN, "Ban users")
            ])
        ]
        self.required_permissions = Permission.ADMINISTRATOR
    
    async def execute(self, context: SlashContext, user: str, permission: ModeratorPermission) -> None:
        await reply(context, f"user: {user}, permission: {permission}")
