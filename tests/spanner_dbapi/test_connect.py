# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""connect() module function unit tests."""

import unittest
from unittest import mock


def _make_credentials():
    import google.auth.credentials

    class _CredentialsWithScopes(
        google.auth.credentials.Credentials, google.auth.credentials.Scoped
    ):
        pass

    return mock.Mock(spec=_CredentialsWithScopes)


class Testconnect(unittest.TestCase):
    def _callFUT(self, *args, **kw):
        from google.cloud.spanner_dbapi import connect

        return connect(*args, **kw)

    def test_connect(self):
        from google.api_core.gapic_v1.client_info import ClientInfo
        from google.cloud.spanner_dbapi.connection import Connection

        PROJECT = "test-project"
        USER_AGENT = "user-agent"
        CREDENTIALS = _make_credentials()
        CLIENT_INFO = ClientInfo(user_agent=USER_AGENT)

        with mock.patch("google.cloud.spanner_dbapi.spanner_v1.Client") as client_mock:
            with mock.patch(
                "google.cloud.spanner_dbapi.google_client_info",
                return_value=CLIENT_INFO,
            ) as client_info_mock:

                connection = self._callFUT(
                    "test-instance", "test-database", PROJECT, CREDENTIALS, USER_AGENT
                )

                self.assertIsInstance(connection, Connection)
                client_info_mock.assert_called_once_with(USER_AGENT)

            client_mock.assert_called_once_with(
                project=PROJECT, credentials=CREDENTIALS, client_info=CLIENT_INFO
            )

    def test_instance_not_found(self):
        from google.cloud.spanner_dbapi.exceptions import ProgrammingError

        with mock.patch(
            "google.cloud.spanner_v1.instance.Instance.exists", return_value=False
        ) as exists_mock:

            with self.assertRaises(ProgrammingError):
                self._callFUT("test-instance", "test-database")

            exists_mock.assert_called_once()

    def test_database_not_found(self):
        from google.cloud.spanner_dbapi.exceptions import ProgrammingError

        with mock.patch(
            "google.cloud.spanner_v1.instance.Instance.exists", return_value=True
        ):
            with mock.patch(
                "google.cloud.spanner_v1.database.Database.exists", return_value=False
            ) as exists_mock:

                with self.assertRaises(ProgrammingError):
                    self._callFUT("test-instance", "test-database")

                exists_mock.assert_called_once()

    def test_connect_instance_id(self):
        from google.cloud.spanner_dbapi.connection import Connection

        INSTANCE = "test-instance"

        with mock.patch(
            "google.cloud.spanner_v1.client.Client.instance"
        ) as instance_mock:
            connection = self._callFUT(INSTANCE, "test-database")

            instance_mock.assert_called_once_with(INSTANCE)

        self.assertIsInstance(connection, Connection)

    def test_connect_database_id(self):
        from google.cloud.spanner_dbapi.connection import Connection

        DATABASE = "test-database"

        with mock.patch(
            "google.cloud.spanner_v1.instance.Instance.database"
        ) as database_mock:
            with mock.patch(
                "google.cloud.spanner_v1.instance.Instance.exists", return_value=True
            ):
                connection = self._callFUT("test-instance", DATABASE)

                database_mock.assert_called_once_with(DATABASE, pool=mock.ANY)

        self.assertIsInstance(connection, Connection)


if __name__ == "__main__":
    unittest.main()
