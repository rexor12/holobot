import unittest
from dataclasses import dataclass
from typing import TypeVar, cast

from holobot.sdk.serialization import json_type_hierarchy_root
from holobot.sdk.serialization.json_serializer import JsonSerializer

T = TypeVar("T")

@json_type_hierarchy_root()
@dataclass
class ValueWrapper:
    pass

@dataclass
class IntValueWrapper(ValueWrapper):
    value: int

@dataclass
class BoolValueWrapper(ValueWrapper):
    value: bool

@dataclass
class StrValueWrapper(ValueWrapper):
    value: str

@dataclass
class MyDataClass:
    int_field: int
    str_field: str
    dict_field: dict[str, ValueWrapper]
    list_field: list[int]

class TestJsonSerializer(unittest.TestCase):
    def test_serialize_primitives(self):
        test_cases = (
            (int, -100),
            (int, 0),
            (int, 100),
            (float, -1.2),
            (float, 0),
            (float, 1.2),
            (str, "Hello World!"),
            (str, "[\"Complex\"] with escapable characters, including unicőde: \u23FA"),
            (bool, True),
            (bool, False)
        )

        for object_type, value in test_cases:
            with self.subTest(object_type=object_type, value=value):
                serializer = JsonSerializer()
                serialized_value = serializer.serialize(value)
                deserialized_value = serializer.deserialize(object_type, serialized_value)
                self.assertEqual(deserialized_value, value)

    def test_serialize_float(self):
        test_cases = (
            (float, -1.2),
            (float, 0),
            (float, 1.2)
        )

        for object_type, value in test_cases:
            with self.subTest(object_type=object_type, value=value):
                serializer = JsonSerializer()

                serialized_value = serializer.serialize(value)
                result = serializer.deserialize(object_type, serialized_value)

                self.assertIsNotNone(result)
                result = cast(float, result)
                self.assertAlmostEqual(result, value)

    def test_serialize_list(self):
        value = [1, 2, 3, 4, 5, 6]
        serializer = JsonSerializer()

        serialized_value = serializer.serialize(value)
        result = serializer.deserialize(list[int], serialized_value)

        self.assertIsNotNone(result)
        result = cast(list[int], result)
        self.assertEqual(len(result), len(value))
        for item in result:
            self.assertTrue(item in value)

    def test_serialize_dataclass(self):
        value = MyDataClass(
            int_field=123,
            str_field="Héllő, \"Wörld\"!",
            dict_field={
                "number": IntValueWrapper(456000),
                "bool": BoolValueWrapper(True),
                "string": StrValueWrapper("Does this work?")
            },
            list_field=[1, 2, 3, 4, 5, 6]
        )

        serializer = JsonSerializer((IntValueWrapper, BoolValueWrapper, StrValueWrapper))
        serialized_value = serializer.serialize(value)
        result = serializer.deserialize(MyDataClass, serialized_value)

        self.assertIsNotNone(result)
        result = cast(MyDataClass, result)
        self.assertEqual(result.int_field, value.int_field)
        self.assertEqual(result.str_field, value.str_field)
        self.assertEqual(len(result.dict_field), len(value.dict_field))
        for dict_key, dict_value in result.dict_field.items():
            self.assertTrue(dict_key in value.dict_field)
            self.assertEqual(dict_value, value.dict_field[dict_key])
        self.assertEqual(len(result.list_field), len(value.list_field))
        for item in result.list_field:
            self.assertTrue(item in value.list_field)
