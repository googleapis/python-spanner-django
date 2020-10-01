# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""Connection() class unit tests."""

import unittest
from unittest import mock


class TestConnection(unittest.TestCase):
    def setUp(self):
        from google.cloud.spanner_dbapi.connection import Connection

        with mock.patch(
            "google.cloud.spanner_v1.database.Database"
        ) as database_mock:
            with mock.patch(
                "google.cloud.spanner_v1.instance.Instance"
            ) as instance_mock:
                self.connection = Connection(database_mock, instance_mock)

    def test_connection_close_check(self):
        from google.cloud.spanner_dbapi.exceptions import InterfaceError

        self.connection.close()
        with self.assertRaises(InterfaceError):
            self.connection.cursor()
        self.assertTrue(self.connection._is_closed)

    def test_connection_close_check_if_open(self):
        self.connection.cursor()
        self.assertFalse(self.connection._is_closed)

    def test_is_closed(self):
        self.assertEqual(self.connection._is_closed, self.connection.is_closed)
        self.connection.close()
        self.assertEqual(self.connection._is_closed, self.connection.is_closed)

    def test_inside_transaction(self):
        self.assertEqual(
            self.connection._inside_transaction,
            self.connection.inside_transaction,
        )

    def test_transaction_started(self):
        self.assertEqual(
            self.connection.transaction_started,
            self.connection._transaction_started,
        )

    def test_change_transaction_started(self):
        self.connection._change_transaction_started(True)
        self.assertFalse(self.connection._transaction_started)
        self.connection._inside_transaction = True
        self.connection._change_transaction_started(True)
        self.assertTrue(self.connection._transaction_started)

    def test_cursor(self):
        from google.cloud.spanner_dbapi.cursor import Cursor

        cursor = self.connection.cursor()
        self.assertIsInstance(cursor, Cursor)
        self.assertEqual(self.connection, cursor._connection)

    def test_commit(self):
        from google.cloud.spanner_dbapi.exceptions import Warning

        with self.assertRaises(Warning):
            self.connection.commit()

    def test_rollback(self):
        from google.cloud.spanner_dbapi.exceptions import Warning

        with self.assertRaises(Warning):
            self.connection.rollback()

    def test_context_success(self):
        with self.connection as conn:
            conn.cursor()
        self.assertTrue(self.connection._is_closed)

    def test_context_error(self):
        with self.assertRaises(Exception):
            with self.connection:
                raise Exception
        self.assertTrue(self.connection._is_closed)
