from .models import CommandRule

class CommandRuleManagerInterface:
    async def set_rule(self, rule: CommandRule) -> int:
        raise NotImplementedError
