from dataclasses import dataclass

@dataclass(kw_only=True)
class AttachmentUrl:
    filename: str

    @property
    def raw_url(self) -> str:
        return f"attachment://{self.filename}"

    def __str__(self) -> str:
        return self.raw_url
