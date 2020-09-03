# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

from collections import namedtuple
from enum import Enum
from functools import wraps
import time

from google.cloud import spanner_v1 as spanner

from .cursor import Cursor
from .exceptions import InterfaceError, Warning, ProgrammingError

ColumnDetails = namedtuple("column_details", ["null_ok", "spanner_type"])


class TransactionModes(Enum):
    READ_ONLY = "READ_ONLY"
    READ_WRITE = "READ_WRITE"


class AutocommitDMLModes(Enum):
    TRANSACTIONAL = "TRANSACTIONAL"
    PARTITIONED_NON_ATOMIC = "PARTITIONED_NON_ATOMIC"


def _connection_closed_check(func):
    """Raise an exception if attempting to use an already closed connection."""

    @wraps(func)
    def wrapped(self, *args, **kwargs):
        if self._is_closed:
            raise InterfaceError("connection is already closed")
        return func(self, *args, **kwargs)

    return wrapped


class Connection(object):
    """This is a wrap-around object for the existing `Database` and the
    corresponding `Instance` objects.

    :type database: :class:`~google.cloud.spanner_v1.database.Database`
    :param database: Corresponding Database.

    :type instance: :class:`~google.cloud.spanner_v1.instance.Instance`
    :param instance: The instance that owns the database.
    """

    def __init__(self, database, instance):
        self.database = database
        self.instance = instance
        self.autocommit = True
        self.read_only = False
        self.transaction_mode = (
            TransactionModes.READ_ONLY
            if self.read_only
            else TransactionModes.READ_WRITE
        )
        self.autocommit_dml_mode = AutocommitDMLModes.TRANSACTIONAL
        self.timeout_secs = 0
        self.read_timestamp = None
        self.commit_timestamp = None
        self._is_closed = False
        self._inside_transaction = not self.autocommit
        self._transaction_started = False
        self._ddl_statements = []
        self.read_only_staleness = {}

    @property
    def is_closed(self):
        return self._is_closed

    @property
    def inside_transaction(self):
        return self._inside_transaction

    @property
    def transaction_started(self):
        return self._transaction_started

    def _change_transaction_started(self, val: bool):
        if self._inside_transaction:
            self._transaction_started = val

    @_connection_closed_check
    def snapshot(self):
        return self.database.snapshot()

    @_connection_closed_check
    def run_in_transaction(self, fn, *args, **kwargs):
        return self.database.run_in_transaction(fn, *args, **kwargs)

    @_connection_closed_check
    def append_ddl_statement(self, ddl_statement):
        self._change_transaction_started(True)

        self._ddl_statements.append(ddl_statement)

        if self.autocommit:
            self.commit()

    @_connection_closed_check
    def _run_prior_ddl_statements(self):
        """Run the list of Data Definition Language (DDL) statements on the
        underlying database. Each DDL statement MUST NOT contain a semicolon.

        :rtype: :class:`google.api_core.operation.Operation`
        :returns: an operation instance
        """
        # Synchronously wait on the operation's completion.
        if self.read_only:
            self._ddl_statements = []
            raise ProgrammingError("Connection is in 'read_only' mode")

        if not self._ddl_statements:
            return

        ddl_statements = self._ddl_statements
        self._ddl_statements = []

        return self.database.update_ddl(ddl_statements).result()

    @_connection_closed_check
    def list_tables(self):
        return self.run_sql_in_snapshot(
            """SELECT
                t.table_name
            FROM
                information_schema.tables AS t
            WHERE
                t.table_catalog = '' and t.table_schema = ''"""
        )

    @_connection_closed_check
    def run_sql_in_snapshot(self, sql, params=None, param_types=None):
        # Some SQL e.g. for INFORMATION_SCHEMA cannot be run in
        # read-write transactions hence this method exists to circumvent that
        # limit.
        self._run_prior_ddl_statements()

        with self.database.snapshot() as snapshot:
            res = snapshot.execute_sql(
                sql, params=params, param_types=param_types
            )
            return list(res)

    @_connection_closed_check
    def get_table_column_schema(self, table_name):
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
        """Closing database connection"""
        self.rollback()
        self._is_closed = True

    @_connection_closed_check
    def cursor(self):
        """Returns cursor for current database"""
        return Cursor(self)

    @_connection_closed_check
    def rollback(self):
        """Roll back a transaction"""
        self._ddl_statements = []
        self._change_transaction_started(False)

    @_connection_closed_check
    def commit(self):
        """Commit mutations to the database."""
        if self.autocommit:
            raise Warning(
                "This connection is in autocommit mode - manual committing is off."
            )

        self._run_prior_ddl_statements()
        if self.transaction_mode == TransactionModes.READ_WRITE:
            self.commit_timestamp = time.time()

        self._change_transaction_started(False)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value:
            self.rollback()
        elif not self.autocommit:
            self.commit()
        self.close()
