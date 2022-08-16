from hikari import PartialRole as HikariPartialRole, Role as HikariRole

from holobot.discord.sdk.models import Role

TRole = HikariPartialRole | HikariRole

def to_model(dto: TRole) -> Role:
    return Role(
        id=str(dto.id),
        name=dto.name
    )
