# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""Connection() class unit tests."""

import unittest

# import google.cloud.spanner_dbapi.exceptions as dbapi_exceptions

from google.cloud.spanner_dbapi import Connection, InterfaceError, Warning
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

    def test_transaction_management_warnings(self):
        connection = self._make_connection()

        with self.assertRaises(Warning):
            connection.commit()

        with self.assertRaises(Warning):
            connection.rollback()
