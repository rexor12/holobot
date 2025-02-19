from holobot.discord.sdk.exceptions import ServerNotFoundError, UserNotFoundError
from holobot.discord.sdk.servers import IMemberDataProvider

def color_to_hex(color: int | None, alpha: int = 0x32) -> str | None:
    return f"#{color:0>6X}{alpha:2X}" if color is not None else None

async def get_user_name_with_color(
    member_data_provider: IMemberDataProvider,
    server_id: int,
    user_id: int
) -> tuple[str, int | None]:
    try:
        user_data = await member_data_provider.get_basic_data_by_id(server_id, user_id)

        return (
            (user_data.name, user_data.color)
            if user_data
            else (str(user_id), None)
        )
    except (ServerNotFoundError, UserNotFoundError):
        return (str(user_id), None)

async def get_user_name_with_hex_color(
    member_data_provider: IMemberDataProvider,
    server_id: int,
    user_id: int
) -> tuple[str, str | None]:
    user_name, color = await get_user_name_with_color(
        member_data_provider,
        server_id,
        user_id
    )

    return (
        user_name,
        color_to_hex(color)
    )
