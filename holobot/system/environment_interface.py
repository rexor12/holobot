from .models import Version

class EnvironmentInterface:
    @property
    def version(self) -> Version:
        return self.__version
    
    @version.setter
    def version(self, value: Version):
        self.__version = value