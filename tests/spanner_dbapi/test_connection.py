# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""Cloud Spanner DB-API Connection class unit tests."""

import unittest
from unittest import mock


def _make_credentials():
    from google.auth import credentials

    class _CredentialsWithScopes(credentials.Credentials, credentials.Scoped):
        pass

    return mock.Mock(spec=_CredentialsWithScopes)


class TestConnection(unittest.TestCase):

    PROJECT = "test-project"
    INSTANCE = "test-instance"
    DATABASE = "test-database"
    USER_AGENT = "user-agent"
    CREDENTIALS = _make_credentials()

    def _get_client_info(self):
        from google.api_core.gapic_v1.client_info import ClientInfo

        return ClientInfo(user_agent=self.USER_AGENT)

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

        self.assertFalse(connection.is_closed)
        connection.close()
        self.assertTrue(connection.is_closed)

        with self.assertRaises(InterfaceError):
            connection.cursor()

    def test_commit(self):
        from google.cloud.spanner_dbapi import Connection, InterfaceError

        connection = Connection(self.INSTANCE, self.DATABASE)

        with mock.patch(
            "google.cloud.spanner_dbapi.connection.Connection.run_prior_DDL_statements"
        ) as run_ddl_mock:
            connection.commit()
            run_ddl_mock.assert_called_once_with()

        connection.is_closed = True

        with self.assertRaises(InterfaceError):
            connection.commit()

    def test_rollback(self):
        from google.cloud.spanner_dbapi import Connection

        connection = Connection(self.INSTANCE, self.DATABASE)

        with mock.patch(
            "google.cloud.spanner_dbapi.connection.Connection._raise_if_closed"
        ) as check_closed_mock:
            connection.rollback()
            check_closed_mock.assert_called_once_with()

    def test_run_prior_DDL_statements(self):
        from google.cloud.spanner_dbapi import Connection, InterfaceError

        with mock.patch(
            "google.cloud.spanner_v1.database.Database", autospec=True,
        ) as mock_database:
            connection = Connection(self.INSTANCE, mock_database)

            connection.run_prior_DDL_statements()
            mock_database.update_ddl.assert_not_called()

            ddl = ["ddl"]
            connection.ddl_statements = ddl

            connection.run_prior_DDL_statements()
            mock_database.update_ddl.assert_called_once_with(ddl)

            connection.is_closed = True

            with self.assertRaises(InterfaceError):
                connection.run_prior_DDL_statements()

    def test_context(self):
        from google.cloud.spanner_dbapi import Connection

        connection = Connection(self.INSTANCE, self.DATABASE)
        with connection as conn:
            self.assertEqual(conn, connection)

        self.assertTrue(connection.is_closed)

    def test_connect(self):
        from google.cloud.spanner_dbapi import Connection, connect

        with mock.patch("google.cloud.spanner_v1.Client"):
            with mock.patch(
                "google.api_core.gapic_v1.client_info.ClientInfo",
                return_value=self._get_client_info(),
            ):
                connection = connect(
                    self.INSTANCE,
                    self.DATABASE,
                    self.PROJECT,
                    self.CREDENTIALS,
                    self.USER_AGENT,
                )
                self.assertIsInstance(connection, Connection)

    def test_connect_instance_not_found(self):
        from google.cloud.spanner_dbapi import connect

        with mock.patch(
            "google.cloud.spanner_v1.instance.Instance.exists",
            return_value=False,
        ):
            with self.assertRaises(ValueError):
                connect("test-instance", "test-database")

    def test_connect_database_not_found(self):
        from google.cloud.spanner_dbapi import connect

        with mock.patch(
            "google.cloud.spanner_v1.database.Database.exists",
            return_value=False,
        ):
            with mock.patch(
                "google.cloud.spanner_v1.instance.Instance.exists",
                return_value=True,
            ):
                with self.assertRaises(ValueError):
                    connect("test-instance", "test-database")
