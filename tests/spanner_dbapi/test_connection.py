# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""Connection() class unit tests."""

import unittest
from unittest import mock


def _make_credentials():
    from google.auth import credentials

    class _CredentialsWithScopes(credentials.Credentials, credentials.Scoped):
        pass

    return mock.Mock(spec=_CredentialsWithScopes)


class TestConnection(unittest.TestCase):

    PROJECT = "test-project"
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

    def test_db_connect(self):
        from google.cloud.spanner_dbapi import Connection, connect

        with mock.patch("google.cloud.spanner_v1.Client"):
            with mock.patch(
                # "google.cloud.spanner_dbapi.version.google_client_info",
                "google.api_core.gapic_v1.client_info.ClientInfo",
                return_value=self._get_client_info(),
            ):
                connection = connect(
                    "test-instance",
                    "test-database",
                    self.PROJECT,
                    self.CREDENTIALS,
                    self.USER_AGENT,
                )
                self.assertIsInstance(connection, Connection)

    def test_instance_not_found(self):
        from google.cloud.spanner_dbapi import connect

        with mock.patch(
            "google.cloud.spanner_v1.instance.Instance.exists",
            return_value=False,
        ):
            with self.assertRaises(ValueError):
                connect("test-instance", "test-database")

    def test_database_not_found(self):
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
