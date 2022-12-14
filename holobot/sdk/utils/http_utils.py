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
    return (
        base_url.rstrip("/")
        + "/"
        + relative_path_full
        + "?"
        + urllib.parse.urlencode(args)
    )
