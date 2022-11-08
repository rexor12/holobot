from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True)
class Translation:
    """Represents a translation of some text."""

    source_text: str
    """The text to be translated."""

    source_language: str
    """The language code of the source text.

    When the source language isn't specified manually,
    it is automatically detected by the translation service.
    """

    result_text: str
    """The translation of the source text."""

    result_language: str
    """The language code of the translation."""
