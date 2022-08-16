from hikari import (
    CustomEmoji as HikariCustomEmoji,
    Emoji as HikariEmoji,
    KnownCustomEmoji as HikariKnownCustomEmoji,
    UnicodeEmoji as HikariUnicodeEmoji
)
from holobot.discord.sdk.models import Emoji

TEmoji = HikariCustomEmoji | HikariEmoji | HikariKnownCustomEmoji | HikariUnicodeEmoji

def to_model(dto: TEmoji) -> Emoji:
    identifier = None
    # Not setting URL for UnicodeEmoji
    # because it relies on 3rd party software
    # which may be unreliable. See its docstring.
    url = None
    if isinstance(dto, (HikariCustomEmoji, HikariKnownCustomEmoji)):
        identifier = dto.id
        url = dto.url

    return Emoji(
        identifier=str(identifier) if identifier else None,
        url=url,
        mention=dto.mention,
        is_known=True
    )
