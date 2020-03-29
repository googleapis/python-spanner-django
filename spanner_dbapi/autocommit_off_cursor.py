# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

import time

import google.api_core.exceptions as grpc_exceptions
from google.cloud.spanner_v1 import param_types

from .base_cursor import BaseCursor
from .exceptions import (
    IntegrityError, InternalError, OperationalError, ProgrammingError,
)
from .parse_utils import (
    STMT_DDL, STMT_INSERT, STMT_NON_UPDATING, classify_stmt,
    ensure_where_clause, get_param_types, parse_insert,
    sql_pyformat_args_to_spanner,
)
from .utils import PeekIterator

_UNSET_COUNT = -1


# This table maps spanner_types to Spanner's data type sizes as per
#   https://cloud.google.com/spanner/docs/data-types#allowable-types
# It is used to map `display_size` to a known type for Cursor.description
# after a row fetch.
# Since ResultMetadata
#   https://cloud.google.com/spanner/docs/reference/rest/v1/ResultSetMetadata
# does not send back the actual size, we have to lookup the respective size.
# Some fields' sizes are dependent upon the dynamic data hence aren't sent back
# by Cloud Spanner.
code_to_display_size = {
    param_types.BOOL.code: 1,
    param_types.DATE.code: 4,
    param_types.FLOAT64.code: 8,
    param_types.INT64.code: 8,
    param_types.TIMESTAMP.code: 12,
}


