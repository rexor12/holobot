from holobot.sdk.utils.string_utils import try_parse_int

def get_custom_int(custom_data: dict[str, str], key: str, default_value: int | None = None) -> int | None:
    value = custom_data.get(key, None)
    if value is None:
        return default_value

    typed_value = try_parse_int(value)

    return typed_value if typed_value is not None else default_value
