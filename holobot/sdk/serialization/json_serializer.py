import inspect
import json
from collections.abc import Callable, Iterable, Sequence
from dataclasses import is_dataclass
from datetime import datetime
from enum import Enum
from io import StringIO
from typing import Any, TypeVar, cast, get_args, get_origin

from dateutil.parser import isoparse

from holobot.sdk.utils.dataclass_utils import (
    DictionaryTypeDescriptor, ObjectTypeDescriptor, get_parameter_infos
)
from holobot.sdk.utils.type_utils import get_fully_qualified_name
from .ijson_serializer_internal import IJsonSerializerInternal
from .json_type_hierarchy_root import _JSON_TYPE_HIERARCHY_ROOT_ATTR

T = TypeVar("T")

_TYPE_KEY: str = "$type"

_DESERIALIZERS: dict[type, Callable[[IJsonSerializerInternal, type, Any], Any]] = {
    str: lambda s, t, obj: obj,
    bool: lambda s, t, obj: obj if isinstance(obj, bool) else str(obj).lower() == "true",
    int: lambda s, t, obj: int(obj) if obj is not None else 0,
    float: lambda s, t, obj: float(obj) if obj is not None else 0.0,
    datetime: lambda s, t, obj: isoparse(obj) if obj else None,
    dict: lambda s, t, obj: s._deserialize_dict(t, obj),
    list: lambda s, t, obj: s._deserialize_list(t, obj)
}

_ESCAPE_CHARACTERS = {
    '"': r'\"',
    '\\': r'\\',
    '/': r'\/',
    '\b': r'\b',
    '\f': r'\f',
    '\n': r'\n',
    '\r': r'\r',
    '\t': r'\t'
}

