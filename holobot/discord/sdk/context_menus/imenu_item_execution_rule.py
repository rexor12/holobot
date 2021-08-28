from .imenu_item import IMenuItem
from ..models import InteractionContext

class IMenuItemExecutionRule:
    """Interface for a menu item execution rule.

    A rule is responsible for determining if a menu item's execution should be interrupted.
    """

    async def should_halt(self, menu_item: IMenuItem, context: InteractionContext) -> bool:
        """Determines if a given menu item should not be executed in the given context.

        Parameters
        ----------
        menu_item : ``IMenuItem``
            The menu item to be validated.

        context : ``InteractionContext``
            The interaction context associated to the request.
            The actual type may be a sub-class of this type.
        
        Returns
        -------
        bool
            True, if the menu item should not be executed in the given context.
        """

        raise NotImplementedError
