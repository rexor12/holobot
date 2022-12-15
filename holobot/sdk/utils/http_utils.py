import urllib.parse

__DEFAULT_ARGS = {}

def build_url(
    base_url: str,
    relative_path: str | tuple[str, ...],
    args: dict[str, str | int | float | bool] | None = None
) -> str:
    if args is None:
        args = __DEFAULT_ARGS

    relative_path_full = (
        "/".join(
            map(
                lambda p: urllib.parse.quote_plus(p.strip("/")),
                relative_path
            )
        )
        if isinstance(relative_path, tuple)
        else relative_path.strip("/")
    )

    url_parts = [base_url.rstrip("/")]
    if relative_path_full:
        url_parts.append("/")
        url_parts.append(relative_path_full)
    if args:
        url_parts.append("?")
        url_parts.append(urllib.parse.urlencode(args))

    return "".join(url_parts)