# TODO Support the (de)serialization of generic types (eg. class MyDataClass(Generic[T]))
class JsonSerializer(IJsonSerializerInternal):
    def __init__(
        self,
        known_types: Iterable[type] | None = None
    ) -> None:
        self.__known_types: dict[str, type] = {}
        for known_type in known_types or ():
            name = get_fully_qualified_name(known_type)
            self.__known_types[name] = known_type

    def deserialize(self, object_type: type[T], json_data: str | dict[str, Any]) -> T | None:
        return self.__deserialize(object_type, json_data)

    def deserialize2(self, json_data: str | dict[str, Any]) -> Any | None:
        return self.__deserialize(None, json_data)

    def serialize(self, obj: Any) -> str:
        buffer = StringIO()
        self.__serialize_instance(buffer, obj)

        return buffer.getvalue()

    def _deserialize_dict(self, dict_type: type, obj: Any) -> dict[Any, Any]:
        parameters = get_args(dict_type)
        return {
            key: self.__deserialize_instance(parameters[1], value)
            for key, value in (obj or {}).items()
        }

    def _deserialize_dataclass(self, object_type: type[T], obj: Any) -> T | None:
        parameter_infos = get_parameter_infos(object_type)
        arguments: dict[str, Any] = {}
        for parameter_info in parameter_infos:
            if parameter_info.collection_constructor is dict:
                if not isinstance(parameter_info.object_type, DictionaryTypeDescriptor):
                    raise TypeError(
                        "Expected the collection parameter's descriptor to be"
                        f" an DictionaryTypeDescriptor, but got {parameter_info.object_type}."
                    )

                argument_items = {
                    key: self.__deserialize_instance(parameter_info.object_type.value_type, value)
                    for key, value in (obj.get(parameter_info.name) or {}).items()
                }
                arguments[parameter_info.name] = argument_items
            elif parameter_info.collection_constructor is not None:
                if not isinstance(parameter_info.object_type, ObjectTypeDescriptor):
                    raise TypeError(
                        "Expected the collection parameter's descriptor to be"
                        f" an ObjectTypeDescriptor, but got {parameter_info.object_type}."
                    )

                argument_items = [
                    self.__deserialize_instance(parameter_info.object_type.value, item)
                    for item in (obj.get(parameter_info.name) or [])
                ]
                arguments[parameter_info.name] = parameter_info.collection_constructor(argument_items)
            else:
                if not isinstance(parameter_info.object_type, ObjectTypeDescriptor):
                    raise TypeError(
                        "Expected the non-collection parameter's descriptor to be"
                        f" an ObjectTypeDescriptor, but got {parameter_info.object_type}."
                    )

                argument = self.__deserialize_instance(
                    parameter_info.object_type.value,
                    obj.get(parameter_info.name)
                )
                if argument is None and not parameter_info.allows_none:
                    if parameter_info.default_value:
                        argument = parameter_info.default_value
                    elif parameter_info.default_factory:
                        argument = parameter_info.default_factory()
                    else:
                        raise TypeError(
                            f"Deserialized None for attribute '{parameter_info.name}'"
                            " which doesn't accept it as a valid value."
                        )
                arguments[parameter_info.name] = argument

        return object_type(**arguments)

    def _deserialize_list(self, list_type: type, obj: Any) -> list[Any]:
        parameters = get_args(list_type)
        return [
            self.__deserialize_instance(parameters[0], item)
            for item in (obj or [])
        ]

    def __deserialize(
        self,
        object_type: type | None,
        json_data: str | dict[str, Any]
    ) -> Any | None:
        json_object = json.loads(json_data) if isinstance(json_data, str) else json_data
        return self.__deserialize_instance(object_type, json_object)

    def __deserialize_instance(
        self,
        object_type: type[T] | None,
        obj: Any
    ) -> T | Any | None:
        if obj is None:
            return None

        is_json_type_hierarchy_root = getattr(object_type, _JSON_TYPE_HIERARCHY_ROOT_ATTR, None)
        if object_type is None or is_json_type_hierarchy_root:
            if not (object_type_descriptor := obj.get(_TYPE_KEY, None)):
                raise TypeError("Cannot deserialize unknown object type.")

            if not (object_type := self.__known_types.get(object_type_descriptor, None)):
                raise TypeError(
                    f"Cannot deserialize unknown object type '{object_type_descriptor}'."
                )
        else:
            origin = get_origin(object_type)
            if deserializer := _DESERIALIZERS.get(origin or object_type, None):
                return deserializer(self, object_type, obj)

        if is_dataclass(object_type):
            return self._deserialize_dataclass(object_type, obj)

        if inspect.isclass(object_type) and issubclass(object_type, Enum):
            if not isinstance(obj, int):
                raise ValueError(
                    f"Expected an enum value to be an int, but got '{type(obj)}'."
                )
            return object_type(obj)

        raise TypeError(f"Cannot deserialize unknown type {object_type}.")

    def __serialize_dataclass(
        self,
        buffer: StringIO,
        obj: Any
    ) -> None:
        object_type = type(obj)
        parameter_infos = get_parameter_infos(object_type)
        buffer.write("{")
        buffer.write(f"\"{_TYPE_KEY}\":\"{get_fully_qualified_name(object_type)}\"")
        if len(parameter_infos) > 0:
            buffer.write(",")

        for index, parameter_info in enumerate(parameter_infos):
            buffer.write("\"")
            buffer.write(parameter_info.name)
            buffer.write("\":")
            self.__serialize_instance(
                buffer,
                getattr(obj, parameter_info.name)
            )
            if index + 1 < len(parameter_infos):
                buffer.write(",")
        buffer.write("}")

    def __serialize_instance(
        self,
        buffer: StringIO,
        obj: Any | None
    ) -> None:
        if obj is None:
            buffer.write("null")
            return

        if isinstance(obj, str):
            JsonSerializer.__serialize_string(buffer, obj)
            return
        elif isinstance(obj, bool):
            buffer.write("true" if obj else "false")
            return
        elif isinstance(obj, (int, float)):
            buffer.write(str(obj))
            return
        elif isinstance(obj, datetime):
            JsonSerializer.__serialize_string(buffer, obj.isoformat())
            return
        elif is_dataclass(obj):
            self.__serialize_dataclass(buffer, obj)
            return

        object_type = type(obj)
        if issubclass(object_type, dict):
            items = cast(dict[str, Any], obj).items()
            buffer.write("{")
            for index, item in enumerate(items):
                name, value = item
                buffer.write(f"\"{name}\":")
                self.__serialize_instance(buffer, value)
                if index + 1 < len(items):
                    buffer.write(",")
            buffer.write("}")
            return
        elif issubclass(object_type, Iterable):
            items = (
                cast(Sequence, obj)
                if issubclass(object_type, Sequence)
                else [*obj]
            )
            buffer.write("[")
            for index, item in enumerate(items):
                self.__serialize_instance(buffer, item)
                if index + 1 < len(items):
                    buffer.write(",")
            buffer.write("]")
            return

        raise TypeError(f"Cannot serialize unsupported type '{object_type}'.")

    @staticmethod
    def __serialize_string(buffer: StringIO, value: str) -> None:
        buffer.write("\"")
        for char in value:
            if (ec := _ESCAPE_CHARACTERS.get(char, None)) is not None:
                buffer.write(ec)
            elif ord(char) < 0x20 or ord(char) > 0x7F:
                buffer.write(r'\u{:04x}'.format(ord(char)))
            else:
                buffer.write(char)
        buffer.write("\"")

DEFAULT_JSON_SERIALIZER = JsonSerializer()

def deserialize(object_type: type[T], json_data: str | dict[str, Any]) -> T | None:
    """Deserializes the given JSON data as the specified type, using the default settings.

    :param object_type: The target type.
    :type object_type: type[T]
    :param json_data: The JSON data to be deserialized.
    :type json_data: str | dict
    :return: If successful, the deserialized instance of the specified type.
    :rtype: T | None
    """

    return DEFAULT_JSON_SERIALIZER.deserialize(object_type, json_data)
