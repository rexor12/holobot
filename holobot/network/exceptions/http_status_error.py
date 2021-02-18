class HttpStatusError(Exception):
    def __init__(self, status_code: int, message: str = None, **attrs):
        super().__init__(message)
        self.status_code = status_code
        self.attrs = attrs