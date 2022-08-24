from __future__ import annotations

class Version:
    def __init__(self, major: int = 0, minor: int = 0, patch: int = 0, build: int = 0):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.build = build

    @classmethod
    def from_file(cls, path: str) -> Version:
        with open(path) as f:
            version_parts = f.read().strip().split(".")
        return cls(*map(int, version_parts))

    @property
    def major(self) -> int:
        return self.__major

    @major.setter
    def major(self, value: int):
        self.__major = value

    @property
    def minor(self) -> int:
        return self.__minor

    @minor.setter
    def minor(self, value: int):
        self.__minor = value

    @property
    def patch(self) -> int:
        return self.__patch

    @patch.setter
    def patch(self, value: int):
        self.__patch = value

    @property
    def build(self) -> int:
        return self.__build

    @build.setter
    def build(self, value: int):
        self.__build = value

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}.{self.build}"
