from .models import ServerData

class IServerDataProvider:
    def get_basic_data_by_id(self, server_id: str) -> ServerData:
        raise NotImplementedError
