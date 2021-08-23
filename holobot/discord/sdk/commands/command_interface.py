from .models import CommandResponse, ServerChatInteractionContext
from ..enums import Permission
from typing import Any, Dict, List, Optional, Tuple

class CommandInterface:
    @property
    def group_name(self) -> Optional[str]:
        return self.__group_name
    
    @group_name.setter
    def group_name(self, value: Optional[str]) -> None:
        self.__group_name = value
        
    @property
    def subgroup_name(self) -> Optional[str]:
        return self.__subgroup_name
    
    @subgroup_name.setter
    def subgroup_name(self, value: Optional[str]) -> None:
        self.__subgroup_name = value
        
    @property
    def name(self) -> str:
        return self.__name
    
    @name.setter
    def name(self, value: str) -> None:
        self.__name = value
        
    @property
    def description(self) -> Optional[str]:
        return self.__description
    
    @description.setter
    def description(self, value: Optional[str]) -> None:
        self.__description = value
    
    @property
    def options(self) -> List[Dict[str, Any]]:
        return self.__options
    
    @options.setter
    def options(self, value: List[Dict[str, Any]]) -> None:
        self.__options = value
    
    @property
    def required_permissions(self) -> Permission:
        return self.__required_permissions
    
    @required_permissions.setter
    def required_permissions(self, value: Permission) -> None:
        self.__required_permissions = value

    async def execute(self, context: ServerChatInteractionContext, **kwargs) -> CommandResponse:
        """Executes the behavior associated to this command.
        
        Parameters
        ----------
        context : ``ServerChatInteractionContext``
            The interaction context associated to the request.
        
        Returns
        -------
        ``CommandResponse``
            The response from the execution of the request.
            The actual type may be a sub-class of this type.
        """

        raise NotImplementedError
    
    async def is_allowed_for_guild(self, guild_id: int) -> bool:
        """Determines if the command is allowed for a specific guild.

        Determines if the command is allowed for the guild with the specified identifier.

        Parameters
        ----------
        guild_id : int
            The identifier of the guild to check.
        
        Returns
        -------
        bool
            True, if the command is allowed for the specified guild.
        """

        raise NotImplementedError
    
    async def get_allowed_guild_ids(self) -> Tuple[int, ...]:
        """Get the allowed guilds' identifiers.

        Get a list of guild identifiers for which the command is available.

        Returns
        -------
        int tuple
            The list of guild identifiers.
        
        Remarks
        -------
        If the returned list is empty, it means the command is a global command.
        """

        raise NotImplementedError
