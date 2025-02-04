from dataclasses import dataclass

from holobot.sdk.database.entities import Identifier

@dataclass(kw_only=True)
class Valentine2025RatingId(Identifier):
    source_user_id: int
    target_user_id: int

    def __str__(self) -> str:
        return f"Valentine2025RatingId/{self.source_user_id}/{self.target_user_id}"

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Valentine2025RatingId):
            return False

        return (
            self.source_user_id == value.source_user_id
            and self.target_user_id == value.target_user_id
        )

    @staticmethod
    def create(source_user_id: int, target_user_id: int) -> 'Valentine2025RatingId':
        return Valentine2025RatingId(
            source_user_id=source_user_id,
            target_user_id=target_user_id
        )
