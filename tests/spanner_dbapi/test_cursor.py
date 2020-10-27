# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""Cursor() class unit tests."""

import unittest
from unittest import mock

from google.api_core.exceptions import Aborted
from google.cloud.spanner_dbapi import connect, InterfaceError
from google.cloud.spanner_dbapi.checksum import ResultsChecksum
from google.cloud.spanner_dbapi.cursor import ColumnInfo


class TestCursor(unittest.TestCase):
    def test_close(self):
        with mock.patch(
            "google.cloud.spanner_v1.instance.Instance.exists",
            return_value=True,
        ):
            with mock.patch(
                "google.cloud.spanner_v1.database.Database.exists",
                return_value=True,
            ):
                connection = connect("test-instance", "test-database")

        cursor = connection.cursor()
        self.assertFalse(cursor.is_closed)

        cursor.close()

        self.assertTrue(cursor.is_closed)
        with self.assertRaises(InterfaceError):
            cursor.execute("SELECT * FROM database")

    def test_connection_closed(self):
        with mock.patch(
            "google.cloud.spanner_v1.instance.Instance.exists",
            return_value=True,
        ):
            with mock.patch(
                "google.cloud.spanner_v1.database.Database.exists",
                return_value=True,
            ):
                connection = connect("test-instance", "test-database")

        cursor = connection.cursor()
        self.assertFalse(cursor.is_closed)

        connection.close()

        self.assertTrue(cursor.is_closed)
        with self.assertRaises(InterfaceError):
            cursor.execute("SELECT * FROM database")

    def test_executemany_on_closed_cursor(self):
        with mock.patch(
            "google.cloud.spanner_v1.instance.Instance.exists",
            return_value=True,
        ):
            with mock.patch(
                "google.cloud.spanner_v1.database.Database.exists",
                return_value=True,
            ):
                connection = connect("test-instance", "test-database")

        cursor = connection.cursor()
        cursor.close()

        with self.assertRaises(InterfaceError):
            cursor.executemany(
                """SELECT * FROM table1 WHERE "col1" = @a1""", ()
            )

    def test_executemany(self):
        operation = """SELECT * FROM table1 WHERE "col1" = @a1"""
        params_seq = ((1,), (2,))

        with mock.patch(
            "google.cloud.spanner_v1.instance.Instance.exists",
            return_value=True,
        ):
            with mock.patch(
                "google.cloud.spanner_v1.database.Database.exists",
                return_value=True,
            ):
                connection = connect("test-instance", "test-database")

        cursor = connection.cursor()
        with mock.patch(
            "google.cloud.spanner_dbapi.cursor.Cursor.execute"
        ) as execute_mock:
            cursor.executemany(operation, params_seq)

        execute_mock.assert_has_calls(
            (mock.call(operation, (1,)), mock.call(operation, (2,)))
        )

    def test_fetchone_retry_aborted(self):
        """Check that aborted fetch re-executing transaction."""
        with mock.patch(
            "google.cloud.spanner_v1.instance.Instance.exists",
            return_value=True,
        ):
            with mock.patch(
                "google.cloud.spanner_v1.database.Database.exists",
                return_value=True,
            ):
                connection = connect("test-instance", "test-database")

        cursor = connection.cursor()
        cursor._checksum = ResultsChecksum()

        with mock.patch(
            "google.cloud.spanner_dbapi.cursor.Cursor.__next__",
            side_effect=(Aborted("Aborted"), None),
        ):
            with mock.patch(
                "google.cloud.spanner_dbapi.connection.Connection.retry_transaction"
            ) as retry_mock:

                cursor.fetchone()

                retry_mock.assert_called_once()

    def test_fetchone_retry_aborted_statements(self):
        """Check that retried transaction executing the same statements."""
        row = ["field1", "field2"]
        with mock.patch(
            "google.cloud.spanner_v1.instance.Instance.exists",
            return_value=True,
        ):
            with mock.patch(
                "google.cloud.spanner_v1.database.Database.exists",
                return_value=True,
            ):
                connection = connect("test-instance", "test-database")

        cursor = connection.cursor()
        cursor._checksum = ResultsChecksum()
        cursor._checksum.consume_result(row)

        statement = {
            "sql": "SELECT 1",
            "params": [],
            "param_types": {},
            "checksum": cursor._checksum,
        }
        connection._statements.append(statement)

        with mock.patch(
            "google.cloud.spanner_dbapi.cursor.Cursor.__next__",
            side_effect=(Aborted("Aborted"), None),
        ):
            with mock.patch(
                "google.cloud.spanner_dbapi.connection.Connection.run_statement",
                return_value=([row], ResultsChecksum()),
            ) as run_mock:

                cursor.fetchone()

                run_mock.assert_called_with(statement, retried=True)

    def test_fetchone_retry_aborted_statements_checksums_mismatch(self):
        """Check transaction retrying with underlying data being changed."""
        row = ["field1", "field2"]
        row2 = ["updated_field1", "field2"]

        with mock.patch(
            "google.cloud.spanner_v1.instance.Instance.exists",
            return_value=True,
        ):
            with mock.patch(
                "google.cloud.spanner_v1.database.Database.exists",
                return_value=True,
            ):
                connection = connect("test-instance", "test-database")

        cursor = connection.cursor()
        cursor._checksum = ResultsChecksum()
        cursor._checksum.consume_result(row)

        statement = {
            "sql": "SELECT 1",
            "params": [],
            "param_types": {},
            "checksum": cursor._checksum,
        }
        connection._statements.append(statement)

        with mock.patch(
            "google.cloud.spanner_dbapi.cursor.Cursor.__next__",
            side_effect=Aborted("Aborted"),
        ):
            with mock.patch(
                "google.cloud.spanner_dbapi.connection.Connection.run_statement",
                return_value=([row2], ResultsChecksum()),
            ) as run_mock:

                with self.assertRaises(Aborted):
                    cursor.fetchone()

                run_mock.assert_called_with(statement, retried=True)


class TestColumns(unittest.TestCase):
    def test_ctor(self):
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
        fields = ("col-name", 8, 5, 10, 3, None, False)
        cols = ColumnInfo(*fields)

        for i in range(0, 7):
            self.assertEqual(cols[i], fields[i])

    def test___str__(self):
        cols = ColumnInfo("col-name", 8, None, 10, 3, None, False)

        self.assertEqual(
            str(cols),
            "ColumnInfo(name='col-name', type_code=8, internal_size=10, precision='3')",
        )
