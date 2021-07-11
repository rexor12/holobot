from typing import Dict, Optional, Tuple

class CommandRegistryInterface:
    def command_exists(self, command_name: str, group_name: Optional[str] = None, subgroup_name: Optional[str] = None) -> bool:
        raise NotImplementedError
    
    def group_exists(self, group_name: str) -> bool:
        raise NotImplementedError
    
    def get_commands(self) -> Dict[str, Dict[str, Tuple[str, ...]]]:
        raise NotImplementedError
