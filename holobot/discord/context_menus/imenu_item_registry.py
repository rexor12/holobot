from discord_slash import SlashCommand

class IMenuItemRegistry:
    def register_menu_items(self, slash: SlashCommand) -> None:
        raise NotImplementedError
