# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""Cursor() class unit tests."""

import unittest
import mock


class TestCursor(unittest.TestCase):

    INSTANCE = "test-instance"
    DATABASE = "test-database"

    def test_property_connection(self):
        from google.cloud.spanner_dbapi import Connection, Cursor

        connection = Connection(self.INSTANCE, self.DATABASE)
        cursor = Cursor(connection)
        self.assertEqual(cursor.connection, connection)

    def test_property_description(self):
        from google.cloud.spanner_dbapi import Connection, Cursor
        from google.cloud.spanner_dbapi._helpers import ColumnInfo

        connection = Connection(self.INSTANCE, self.DATABASE)
        cursor = Cursor(connection)
        self.assertIsNone(cursor.description)
        cursor._result_set = res_set = mock.MagicMock()
        res_set.metadata.row_type.fields = [mock.MagicMock()]
        self.assertIsNotNone(cursor.description)
        self.assertIsInstance(cursor.description[0], ColumnInfo)

    def test_property_rowcount(self):
        from google.cloud.spanner_dbapi import Connection, Cursor
        from google.cloud.spanner_dbapi.cursor import _UNSET_COUNT

        connection = Connection(self.INSTANCE, self.DATABASE)
        cursor = Cursor(connection)
        self.assertEqual(cursor.rowcount, _UNSET_COUNT)

    def test_callproc(self):
        from google.cloud.spanner_dbapi import Connection, Cursor
        from google.cloud.spanner_dbapi.exceptions import InterfaceError

        connection = Connection(self.INSTANCE, self.DATABASE)
        cursor = Cursor(connection)
        cursor._is_closed = True
        with self.assertRaises(InterfaceError):
            cursor.callproc(procname=None)

    def test_do_execute_update(self):
        from google.cloud.spanner_dbapi import Connection, Cursor
        from google.cloud.spanner_dbapi.cursor import _UNSET_COUNT

        connection = Connection(self.INSTANCE, self.DATABASE)
        cursor = Cursor(connection)
        transaction = mock.MagicMock()

        def run_helper(ret_value):
            transaction.execute_update.return_value = ret_value
            res = cursor._do_execute_update(
                transaction=transaction, sql="sql", params=None,
            )
            return res

        expected = "good"
        self.assertEqual(run_helper(expected), expected)
        self.assertEqual(cursor._row_count, _UNSET_COUNT)

        expected = 1234
        self.assertEqual(run_helper(expected), expected)
        self.assertEqual(cursor._row_count, expected)

    def test_execute_programming_error(self):
        from google.cloud.spanner_dbapi import Connection, Cursor
        from google.cloud.spanner_dbapi.exceptions import ProgrammingError

        connection = Connection(self.INSTANCE, self.DATABASE)
        cursor = Cursor(connection)
        cursor._connection = None
        with self.assertRaises(ProgrammingError):
            cursor.execute(sql="")

    def test_execute_attribute_error(self):
        from google.cloud.spanner_dbapi import Connection, Cursor

        connection = Connection(self.INSTANCE, self.DATABASE)
        cursor = Cursor(connection)

        with self.assertRaises(AttributeError):
            cursor.execute(sql="")

    def test_execute_statement(self):
        from google.cloud.spanner_dbapi import Connection, Cursor
        from google.cloud.spanner_dbapi import parse_utils

        connection = Connection(self.INSTANCE, mock.MagicMock())
        cursor = Cursor(connection)

        with mock.patch(
            "google.cloud.spanner_dbapi.parse_utils.classify_stmt",
            return_value=parse_utils.STMT_DDL,
        ) as mock_classify_stmt:
            sql = "sql"
            cursor.execute(sql=sql)
            mock_classify_stmt.assert_called_once_with(sql)
            self.assertEqual(cursor._connection.ddl_statements, [sql])

        with mock.patch(
            "google.cloud.spanner_dbapi.parse_utils.classify_stmt",
            return_value=parse_utils.STMT_NON_UPDATING,
        ):
            with mock.patch(
                "google.cloud.spanner_dbapi.cursor.Cursor._handle_DQL",
                return_value=parse_utils.STMT_NON_UPDATING,
            ) as mock_handle_ddl:
                cursor.execute(sql="sql")
                mock_handle_ddl.assert_called()

        with mock.patch(
            "google.cloud.spanner_dbapi.parse_utils.classify_stmt",
            return_value=parse_utils.STMT_INSERT,
        ):
            with mock.patch(
                "google.cloud.spanner_dbapi._helpers.handle_insert",
                return_value=parse_utils.STMT_INSERT,
            ) as mock_handle_insert:
                cursor.execute(sql="sql")
                mock_handle_insert.assert_called()

    def test_execute_integrity_error(self):
        from google.api_core import exceptions
        from google.cloud.spanner_dbapi import Connection, Cursor
        from google.cloud.spanner_dbapi.exceptions import IntegrityError

        connection = Connection(self.INSTANCE, mock.MagicMock())
        cursor = Cursor(connection)

        with mock.patch(
            "google.cloud.spanner_dbapi.parse_utils.classify_stmt",
            side_effect=exceptions.AlreadyExists("message"),
        ):
            with self.assertRaises(IntegrityError):
                cursor.execute(sql="sql")

        with mock.patch(
            "google.cloud.spanner_dbapi.parse_utils.classify_stmt",
            side_effect=exceptions.FailedPrecondition("message"),
        ):
            with self.assertRaises(IntegrityError):
                cursor.execute(sql="sql")

    def test_execute_invalid_argument(self):
        from google.api_core import exceptions
        from google.cloud.spanner_dbapi import Connection, Cursor
        from google.cloud.spanner_dbapi.exceptions import ProgrammingError

        connection = Connection(self.INSTANCE, mock.MagicMock())
        cursor = Cursor(connection)

        with mock.patch(
            "google.cloud.spanner_dbapi.parse_utils.classify_stmt",
            side_effect=exceptions.InvalidArgument("message"),
        ):
            with self.assertRaises(ProgrammingError):
                cursor.execute(sql="sql")

    def test_execute_internal_server_error(self):
        from google.api_core import exceptions
        from google.cloud.spanner_dbapi import Connection, Cursor
        from google.cloud.spanner_dbapi.exceptions import OperationalError

        connection = Connection(self.INSTANCE, mock.MagicMock())
        cursor = Cursor(connection)

        with mock.patch(
            "google.cloud.spanner_dbapi.parse_utils.classify_stmt",
            side_effect=exceptions.InternalServerError("message"),
        ):
            with self.assertRaises(OperationalError):
                cursor.execute(sql="sql")

    def test_fetchone(self):
        pass

    def test_fetchmany(self):
        pass

    def test_fetchall(self):
        pass

    def test_nextset(self):
        pass

    def test_setinputsizes(self):
        pass

    def test_setoutputsize(self):
        pass

    def test_handle_insert(self):
        pass

    def test_do_execute_insert_heterogenous(self):
        pass

    def test_do_execute_insert_homogenous(self):
        pass

    def test_handle_ddl(self):
        pass

    def test_context(self):
        pass

    def test_next(self):
        pass

    def test_iter(self):
        pass

    def test_list_tables(self):
        pass

    def test_run_sql_in_snapshot(self):
        pass

    def test_get_table_column_schema(self):
        pass

    def test_close(self):
        from google.cloud.spanner_dbapi import connect, InterfaceError

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

    def test_executemany_on_closed_cursor(self):
        from google.cloud.spanner_dbapi import connect, InterfaceError

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
        from google.cloud.spanner_dbapi import connect

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
