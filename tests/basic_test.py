#
# Copyright (c) 2020 Carsten Igel.
#
# This file is part of pip-licenses-reader
# (see https://github.com/carstencodes/pip-licenses-reader).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#

import unittest
import tempfile
import os
from pathlib import Path
from typing import FrozenSet, List

import pip_licenses_reader


__ITEM_SOME = """{
    "Author": "Me",
    "Version": "0.1.0",
    "URL": "https://some.site",
    "License": "GPLv3",
    "Name": "SomePackage"
}"""
__ITEM_PIP_LR = """{
    "Author": "Carsten Igel",
    "Version": "0.8.0",
    "URL": "https://github.com/carstencodes/pip-licenses-reader",
    "License": "BSD",
    "Name": "pip_licenses_reader"
}"""
__ITEM_SIMPLE = """{
    "Author": "Somebody",
    "Version": "1.2.3",
    "URL": "https://any.site",
    "License": "MIT",
    "Name": "AnyPackage"
}"""
__ITEM_DEFUNC = '{ "Author": "Me", "Version": "0.1.0" }'

FILE_CONTENT_IS_OBJ = '{ "a": "b" }'
FILE_CONTENT_IS_EMPTY_LIST = "[]"
FILE_CONTENT_THREE_COMPLETE_ITEMS = (
    "[" + __ITEM_SOME + ", " + __ITEM_SIMPLE + ", " + __ITEM_PIP_LR + "]"
)


class _MockFile:
    def __init__(self, content: str) -> None:
        self.__content = content
        self.__temp_file = None

    def __enter__(self) -> Path:
        temp_file = tempfile.mktemp(".json", "pip_lic_read_test")
        with open(temp_file, "w+") as handle:
            handle.write(self.__content)

        self.__temp_file = temp_file
        return temp_file

    def __exit__(self, t, val, tb) -> bool:
        if self.__temp_file:
            os.remove(self.__temp_file)

        self.__temp_file = None

        return False


class EmptyTest(unittest.TestCase):
    def test_default_typing_major_type(self) -> None:
        any_obj = pip_licenses_reader.read_file()
        self.assertTrue(
            isinstance(any_obj, pip_licenses_reader.LicenseCollection)
        )

    def test_default_typing_collection_type(self) -> None:
        any_obj = pip_licenses_reader.read_file()
        self.assertTrue(isinstance(any_obj.projects, frozenset))

    def test_no_file_returns_empty(self) -> None:
        any_obj = pip_licenses_reader.read_file()
        self.assertIsNotNone(any_obj)

    def test_no_file_returns_empty_frozen_set(self) -> None:
        any_obj = pip_licenses_reader.read_file()
        self.assertEqual(len(any_obj.projects), 0)

    def test_file_is_object(self) -> None:
        global FILE_CONTENT_IS_OBJ
        with _MockFile(FILE_CONTENT_IS_OBJ) as mock:
            any_obj = pip_licenses_reader.read_file(mock)
            self.assertIsNotNone(any_obj)

    def test_file_is_object_empty_frozenset(self) -> None:
        global FILE_CONTENT_IS_OBJ
        with _MockFile(FILE_CONTENT_IS_OBJ) as mock:
            any_obj = pip_licenses_reader.read_file(mock)
            self.assertEqual(len(any_obj.projects), 0)

    def test_file_is_list(self) -> None:
        global FILE_CONTENT_IS_EMPTY_LIST
        with _MockFile(FILE_CONTENT_IS_EMPTY_LIST) as mock:
            any_obj = pip_licenses_reader.read_file(mock)
            self.assertIsNotNone(any_obj)

    def test_file_is_list_empty_frozenset(self) -> None:
        global FILE_CONTENT_IS_EMPTY_LIST
        with _MockFile(FILE_CONTENT_IS_EMPTY_LIST) as mock:
            any_obj = pip_licenses_reader.read_file(mock)
            self.assertEqual(len(any_obj.projects), 0)


class FileContentTest(unittest.TestCase):
    def test_file_three_complete_items_success(self) -> None:
        global FILE_CONTENT_THREE_COMPLETE_ITEMS
        with _MockFile(FILE_CONTENT_THREE_COMPLETE_ITEMS) as mock:
            any_obj = pip_licenses_reader.read_file(mock)
            self.assertIsNotNone(any_obj)
            self.assertEqual(len(any_obj.projects), 3)

    def test_file_three_complete_items_content_two(self) -> None:
        global FILE_CONTENT_THREE_COMPLETE_ITEMS
        with _MockFile(FILE_CONTENT_THREE_COMPLETE_ITEMS) as mock:
            any_obj = pip_licenses_reader.read_file(mock)
            project: pip_licenses_reader.ProjectInfo = (
                FileContentTest.sort_items(any_obj.projects)[1]
            )
            self.assertEqual(project.author, "Me")
            self.assertEqual(project.version, "0.1.0")
            self.assertEqual(project.url, "https://some.site")
            self.assertEqual(project.license, "GPLv3")
            self.assertEqual(project.name, "SomePackage")

    def test_file_three_complete_items_content_three(self) -> None:
        global FILE_CONTENT_THREE_COMPLETE_ITEMS
        with _MockFile(FILE_CONTENT_THREE_COMPLETE_ITEMS) as mock:
            any_obj = pip_licenses_reader.read_file(mock)
            project: pip_licenses_reader.ProjectInfo = (
                FileContentTest.sort_items(any_obj.projects)[2]
            )
            self.assertEqual(project.author, "Carsten Igel")
            self.assertEqual(project.version, "0.8.0")
            self.assertEqual(
                project.url,
                "https://github.com/carstencodes/pip-licenses-reader",
            )
            self.assertEqual(project.license, "BSD")
            self.assertEqual(project.name, "pip_licenses_reader")

    def test_file_three_complete_items_content_one(self) -> None:
        global FILE_CONTENT_THREE_COMPLETE_ITEMS
        with _MockFile(FILE_CONTENT_THREE_COMPLETE_ITEMS) as mock:
            any_obj = pip_licenses_reader.read_file(mock)
            project: pip_licenses_reader.ProjectInfo = (
                FileContentTest.sort_items(any_obj.projects)[0]
            )
            self.assertEqual(project.author, "Somebody")
            self.assertEqual(project.version, "1.2.3")
            self.assertEqual(project.url, "https://any.site")
            self.assertEqual(project.license, "MIT")
            self.assertEqual(project.name, "AnyPackage")

    @staticmethod
    def sort_items(
        items: FrozenSet[pip_licenses_reader.ProjectInfo],
    ) -> List[pip_licenses_reader.ProjectInfo]:
        result = list(items)
        result.sort(key=lambda p: p.name)
        return result


if __name__ == "__main__":
    unittest.main()
