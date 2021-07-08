from .models import Version

class EnvironmentInterface:
    @property
    def root_path(self) -> str:
        raise NotImplementedError

    @property
    def version(self) -> Version:
        raise NotImplementedError

    async def is_debug_mode(self) -> bool:
        raise NotImplementedError
