# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""DB-API Connection for the Google Cloud Spanner."""

from google.api_core.gapic_v1.client_info import ClientInfo
from google.cloud import spanner_v1 as spanner

from google.cloud.spanner_dbapi.cursor import Cursor
from google.cloud.spanner_dbapi.exceptions import InterfaceError
from google.cloud.spanner_dbapi.version import DEFAULT_USER_AGENT
from google.cloud.spanner_dbapi.version import PY_VERSION


class Connection(object):
    """DB-API Connection to a Google Cloud Spanner database.

    :type database: :class:`~google.cloud.spanner_v1.database.Database`
    :param database: The database to which the connection is linked.
    """

    def __init__(self, instance, database):
        self.instance = instance
        self.database = database
        self.is_closed = False

        self.ddl_statements = []

    def _raise_if_closed(self):
        """Helper to check the connection state before running a query.
        Raises an exception if this connection is closed.

        :raises: :class:`InterfaceError`: if this connection is closed.
        """
        if self.is_closed:
            raise InterfaceError("connection is already closed")

    def close(self):
        """Closes this connection.

        The connection will be unusable from this point forward.
        """
        self.database = None
        self.is_closed = True

    def commit(self):
        """Commits any pending transaction to the database."""
        self._raise_if_closed()

        self.run_prior_DDL_statements()

    def rollback(self):
        """A no-op, raising an error if the connection is closed."""
        self._raise_if_closed()

    def cursor(self):
        """Factory to create a DB-API Cursor."""
        self._raise_if_closed()

        return Cursor(self)

    def run_prior_DDL_statements(self):
        self._raise_if_closed()

        if self.ddl_statements:
            ddl_statements = self.ddl_statements
            self.ddl_statements = []

            return self.database.update_ddl(ddl_statements).result()

    def __enter__(self):
        return self

    def __exit__(self, etype, value, traceback):
        self.commit()
        self.close()


def connect(
    instance_id, database_id, project=None, credentials=None, user_agent=None
):
    """Creates a connection to a Google Cloud Spanner database.

    :type instance_id: str
    :param instance_id: ID of the instance to connect to.

    :type database_id: str
    :param database_id: The name of the database to connect to.

    :type project: str
    :param project: (Optional) The ID of the project which owns the
                    instances, tables and data. If not provided, will
                    attempt to determine from the environment.

    :type credentials: :class:`~google.auth.credentials.Credentials`
    :param credentials: (Optional) The authorization credentials to attach to
                        requests. These credentials identify this application
                        to the service. If none are specified, the client will
                        attempt to ascertain the credentials from the
                        environment.

    :type user_agent: str
    :param user_agent: (Optional) Prefix to the user agent header.

    :rtype: :class:`google.cloud.spanner_dbapi.connection.Connection`
    :returns: Connection object associated with the given Google Cloud Spanner
              resource.

    :raises: :class:`ValueError` in case of given instance/database
             doesn't exist.
    """

    client_info = ClientInfo(
        user_agent=user_agent or DEFAULT_USER_AGENT, python_version=PY_VERSION,
    )

    client = spanner.Client(
        project=project, credentials=credentials, client_info=client_info,
    )

    instance = client.instance(instance_id)
    if not instance.exists():
        raise ValueError("instance '%s' does not exist." % instance_id)

    database = instance.database(database_id, pool=spanner.pool.BurstyPool())
    if not database.exists():
        raise ValueError("database '%s' does not exist." % database_id)

    return Connection(instance, database)
