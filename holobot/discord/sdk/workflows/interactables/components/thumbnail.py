from dataclasses import dataclass

from .attachment_url import AttachmentUrl
from .component_base import ComponentBase

@dataclass(kw_only=True)
class Thumbnail(ComponentBase):
    """A component usable in section components only, that displays an image thumbnail, similar to embeds."""

    media: str | AttachmentUrl
    """Either the URL to an external media or an attachment."""

    description: str | None = None
    """An optional description that serves as the alt text for the media."""

    is_spoiler: bool = False
    """Whether the media should be marked as spoiler."""
