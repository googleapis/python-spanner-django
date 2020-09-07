# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

from collections import namedtuple
from functools import wraps

from .cursor import Cursor
from .exceptions import InterfaceError, Warning
from .enums import AutocommitDMLModes, TransactionModes

ColumnDetails = namedtuple("column_details", ["null_ok", "spanner_type"])


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

    def close(self):
        """Closing database connection"""
        self._is_closed = True

    @_connection_closed_check
    def cursor(self):
        """Returns cursor for current database"""
        return Cursor(self)

    @_connection_closed_check
    def rollback(self):
        """Roll back a transaction"""
        raise Warning(
            "Connection always works in `autocommit` mode, because of Spanner's limitations."
        )

    @_connection_closed_check
    def commit(self):
        """Commit mutations to the database."""
        raise Warning(
            "Connection always works in `autocommit` mode, because of Spanner's limitations."
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
