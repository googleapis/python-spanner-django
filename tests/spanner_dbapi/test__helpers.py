# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""Cloud Spanner DB-API Connection class unit tests."""

import unittest

# from unittest import mock


class TestHelpers(unittest.TestCase):
    def test_execute_insert_heterogenous(self):
        pass

    def test_execute_insert_homogenous(self):
        pass

    def test_handle_insert(self):
        pass


class TestColumnInfo(unittest.TestCase):
    def test_ctor(self):
        from google.cloud.spanner_dbapi.cursor import ColumnInfo

        name = "col-name"
        type_code = 8
        display_size = 5
        internal_size = 10
        precision = 3
        scale = None
        null_ok = False

        cols = ColumnInfo(
            name,
            type_code,
            display_size,
            internal_size,
            precision,
            scale,
            null_ok,
        )

        self.assertEqual(cols.name, name)
        self.assertEqual(cols.type_code, type_code)
        self.assertEqual(cols.display_size, display_size)
        self.assertEqual(cols.internal_size, internal_size)
        self.assertEqual(cols.precision, precision)
        self.assertEqual(cols.scale, scale)
        self.assertEqual(cols.null_ok, null_ok)
        self.assertEqual(
            cols.fields,
            (
                name,
                type_code,
                display_size,
                internal_size,
                precision,
                scale,
                null_ok,
            ),
        )

    def test___get_item__(self):
        from google.cloud.spanner_dbapi.cursor import ColumnInfo

        fields = ("col-name", 8, 5, 10, 3, None, False)
        cols = ColumnInfo(*fields)

        for i in range(0, 7):
            self.assertEqual(cols[i], fields[i])

    def test___str__(self):
        from google.cloud.spanner_dbapi.cursor import ColumnInfo

        cols = ColumnInfo("col-name", 8, None, 10, 3, None, False)

        self.assertEqual(
            str(cols),
            "ColumnInfo(name='col-name', type_code=8, internal_size=10, precision='3')",
        )
