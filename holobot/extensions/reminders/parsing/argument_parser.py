from enum import IntEnum, unique
from typing import Dict, Tuple

DEFAULT_BREAK_CHARS = (" ",)
UNBOUND_KEY = "__unbound"

@unique
class ParserState(IntEnum):
    PARSING_KEY = 0,
    PARSING_VALUE = 1,
    PARSING_UNBOUND = 2

class State:
    def __init__(self, keys: Tuple[str, ...], break_chars: Tuple[str, ...] = DEFAULT_BREAK_CHARS) -> None:
        self.args: Dict[str, str] = { UNBOUND_KEY: "" }
        for key in keys:
            self.args[key] = ""
        self.state: ParserState = ParserState.PARSING_KEY
        self.buffer: str = ""
        self.break_chars: Tuple[str, ...] = break_chars
        self.key: str = ""

def parse_arguments(keys: Tuple[str, ...], value: str, break_chars: Tuple[str, ...] = DEFAULT_BREAK_CHARS) -> Dict[str, str]:
    if UNBOUND_KEY in keys:
        raise ValueError("The reserved unbound key cannot be among the keys.")
    state: State = State(keys, break_chars)
    for char in value:
        __on_char(state, char)
    __flush(state)
    return state.args

def __flush(state: State) -> None:
    if len(state.buffer) == 0:
        return
    
    # If it's a value, we just assign it to the associated key.
    if state.state == ParserState.PARSING_VALUE:
        state.args[state.key] = state.buffer
        state.key = state.buffer = ""
        return
    
    # Otherwise, we'll assume it's the unbound string.
    state.args[UNBOUND_KEY] = state.buffer
    state.buffer = state.key = ""

def __on_char(state: State, char: str) -> None:
    if state.state == ParserState.PARSING_KEY:
        __on_char_parsing_key(state, char)
    elif state.state == ParserState.PARSING_VALUE:
        __on_char_parsing_value(state, char)
    elif state.state == ParserState.PARSING_UNBOUND:
        __on_char_parsing_unbound(state, char)
    else:
        raise ValueError("The parser is in an invalid state.")

def __on_char_parsing_key(state: State, char: str) -> None:
    # Not a break yet.
    if not char in state.break_chars:
        state.buffer += char
        return
    
    # We have a key.
    if state.buffer in state.args.keys():
        state.key = state.buffer
        state.buffer = ""
        state.state = ParserState.PARSING_VALUE
        return
    
    # Not a key, so we move on to the unbound string.
    state.buffer += char
    state.state = ParserState.PARSING_UNBOUND

def __on_char_parsing_value(state: State, char: str) -> None:
    # Not a break yet.
    if not char in state.break_chars:
        state.buffer += char
        return
    
    # We have the value.
    state.args[state.key] = state.buffer
    state.buffer = state.key = ""
    state.state = ParserState.PARSING_KEY

def __on_char_parsing_unbound(state: State, char: str) -> None:
    state.buffer += char
    state.args[UNBOUND_KEY] = state.buffer
