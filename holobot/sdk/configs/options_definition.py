from typing import Any, ClassVar

class OptionsDefinition:
    section_name: ClassVar[str] = NotImplemented

    def __new__(cls: type, *args, **kwargs) -> Any:
        if cls is OptionsDefinition:
            raise TypeError(f"Only children of '{cls.__name__}' may be instantiated.")
        return super().__new__(cls)

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if cls.section_name is NotImplemented:
            raise NotImplementedError("Sub-classes must specify the configuration section name.")
