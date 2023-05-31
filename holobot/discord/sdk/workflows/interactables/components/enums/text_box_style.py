from enum import IntEnum, unique

@unique
class TextBoxStyle(IntEnum):
    """Defines valid values for styling text boxes."""

    SINGLE_LINE = 0
    """The text box allows only a single line as input."""

    MULTI_LINE = 1
    """The text box allows multiple lines as input."""
