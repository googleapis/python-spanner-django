# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""Connection() class unit tests."""

import unittest
from unittest import mock

# import google.cloud.spanner_dbapi.exceptions as dbapi_exceptions
from google.cloud.spanner_v1.transaction import Transaction

from google.cloud.spanner_dbapi import Connection, InterfaceError
from google.cloud.spanner_dbapi.connection import AUTOCOMMIT_MODE_WARNING
from google.cloud.spanner_v1.database import Database
from google.cloud.spanner_v1.instance import Instance
from google.cloud.spanner_v1.database import SnapshotCheckout


class TestConnection(unittest.TestCase):
    instance_name = "instance-name"
    database_name = "database-name"
    ddl_statements = ["ALTER TABLE TestTable ADD COLUMN Column STRING(1024)"]

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

    def test_read_snapshot(self):
        connection = self._make_connection()

        self.assertIsInstance(connection.read_snapshot(), SnapshotCheckout)
    #     TODO check smth

    def test_in_transaction(self):
        import datetime
        from google.cloud.spanner_v1.proto.spanner_pb2 import CommitResponse
        from google.cloud.spanner_v1.proto.transaction_pb2 import (
            Transaction as TransactionPB,
            TransactionOptions,
        )
        from google.cloud._helpers import UTC
        from google.cloud._helpers import _datetime_to_pb_timestamp

        connection = self._make_connection()

        TABLE_NAME = "citizens"
        COLUMNS = ["email", "first_name", "last_name", "age"]
        VALUES = [
            ["phred@exammple.com", "Phred", "Phlyntstone", 32],
            ["bharney@example.com", "Bharney", "Rhubble", 31],
        ]

        TRANSACTION_ID = b"FACEDACE"
        transaction_pb = TransactionPB(id=TRANSACTION_ID)
        now = datetime.datetime.utcnow().replace(tzinfo=UTC)
        now_pb = _datetime_to_pb_timestamp(now)
        response = CommitResponse(commit_timestamp=now_pb)
        # gax_api = self._make_spanner_api()
        # gax_api.begin_transaction.return_value = transaction_pb
        # gax_api.commit.return_value = response
        # database = self._make_database()
        # database.spanner_api = gax_api
        # session = self._make_one(database)
        # session._session_id = self.SESSION_ID

        called_with = []
        def unit_of_work(txn, *args, **kw):
            called_with.append((txn, args, kw))
            txn.insert(TABLE_NAME, COLUMNS, VALUES)
            return 42

        return_value = connection.in_transaction(unit_of_work, "abc", some_arg="def")

        # txn, args, kw = called_with[0]
        # self.assertIsInstance(txn, Transaction)
        # self.assertEqual(return_value, 42)
        # self.assertEqual(args, ("abc",))
        # self.assertEqual(kw, {"some_arg": "def"})


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
