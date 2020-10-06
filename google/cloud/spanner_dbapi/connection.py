# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

from collections import namedtuple

from google.cloud import spanner_v1 as spanner

from .cursor import Cursor
from .exceptions import InterfaceError

ColumnDetails = namedtuple("column_details", ["null_ok", "spanner_type"])


class Connection:
    """
    A wrap-around object for the existing
    :class:`~google.cloud.spanner_v1.database.Database` and the corresponding
    :class:`~google.cloud.spanner_admin_instance_v1.types.Instance` objects.

    :type db_handle: :class:`Database`
    :param db_handle: Database handle.
    """

    def __init__(self, db_handle):
        self._dbhandle = db_handle
        self._ddl_statements = []

        self.is_closed = False

    def cursor(self):
        """Factory to create a :class:`Cursor` linked to this Connection.

        :rtype: :class:`Cursor`
        :returns: A database cursor, which is used to manage the context of a
                  fetch operation.
        """
        self._raise_if_closed()

        return Cursor(self)

    def _raise_if_closed(self):
        """Raise an exception if this connection is closed.

        Helper to check the connection state before
        running a SQL/DDL/DML query.

        :raises: :class:`InterfaceError` if this connection is closed.
        """
        if self.is_closed:
            raise InterfaceError("connection is already closed")

    def __handle_update_ddl(self, ddl_statements):
        """
        Run the list of Data Definition Language (DDL) statements on the underlying
        database. Each DDL statement MUST NOT contain a semicolon.

        :type ddl_statements: list
        :param ddl_statements: A list of DDL statements, each without a
                               semicolon.
        """
        self._raise_if_closed()
        # Synchronously wait on the operation's completion.
        return self._dbhandle.update_ddl(ddl_statements).result()

    def read_snapshot(self):
        """Return a Snapshot of the linked Database.

        :rtype: :class:`~google.cloud.spanner_v1.snapshot.Snapshot`
        :returns: A snapshot of the linked Database.
        """
        self._raise_if_closed()
        return self._dbhandle.snapshot()

    def in_transaction(self, fn, *args, **kwargs):
        """Perform a unit of work in a linked Transaction, retrying on abort.

        :type fn: callable
        :param fn: takes a required positional argument, the transaction,
                   and additional positional / keyword arguments as supplied
                   by the caller.

        :type *args: tuple
        :param *args: additional positional arguments to be passed to ``fn``.

        :type **kwargs: dict
        :param **kwargs: (Optional) keyword arguments to be passed to ``fn``.
                         If passed, "timeout_secs" will be removed and used to
                         override the default retry timeout which defines
                         maximum timestamp to continue retrying the transaction.

        :rtype: Any
        :returns: Runs the given function as it would be a transaction.
        """
        self._raise_if_closed()
        return self._dbhandle.run_in_transaction(fn, *args, **kwargs)

    def append_ddl_statement(self, ddl_statement):
        """Append DDL statement to the existing list of DDL statements in
        linked database.

        :type ddl_statements: list
        :param ddl_statements: A list of DDL statements, each without a
                               semicolon.
        """
        self._raise_if_closed()
        self._ddl_statements.append(ddl_statement)

    def run_prior_DDL_statements(self):
        """Run prior Operation.

        :rtype: str
        :returns: Updated statements.
        """
        self._raise_if_closed()

        if not self._ddl_statements:
            return

        ddl_statements = self._ddl_statements
        self._ddl_statements = []

        return self.__handle_update_ddl(ddl_statements)

    def list_tables(self):
        """List tables contained within the linked Database.

        :rtype: list
        :returns: Tables with corresponding information.
        """
        return self.run_sql_in_snapshot(
            """
            SELECT
              t.table_name
            FROM
              information_schema.tables AS t
            WHERE
              t.table_catalog = '' and t.table_schema = ''
            """
        )

    def run_sql_in_snapshot(self, sql, params=None, param_types=None):
        """Run an SQL request on the linked Database snapshot.

        :type sql: str
        :param sql: SQL request.

        :type params: list
        :param params: (Optional) List of parameters.

        :type param_types: dict
        :param param_types: (Optional) List of parameters' types.

        :rtype: list
        :returns: A list of :class:`~google.cloud.spanner_v1.streamed.StreamedResultSet`
                  results.
        """
        # Some SQL e.g. for INFORMATION_SCHEMA cannot be run in read-write transactions
        # hence this method exists to circumvent that limit.
        self.run_prior_DDL_statements()

        with self._dbhandle.snapshot() as snapshot:
            res = snapshot.execute_sql(
                sql, params=params, param_types=param_types
            )
            return list(res)

    def get_table_column_schema(self, table_name):
        """Get table column schema.

        :type table_name: str
        :param table_name: Name of the table.

        :rtype: dict
        :returns: Column description.
        """
        rows = self.run_sql_in_snapshot(
            """SELECT
                COLUMN_NAME, IS_NULLABLE, SPANNER_TYPE
            FROM
                INFORMATION_SCHEMA.COLUMNS
            WHERE
                TABLE_SCHEMA = ''
            AND
                TABLE_NAME = @table_name""",
            params={"table_name": table_name},
            param_types={"table_name": spanner.param_types.STRING},
        )

        column_details = {}
        for column_name, is_nullable, spanner_type in rows:
            column_details[column_name] = ColumnDetails(
                null_ok=is_nullable == "YES", spanner_type=spanner_type
            )
        return column_details

    def close(self):
        """Close this connection.

        .. note:: The connection will be unusable from this point forward.
        """
        self.rollback()
        self.__dbhandle = None
        self.is_closed = True

    def commit(self):
        """Commit all the pending transactions."""
        self._raise_if_closed()

        self.run_prior_DDL_statements()

    def rollback(self):
        self._raise_if_closed()

        # TODO: to be added.

    def __enter__(self):
        return self

    def __exit__(self, etype, value, traceback):
        self.commit()
        self.close()
