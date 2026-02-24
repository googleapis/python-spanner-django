# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

from django.core.exceptions import EmptyResultSet
from django.db.models.sql.compiler import (
    SQLAggregateCompiler as BaseSQLAggregateCompiler,
    SQLCompiler as BaseSQLCompiler,
    SQLDeleteCompiler as BaseSQLDeleteCompiler,
    SQLInsertCompiler as BaseSQLInsertCompiler,
    SQLUpdateCompiler as BaseSQLUpdateCompiler,
)
from django.db.utils import DatabaseError


class SQLCompiler(BaseSQLCompiler):
    """
    A variation of the Django SQL compiler, adjusted for Spanner-specific
    functionality.
    """

    def get_combinator_sql(self, combinator, all):
        features = self.connection.features
        compilers = [
            query.get_compiler(self.using, self.connection, self.elide_empty)
            for query in self.query.combined_queries
        ]
        if not features.supports_slicing_ordering_in_compound:
            for compiler in compilers:
                if compiler.query.is_sliced:
                    raise DatabaseError(
                        "LIMIT/OFFSET not allowed in subqueries of compound statements."
                    )
                if compiler.get_order_by():
                    raise DatabaseError(
                        "ORDER BY not allowed in subqueries of compound statements."
                    )
        parts = []
        empty_compiler = None
        for compiler in compilers:
            try:
                # Use Django 5.2's combinator part SQL generation which handles column ordering correctly
                parts.append(self._get_combinator_part_sql(compiler))
            except EmptyResultSet:
                # Omit the empty queryset with UNION and with DIFFERENCE if the
                # first queryset is nonempty.
                if combinator == "union" or (combinator == "difference" and parts):
                    empty_compiler = compiler
                    continue
                raise
        if not parts:
            raise EmptyResultSet
        elif len(parts) == 1 and combinator == "union" and self.query.is_sliced:
            # A sliced union cannot be composed of a single component because
            # in the event the later is also sliced it might result in invalid
            # SQL due to the usage of multiple LIMIT clauses. Prevent that from
            # happening by always including an empty resultset query to force
            # the creation of an union.
            empty_compiler.elide_empty = False
            parts.append(self._get_combinator_part_sql(empty_compiler))
        combinator_sql = self.connection.ops.set_operators[combinator]
        # Spanner requires ALL or DISTINCT for all set operators (UNION, INTERSECT, EXCEPT)
        combinator_sql += " ALL" if all else " DISTINCT"
        braces = "{}"
        if not self.query.subquery and features.supports_slicing_ordering_in_compound:
            braces = "({})"
        sql_parts, args_parts = zip(
            *((braces.format(sql), args) for sql, args in parts)
        )
        result = [" {} ".format(combinator_sql).join(sql_parts)]
        params = []
        for part in args_parts:
            params.extend(part)
        return result, params


class SQLInsertCompiler(BaseSQLInsertCompiler, SQLCompiler):
    """A wrapper class for compatibility with Django specifications."""

    pass


class SQLDeleteCompiler(BaseSQLDeleteCompiler, SQLCompiler):
    """A wrapper class for compatibility with Django specifications."""

    pass


class SQLUpdateCompiler(BaseSQLUpdateCompiler, SQLCompiler):
    """A wrapper class for compatibility with Django specifications."""

    pass


class SQLAggregateCompiler(BaseSQLAggregateCompiler, SQLCompiler):
    """A wrapper class for compatibility with Django specifications."""

    pass
