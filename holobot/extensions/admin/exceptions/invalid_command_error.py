class InvalidCommandError(Exception):
    @property
    def command_name(self) -> str | None:
        return self.__command_name

    @command_name.setter
    def command_name(self, value: str | None) -> None:
        self.__command_name = value

    @property
    def group_name(self) -> str | None:
        return self.__group_name

    @group_name.setter
    def group_name(self, value: str | None) -> None:
        self.__group_name = value

    @property
    def subgroup_name(self) -> str | None:
        return self.__subgroup_name

    @subgroup_name.setter
    def subgroup_name(self, value: str | None) -> None:
        self.__subgroup_name = value

    def __init__(
        self,
        command_name: str | None,
        group_name: str | None,
        subgroup_name: str | None,
        *args
    ) -> None:
        super().__init__(*args)
        self.command_name = command_name
        self.group_name = group_name
        self.subgroup_name = subgroup_name

    def __str__(self) -> str:
        return f"{super().__str__()}\nCommand: {self.command_name}, group: {self.group_name}, subgroup: {self.subgroup_name}"
