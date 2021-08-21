from .imenu_item import IMenuItem
from discord_slash.context import MenuContext

class IMenuItemExecutionRule:
    """Interface for a menu item execution rule.

    A rule is responsible for determining if a menu item's execution should be interrupted.
    """

    async def should_halt(self, menu_item: IMenuItem, context: MenuContext) -> bool:
        """Determines if a given menu item should not be executed in the given context.

        Parameters
        ----------
        menu_item : ``IMenuItem``
            The menu item to be validated.

        context : ``MenuContext``
            The current menu item context.
        
        Returns
        -------
        bool
            True, if the menu item should not be executed in the given context.
        """

        raise NotImplementedError
