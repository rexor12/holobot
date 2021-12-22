class IBotDataProvider:
    def get_user_id(self) -> str:
        raise NotImplementedError

    def get_avatar_url(self) -> str:
        raise NotImplementedError

    def get_latency(self) -> float:
        raise NotImplementedError

    def get_server_count(self) -> int:
        raise NotImplementedError
