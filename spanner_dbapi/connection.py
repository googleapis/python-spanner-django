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
from .exceptions import InterfaceError, Warning

ColumnDetails = namedtuple("column_details", ["null_ok", "spanner_type"])


class TransactionModes(Enum):
    read_only = "READ_ONLY"
    read_write = "READ_WRITE"


class AutocommitDMLModes(Enum):
    transactional = "TRANSACTIONAL"
    partitioned_non_atomic = "PARTITIONED_NON_ATOMIC"


def _is_conn_closed_check(func):
    """
    Raise an exception if attempting to use an already closed connection.
    """

    @wraps(func)
    def wrapped(self, *args, **kwargs):
        if self.__is_closed:
            raise InterfaceError("connection is already closed")
        return func(self, *args, **kwargs)

    return wrapped


class Connection(object):
    """This is a wrap-around object for the existing `Database` and the
    corresponding `Instance` objects.

    :type database: :class:`~google.cloud.spanner_v1.database.Database`
    :param database: Corresponding Database

    :type instance: :class:`~google.cloud.spanner_v1.instance.Instance`
    :param instance: The instance that owns the database.

    :type autocommit: bool
    :param autocommit: (Optional) When changed to True, all the pending
                       transactions must be committed.

    :type read_only: bool
    :param read_only: (Optional) Indicates if the Connection is intended to be
                      used for read-only transactions.
    """

    def __init__(self, database, instance, autocommit=True, read_only=False):
        self.database = database
        self.instance = instance
        self.autocommit = autocommit
        self.read_only = read_only
        self.transaction_mode = (
            TransactionModes.read_only
            if self.read_only
            else TransactionModes.read_write
        )
        self.autocommit_dml_mode = AutocommitDMLModes.transactional
        self.timeout_secs = 0
        self.read_timestamp = None
        self.commit_timestamp = None
        self.__is_closed = False
        self.__inside_transaction = not autocommit
        self.__transaction_started = False
        self.__ddl_statements = []
        self.read_only_staleness = {}

    @property
    def is_closed(self):
        return self.__is_closed

    @property
    def inside_transaction(self):
        return self.__inside_transaction

    @property
    def transaction_started(self):
        return self.__transaction_started

    @property
    def _ddl_statements(self):
        return self.__ddl_statements

    @_ddl_statements.setter
    def _ddl_statements(self, dll):
        self._change_transaction_started(True)

        self.__ddl_statements = dll
        if self.autocommit:
            self.commit()

    def _change_transaction_started(self, val: bool):
        if self.__inside_transaction:
            self.__transaction_started = val

    @_is_conn_closed_check
    def __handle_update_ddl(self, ddl_statements):
        """
        Run the list of Data Definition Language (DDL) statements on the
        underlying database. Each DDL statement MUST NOT contain a semicolon.
        Args:
            ddl_statements: a list of DDL statements, each without a semicolon.
        Returns:
            google.api_core.operation.Operation.result()
        """
        # Synchronously wait on the operation's completion.
        return self.database.update_ddl(ddl_statements).result()

    @_is_conn_closed_check
    def read_snapshot(self):
        return self.database.snapshot()

    @_is_conn_closed_check
    def in_transaction(self, fn, *args, **kwargs):
        return self.database.run_in_transaction(fn, *args, **kwargs)

    @_is_conn_closed_check
    def append_ddl_statement(self, ddl_statement):
        self.__ddl_statements.append(ddl_statement)

    @_is_conn_closed_check
    def run_prior_ddl_statements(self):
        if self.read_only:
            self.__ddl_statements = []
            raise Warning("Connection is in 'read_only' mode")

        if not self.__ddl_statements:
            return

        ddl_statements = self.__ddl_statements
        self.__ddl_statements = []

        return self.__handle_update_ddl(ddl_statements)

    def list_tables(self):
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
        # Some SQL e.g. for INFORMATION_SCHEMA cannot be run in
        # read-write transactions hence this method exists to circumvent that
        # limit.
        self.run_prior_ddl_statements()

        with self.database.snapshot() as snapshot:
            res = snapshot.execute_sql(
                sql, params=params, param_types=param_types
            )
            return list(res)

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
        """
        Closing database connection
        """
        self.rollback()
        self.__is_closed = True

    @_is_conn_closed_check
    def cursor(self):
        return Cursor(self)

    @_is_conn_closed_check
    def rollback(self):
        self.__ddl_statements = []
        self._change_transaction_started(False)

    @_is_conn_closed_check
    def commit(self):
        if self.autocommit:
            raise Warning("'autocommit' is set to 'True'")

        self.run_prior_ddl_statements()
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
