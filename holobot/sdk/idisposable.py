# NOTE: Doesn't inherit from Protocol, because isinstance checks don't work then.
class IDisposable:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._on_dispose()

    def dispose(self) -> None:
        self._on_dispose()

    def _on_dispose(self) -> None:
        ...
