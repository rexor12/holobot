class QuotaExhaustedError(Exception):
    """Raised when an API quota is exhausted."""

    def __init__(self, *args):
        super().__init__(*args)
