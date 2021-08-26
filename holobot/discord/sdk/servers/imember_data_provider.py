from .models import MemberData
from ..enums import Permission

class IMemberDataProvider:
    def get_basic_data_by_id(self, server_id: str, user_id: str) -> MemberData:
        raise NotImplementedError

    def get_basic_data_by_name(self, server_id: str, name: str) -> MemberData:
        raise NotImplementedError

    def is_member(self, server_id: str, user_id: str) -> bool:
        raise NotImplementedError

    def get_member_permissions(self, server_id: str, channel_id: str, user_id: str) -> Permission:
        raise NotImplementedError
