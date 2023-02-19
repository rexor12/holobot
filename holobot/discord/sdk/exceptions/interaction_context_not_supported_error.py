class InteractionContextNotSupportedError(Exception):
    def __init__(self) -> None:
        super().__init__("The specified interaction context isn't supported.")
