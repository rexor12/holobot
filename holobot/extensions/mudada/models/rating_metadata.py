from dataclasses import dataclass

@dataclass(kw_only=True)
class RatingMetadata:
    source_user_id: int
