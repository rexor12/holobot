from typing import Optional
from .. import CommandRuleManagerInterface
from ..enums import RuleState
from ..models import CommandRule
from discord.ext.commands.cog import Cog
from discord_slash import cog_ext, SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_choice, create_option
from holobot.discord.bot import Bot
from holobot.discord.sdk.commands.decorators import register_command
from holobot.discord.sdk.utils import reply
from holobot.sdk.logging import LogInterface

import re

# By default (when the bot joins), all of the commands are allowed in every channel.
# Let's make sure we allow commands to be used in #bots only:
#   /admin commandrule state: allow channel: #bots
# Let's disable hentai related commands, because we don't want people to use them in #bots:
#   /admin commandrule state: forbid group: hentai
# But we have a special room where we want to allow it:
#   /admin commandrule state: allow group: hentai channel: #lewd
# Still, we want to disable the hardcore command even there:
#   /admin commandrule state: forbid group: hentai command: bdsm
#
# So, we can observe the rule precedence from the above example:
# 1. Global rules that specify neither a command nor a group.
# 2. Group rules that specify no command.
# 3. Command rules.
# Rules with no channels specified are applied first:
#   If the rule is an allow rule, the related commands become disabled everywhere else.
#   If the rule is a forbid rule, the related commands are forbidden in that channel only.
#       If no channel is specified, they are forbidden everywhere.
# Also the same type of rule isn't allowed twice (ie. forbid and allow at the same time), for example:
#   /admin commandrule state: allow channel: #bots
#   /admin commandrule state: forbid channel: #bots
#
# Complex example:
# We want to enable "hentai" commands only in "lewds", except for "bdsm",
# which should be disabled everywhere. We want to disable the rest in #lewds.
# We already have rules set up that disable all commands in "general"
# and "voice-context" and a rule that enables "voice" commands in "voice-context".
# We want to keep these rules.
#
# So this is what's set up already:
#   /admin commandrule state: forbid channel: #general
#   /admin commandrule state: forbid channel: #voice-context
#   /admin commandrule state: allow group: voice channel: #voice-context
# And these are the new rules:
#   /admin commandrule state: allow group: hentai channel: #lewds
#   /admin commandrule state: forbid group: hentai command: bdsm
#   /admin commandrule state: forbid group: hentai
#
# When a user goes to #lewds and types "/hentai bdsm" the following logic is executed:
#   1. Default state (the command is allowed)
#   2. Global rules (no group, no command, channel: all/#lewds)
#   3. Group rule (group, channel: all/#lewds)
#       - forbid hentai (the command is forbidden)
#       - allow hentai * #lewds (the command is allowed)
#   4. Command rules (command, channel: all/#lewds)
#       - forbid hentai bdsm #lewds (the command is forbidden)
# 
# Database table for rules:
#   - id: The identifier of the rule.
#   - created_at: When the rule was created/changed.
#   - created_by: The identifier of the user who created the rule.
#   - server_id: Which server the rule belongs to.
#   - state: Allow/forbid.
#   - group: The name of the command group, if any.
#   - command: The name of the command, if any.
#   - channel: The identifier of the related channel, if any.
# 
# Setup wizard:
# $ /admin command rulewizard
# 
# Would you like to _allow_ or _forbid_ a command?
# [V] [X]   <- reactions :white_check_mark: and :no_entry:
# $ (reacts with whichever)
# 
# Would you like the rule to apply to specific channels only?
# [V] [X]
# $ (reacts with yes)
# 
# Please, link all the channels separated by spaces (eg. "#general #art").
# $ #general #art #programming
# 
# Which group of commands is it?
# $ hentai
# 
# Would you like the rule to apply to the entire group?
# [V] [X]
# $ (reacts with no)
# 
# Please, list all the commands separated by spaces (eg. "roll roulette").
# $ nhentai ehentai
# 
# The commands _nhentai_ and _ehentai_ of the group _hentai_ are now **forbidden** in #general, #art and #programming.

channel_regex = re.compile(r"^<#(?P<id>\d+)>$")

class Rules(Cog, name="Rules"):
    def __init__(self, bot: Bot):
        super().__init__()
        self.__log = bot.service_collection.get(LogInterface).with_name("Admin", "Features")
        self.__command_rule_manager: CommandRuleManagerInterface = bot.service_collection.get(CommandRuleManagerInterface)
    
    @register_command
    @cog_ext.cog_subcommand(base="admin", subcommand_group="command", name="setrule", options=[
        create_option("state", "Whether to allow or forbid commands.", SlashCommandOptionType.STRING, True, [
            create_choice("Allow", "Allow"),
            create_choice("Forbid", "Forbid")
        ]),
        create_option("group", "An entire command group, such as \"admin\".", SlashCommandOptionType.STRING, False),
        create_option("command", "A command inside a command group, such as \"roll\".", SlashCommandOptionType.STRING, False),
        create_option("channel", "The link of the applicable channel.", SlashCommandOptionType.STRING, False)
    ], guild_ids=[822228166381797427])
    async def slash_set_command_rule(self, context: SlashContext, state: str, group: Optional[str] = None, command: Optional[str] = None, channel: Optional[str] = None):
        if context.guild is None:
            await reply(context, "Command rules can be defined in servers only.")
            return
        channel_id: Optional[str] = None
        if channel is not None:
            if (channel_match := channel_regex.match(channel)) is None:
                await reply(context, "Invalid channel. Did you link it properly?")
                return
            channel_id = channel_match.group("id")
        rule = CommandRule()
        rule.created_by = str(context.author_id)
        rule.server_id = str(context.guild.id)
        rule.state = RuleState.parse(state)
        rule.group = group
        rule.command = command
        rule.channel_id = channel_id
        await self.__command_rule_manager.set_rule(rule)
        await reply(context, f"Your rule has been set: {rule.textify()}")

def setup(bot: Bot):
    bot.add_cog(Rules(bot))