class Cursor(BaseCursor):
    def __init__(self, connection):
        super(Cursor, self).__init__(connection)
        self.__sql_in_same_txn = []

    def close(self):
        self.__clear()
        self._closed = True

    def __discard_aborted_txn(self):
        return self._connection.discard_aborted_txn()

    def __get_txn(self):
        return self._connection.get_txn()

    def execute(self, sql, args=None, already_in_retry=False):
        """
        Abstracts and implements execute SQL statements on Cloud Spanner.
        If it encounters grpc_exceptions.Aborted error, it optimistically retries
        the execution a maximum of 2 times, thus a total of 3 times.

        Args:
            sql: A SQL statement
            *args: variadic argument list
            **kwargs: key worded arguments

        Returns:
            None
        """
        self._raise_if_already_closed()

        if not self._connection:
            raise ProgrammingError('Cursor is not connected to the database')

        self._res = None

        # Classify whether this is a read-only SQL statement.
        try:
            classification = classify_stmt(sql)
            if classification == STMT_DDL:
                self._connection.append_ddl_statement(sql)
                return

            # For every other operation, we've got to ensure that
            # any prior DDL statements were run.
            self._run_prior_DDL_statements()

            if classification == STMT_NON_UPDATING:
                self.__handle_DQL(self.__get_txn(), sql, args or None)
            elif classification == STMT_INSERT:
                self.__handle_insert(self.__get_txn(), sql, args or None)
            else:
                self.__handle_update(self.__get_txn(), sql, args or None)

        except grpc_exceptions.InvalidArgument as e:  # We can't retry a syntax issue, fail fast.
            self.__discard_aborted_txn()
            raise ProgrammingError(e.details if hasattr(e, 'details') else e)

        except (grpc_exceptions.AlreadyExists, grpc_exceptions.FailedPrecondition) as e:
            # We can't retry an integrity error within the same transaction regardless.
            self.__discard_aborted_txn()
            raise IntegrityError(e.details if hasattr(e, 'details') else e)

        except Exception as e:
            # Firstly discard the aborted transaction.
            self.__discard_aborted_txn()

            if already_in_retry:  # It is already being retried, so return immediately.
                raise e

            # Attempt to replay all the prior sql within the same transaction.
            sql_args_tuples = self.__sql_in_same_txn[:]
            sql_args_tuples.append((sql, args,))

            return self.__replay_all_prior_statements_in_transaction(sql_args_tuples)
        else:  # No error here
            self.__sql_in_same_txn.append((sql, args,))

    def _clear_transaction_state(self):
        """
        Invoked on every Connection.commit() or Connection.rollback()
        """
        if self.__sql_in_same_txn:
            self.__sql_in_same_txn.clear()

    def __replay_all_prior_statements_in_transaction(self, sql_args_tuples):
        if not sql_args_tuples:
            return

        lastException = None

        for i in range(5):
            # Clean up before attempting the replay.
            self.__sql_in_same_txn.clear()

            print("\033[31mAttempting transaction replay #%d with elements:\n%s\033[00m" % (i, sql_args_tuples))

            for sql, args in sql_args_tuples:
                try:
                    self.execute(sql, args, already_in_retry=True)
                except grpc_exceptions.InvalidArgument as e:  # We can't retry a syntax issue, fail fast.
                    raise ProgrammingError(e.details if hasattr(e, 'details') else e)
                except (grpc_exceptions.AlreadyExists, grpc_exceptions.FailedPrecondition) as e:
                    raise IntegrityError(e.details if hasattr(e, 'details') else e)
                except Exception as e:
                    lastException = e
                    # TODO: Use exponential backoff with jitter, before retrying.
                    time.sleep(0.57)
                    break
            else:
                # All the elements in sql_args_tuples were executed,
                # thus we can now break out of the retry loop.
                # But first, reset all the executed (sql, args) for future replay.
                self.__sql_in_same_txn = sql_args_tuples[:]
                break

        try:
            if lastException:
                self.__discard_aborted_txn()
                raise lastException
        except grpc_exceptions.InvalidArgument as e:
            raise ProgrammingError(e.details if hasattr(e, 'details') else e)
        except grpc_exceptions.InternalServerError as e:
            raise OperationalError(e.details if hasattr(e, 'details') else e)
        except grpc_exceptions.Aborted as e:
            raise InternalError(e.details if hasattr(e, 'details') else e)

    def __handle_update(self, txn, sql, params, param_types=None):
        sql = ensure_where_clause(sql)
        sql, params = sql_pyformat_args_to_spanner(sql, params)

        res = txn.execute_update(sql, params=params, param_types=get_param_types(params))
        self._itr = None
        if type(res) == int:
            self._row_count = res

        return res

    def __handle_insert(self, txn, sql, params):
        parts = parse_insert(sql, params)

        # The split between the two styles exists because:
        # in the common case of multiple values being passed
        # with simple pyformat arguments,
        #   SQL: INSERT INTO T (f1, f2) VALUES (%s, %s, %s)
        #   Params:   [(1, 2, 3, 4, 5, 6, 7, 8, 9, 10,)]
        # we can take advantage of a single RPC with:
        #       transaction.insert(table, columns, values)
        # instead of invoking:
        #   with transaction:
        #       for sql, params in sql_params_list:
        #           transaction.execute_sql(sql, params, param_types)
        # which invokes more RPCs and is more costly.

        sql_params_list = parts.get('sql_params_list')
        for sql, params in sql_params_list:
            sql, params = sql_pyformat_args_to_spanner(sql, params)
            param_types = get_param_types(params)
            res = txn.execute_update(sql, params=params, param_types=param_types)
            # TODO: File a bug with Cloud Spanner and the Python client maintainers
            # about a lost commit when res isn't read from.
            if hasattr(res, '__iter__'):
                _ = list(res)
            elif isinstance(res, int):
                self._row_count = res

    def __handle_DQL(self, txn, sql, params):
        # Reference
        #  https://googleapis.dev/python/spanner/latest/session-api.html#google.cloud.spanner_v1.session.Session.execute_sql
        sql, params = sql_pyformat_args_to_spanner(sql, params)
        res = txn.execute_sql(sql, params=params, param_types=get_param_types(params))
        if type(res) == int:
            self._row_count = res
            self._itr = None
        else:
            # Immediately using:
            #   iter(response)
            # here, because this Spanner API doesn't provide
            # easy mechanisms to detect when only a single item
            # is returned or many, yet mixing results that
            # are for .fetchone() with those that would result in
            # many items returns a RuntimeError if .fetchone() is
            # invoked and vice versa.
            self._res = res
            # Read the first element so that StreamedResult can
            # return the metadata after a DQL statement. See issue #155.
            self._itr = PeekIterator(self._res)
            # Unfortunately, Spanner doesn't seem to send back
            # information about the number of rows available.
            self._row_count = _UNSET_COUNT

    def __enter__(self):
        return self

    def __exit__(self, etype, value, traceback):
        if not etype:  # Not an exception thus we should commit.
            self._connection.commit()
        else:  # An exception occured within the context so rollback.
            self._connection.rollback()

        self.__clear()

    def __clear(self):
        self._connection = None
        self.__txn = None
