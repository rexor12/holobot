from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True)
class Language:
    """Holds information about a language."""

    code: str
    """The ISO-639-1 language code."""

    name: str
    """The name of the language intended for UI display."""
