class FeatureDisabledError(Exception):
    """Raised when the requested feature is disabled."""

    def __init__(self, *args):
        super().__init__(*args)
