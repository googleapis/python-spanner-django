# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""Connection() class unit tests."""

import unittest
from unittest import mock

# import google.cloud.spanner_dbapi.exceptions as dbapi_exceptions

from google.api_core.exceptions import Aborted
from google.cloud.spanner_dbapi import Connection, InterfaceError
from google.cloud.spanner_dbapi.checksum import ResultsChecksum
from google.cloud.spanner_dbapi.connection import AUTOCOMMIT_MODE_WARNING
from google.cloud.spanner_v1.database import Database
from google.cloud.spanner_v1.instance import Instance


class TestConnection(unittest.TestCase):
    instance_name = "instance-name"
    database_name = "database-name"

    def _make_connection(self):
        # we don't need real Client object to test the constructor
        instance = Instance(self.instance_name, client=None)
        database = instance.database(self.database_name)
        return Connection(instance, database)

    def test_ctor(self):
        connection = self._make_connection()

        self.assertIsInstance(connection.instance, Instance)
        self.assertEqual(connection.instance.instance_id, self.instance_name)

        self.assertIsInstance(connection.database, Database)
        self.assertEqual(connection.database.database_id, self.database_name)

        self.assertFalse(connection.is_closed)

    def test_close(self):
        connection = self._make_connection()

        self.assertFalse(connection.is_closed)
        connection.close()
        self.assertTrue(connection.is_closed)

        with self.assertRaises(InterfaceError):
            connection.cursor()

    @mock.patch("warnings.warn")
    def test_transaction_autocommit_warnings(self, warn_mock):
        connection = self._make_connection()
        connection.autocommit = True

        connection.commit()
        warn_mock.assert_called_with(
            AUTOCOMMIT_MODE_WARNING, UserWarning, stacklevel=2
        )
        connection.rollback()
        warn_mock.assert_called_with(
            AUTOCOMMIT_MODE_WARNING, UserWarning, stacklevel=2
        )

    def test_database_property(self):
        connection = self._make_connection()
        self.assertIsInstance(connection.database, Database)
        self.assertEqual(connection.database, connection._database)

        with self.assertRaises(AttributeError):
            connection.database = None

    def test_instance_property(self):
        connection = self._make_connection()
        self.assertIsInstance(connection.instance, Instance)
        self.assertEqual(connection.instance, connection._instance)

        with self.assertRaises(AttributeError):
            connection.instance = None

    def test_run_statement(self):
        """Check that Connection remembers executed statements."""
        sql = """SELECT 23 FROM table WHERE id = @a1"""
        params = {"a1": "value"}
        param_types = {"a1": str}

        connection = self._make_connection()

        statement = {
            "sql": sql,
            "params": params,
            "param_types": param_types,
            "checksum": ResultsChecksum(),
        }

        with mock.patch(
            "google.cloud.spanner_dbapi.connection.Connection.transaction_checkout"
        ):
            connection.run_statement(statement)

        self.assertEqual(connection._statements[0]["sql"], sql)
        self.assertEqual(connection._statements[0]["params"], params)
        self.assertEqual(connection._statements[0]["param_types"], param_types)
        self.assertIsInstance(
            connection._statements[0]["checksum"], ResultsChecksum
        )

    def test_clear_statements_on_commit(self):
        """
        Check that all the saved statements are
        cleared, when the transaction is commited.
        """
        connection = self._make_connection()
        connection._transaction = mock.Mock()
        connection._statements = [{}, {}]

        self.assertEqual(len(connection._statements), 2)

        with mock.patch(
            "google.cloud.spanner_v1.transaction.Transaction.commit"
        ):
            connection.commit()

        self.assertEqual(len(connection._statements), 0)

    def test_clear_statements_on_rollback(self):
        """
        Check that all the saved statements are
        cleared, when the transaction is roll backed.
        """
        connection = self._make_connection()
        connection._transaction = mock.Mock()
        connection._statements = [{}, {}]

        self.assertEqual(len(connection._statements), 2)

        with mock.patch(
            "google.cloud.spanner_v1.transaction.Transaction.commit"
        ):
            connection.rollback()

        self.assertEqual(len(connection._statements), 0)

    def test_retry_transaction(self):
        """Check retrying an aborted transaction."""
        row = ["field1", "field2"]
        connection = self._make_connection()

        checksum = ResultsChecksum()
        checksum.consume_result(row)
        retried_checkum = ResultsChecksum()

        statement = {
            "sql": "SELECT 1",
            "params": [],
            "param_types": {},
            "checksum": checksum,
        }
        connection._statements.append(statement)

        with mock.patch(
            "google.cloud.spanner_dbapi.connection.Connection.run_statement",
            return_value=([row], retried_checkum),
        ) as run_mock:
            with mock.patch(
                "google.cloud.spanner_dbapi.connection._compare_checksums"
            ) as compare_mock:
                connection.retry_transaction()

                compare_mock.assert_called_with(checksum, retried_checkum)

            run_mock.assert_called_with(statement, retried=True)

    def test_retry_transaction_checksum_mismatch(self):
        """
        Check retrying an aborted transaction
        with results checksums mismatch.
        """
        row = ["field1", "field2"]
        retried_row = ["field3", "field4"]
        connection = self._make_connection()

        checksum = ResultsChecksum()
        checksum.consume_result(row)
        retried_checkum = ResultsChecksum()

        statement = {
            "sql": "SELECT 1",
            "params": [],
            "param_types": {},
            "checksum": checksum,
        }
        connection._statements.append(statement)

        with mock.patch(
            "google.cloud.spanner_dbapi.connection.Connection.run_statement",
            return_value=([retried_row], retried_checkum),
        ):
            with self.assertRaises(Aborted):
                connection.retry_transaction()
