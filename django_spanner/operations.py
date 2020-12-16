# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

import os
import re
from base64 import b64decode
from datetime import datetime, time
from decimal import Decimal
from uuid import UUID

from django.conf import settings
from django.db.backends.base.operations import BaseDatabaseOperations
from django.db.utils import DatabaseError
from django.utils import timezone
from django.utils.duration import duration_microseconds
from google.cloud.spanner_dbapi.parse_utils import (
    DateStr,
    TimestampStr,
    escape_name,
)


class DatabaseOperations(BaseDatabaseOperations):
    """A Spanner-specific version of Django database operations."""
    cast_data_types = {"CharField": "STRING", "TextField": "STRING"}
    cast_char_field_without_max_length = "STRING"
    compiler_module = "django_spanner.compiler"

    # Django's lookup names that require a different name in Spanner's
    # EXTRACT() function.
    # https://cloud.google.com/spanner/docs/functions-and-operators#extract
    extract_names = {
        "iso_year": "isoyear",
        "week": "isoweek",
        "week_day": "dayofweek",
    }

    # TODO: Consider changing the hardcoded output to a linked value.
    def max_name_length(self):
        """Get the maximum length of Spanner table and column names.

        See also: https://cloud.google.com/spanner/quotas#tables

        :rtype: int
        :returns: Maximum length of the name of the table.
        """
        return 128

    def quote_name(self, name):
        """
        Return a quoted version of the given table or column name. Also,
        applies backticks to the name that either contain '-' or ' ', or is a
        Cloud Spanner's reserved keyword.

        Spanner says "column name not valid" if spaces or hyphens are present
        (although according to the documantation, any character should be
        allowed in quoted identifiers). Replace problematic characters when
        running the Django tests to prevent crashes. (Don't modify names in
        normal operation to prevent the possibility of colliding with another
        column.)

        See: https://github.com/googleapis/python-spanner-django/issues/204

        :type name: str
        :param name: The Quota name.

        :rtype: :class:`str`
        :returns: Name escaped if it has to be escaped.
        """
        if os.environ.get("RUNNING_SPANNER_BACKEND_TESTS") == "1":
            name = name.replace(" ", "_").replace("-", "_")
        return escape_name(name)

    def bulk_batch_size(self, fields, objs):
        """
        Override the base class method. Returns the maximum number of the
        query parameters.

        :type fields: list
        :param fields: Currently not used.

        :type objs: list
        :param objs: Currently not used.

        :rtype: int
        :returns: The maximum number of query parameters (constant).
        """
        return self.connection.features.max_query_params

    def bulk_insert_sql(self, fields, placeholder_rows):
        """
        A helper method that stitches multiple values into a single SQL
        record.

        :type fields: list
        :param fields: Currently not used.

        :type placeholder_rows: list
        :param placeholder_rows: Data "rows" containing values to combine.

        :rtype: str
        :returns: A SQL statement (a `VALUES` command).
        """
        placeholder_rows_sql = (", ".join(row) for row in placeholder_rows)
        values_sql = ", ".join("(%s)" % sql for sql in placeholder_rows_sql)
        return "VALUES " + values_sql

    def sql_flush(self, style, tables, reset_sequences=False, allow_cascade=False):
        """
        Override the base class method. Returns a list of SQL statements
        required to remove all data from the given database tables (without
        actually removing the tables themselves).

        :type style: :class:`~django.core.management.color.Style`
        :param style: (Currently not used) An object as returned by either
                      color_style() or no_style().

        :type tables: list
        :param tables: A collection of Cloud Spanner Tables

        :type reset_sequences: bool
        :param reset_sequences: (Optional) Currently not used.

        :type allow_cascade: bool
        :param allow_cascade: (Optional) Currently not used.

        :rtype: list
        :returns: A list of SQL statements required to remove all data from
        the given database tables.
        """
        # Cloud Spanner doesn't support TRUNCATE so DELETE instead.
        # A dummy WHERE clause is required.
        if tables:
            delete_sql = "%s %s %%s" % (
                style.SQL_KEYWORD("DELETE"),
                style.SQL_KEYWORD("FROM"),
            )
            return [
                delete_sql % style.SQL_FIELD(self.quote_name(table))
                for table in tables
            ]
        else:
            return []

    def adapt_datefield_value(self, value):
        """Cast date argument into Spanner DB API DateStr format.

        :type value: object
        :param value: A date argument.

        :rtype: :class:`~google.cloud.spanner_dbapi.types.DateStr`
        :returns: Formatted Date.
        """
        if value is None:
            return None
        return DateStr(str(value))

    def adapt_datetimefield_value(self, value):
        """Reformat time argument into Cloud Spanner.

        :type value: object
        :param value: A time argument.

        :rtype: :class:`~google.cloud.spanner_dbapi.types.TimestampStr`
        :returns: Formatted Time.
        """
        if value is None:
            return None
        # Expression values are adapted by the database.
        if hasattr(value, "resolve_expression"):
            return value
        # Cloud Spanner doesn't support tz-aware datetimes
        if timezone.is_aware(value):
            if settings.USE_TZ:
                value = timezone.make_naive(value, self.connection.timezone)
            else:
                raise ValueError(
                    "The Cloud Spanner backend does not support "
                    "timezone-aware datetimes when USE_TZ is False."
                )
        return TimestampStr(value.isoformat(timespec="microseconds") + "Z")

    def adapt_decimalfield_value(
        self, value, max_digits=None, decimal_places=None
    ):
        """
        Convert value from decimal.Decimal into float, for a direct mapping
        and correct serialization with RPCs to Cloud Spanner.

        :type value: :class:`~google.cloud.spanner_v1.types.Numeric`
        :param value: A decimal field value.

        :type max_digits: int
        :param max_digits: (Optional) A maximum number of digits.

        :type decimal_places: int
        :param decimal_places: (Optional) The number of decimal places to store
                               with the number.

        :rtype: float
        :returns: Formatted value.
        """
        if value is None:
            return None
        return float(value)

    def adapt_timefield_value(self, value):
        """
        Transform a time value to an object compatible with what is expected
        by the backend driver for time columns.

        :type value: `datetime.datetime`
        :param value: A time field value.

        :rtype: :class:`~google.cloud.spanner_dbapi.types.TimestampStr`
        :returns: Formatted Time.
        """
        if value is None:
            return None
        # Expression values are adapted by the database.
        if hasattr(value, "resolve_expression"):
            return value
        # Column is TIMESTAMP, so prefix a dummy date to the datetime.time.
        return TimestampStr(
            "0001-01-01T" + value.isoformat(timespec="microseconds") + "Z"
        )

    def get_db_converters(self, expression):
        """Get a list of functions needed to convert field data.

        :type expression: :class:`django.db.models.expressions.BaseExpression`
        :param expression: A query expression to convert.

        :rtype: list
        :returns: Converter functions to apply to Spanner field values.
        """
        converters = super().get_db_converters(expression)
        internal_type = expression.output_field.get_internal_type()
        if internal_type == "DateTimeField":
            converters.append(self.convert_datetimefield_value)
        elif internal_type == "DecimalField":
            converters.append(self.convert_decimalfield_value)
        elif internal_type == "TimeField":
            converters.append(self.convert_timefield_value)
        elif internal_type == "BinaryField":
            converters.append(self.convert_binaryfield_value)
        elif internal_type == "UUIDField":
            converters.append(self.convert_uuidfield_value)
        return converters

    def convert_binaryfield_value(self, value, expression, connection):
        """Convert Spanner BinaryField value for Django.

        :type value: bytes
        :param value: A base64-encoded binary field value.

        :type expression: :class:`django.db.models.expressions.BaseExpression`
        :param expression: A query expression.

        :type connection: :class:`~google.cloud.cpanner_dbapi.connection.Connection`
        :param connection: Reference to a Spanner database connection.

        :rtype: bytes
        :returns: A base64 encoded bytes.
        """
        if value is None:
            return value
        # Cloud Spanner stores bytes base64 encoded.
        return b64decode(value)

    def convert_datetimefield_value(self, value, expression, connection):
        """Convert Spanner DateTimeField value for Django.

        :type value: `DatetimeWithNanoseconds`
        :param value: A datetime field value.

        :type expression: :class:`django.db.models.expressions.BaseExpression`
        :param expression: A query expression.

        :type connection: :class:`~google.cloud.cpanner_dbapi.connection.Connection`
        :param connection: Reference to a Spanner database connection.

        :rtype: datetime
        :returns: A TZ-aware datetime.
        """
        if value is None:
            return value
        # Cloud Spanner returns the
        # google.api_core.datetime_helpers.DatetimeWithNanoseconds subclass
        # of datetime with tzinfo=UTC (which should be replaced with the
        # connection's timezone). Django doesn't support nanoseconds so that
        # part is ignored.
        dt = datetime(
            value.year,
            value.month,
            value.day,
            value.hour,
            value.minute,
            value.second,
            value.microsecond,
        )
        return (
            timezone.make_aware(dt, self.connection.timezone)
            if settings.USE_TZ
            else dt
        )

    def convert_decimalfield_value(self, value, expression, connection):
        """Convert Spanner DecimalField value for Django.

        :type value: float
        :param value: A decimal field.

        :type expression: :class:`django.db.models.expressions.BaseExpression`
        :param expression: A query expression.

        :type connection: :class:`~google.cloud.cpanner_dbapi.connection.Connection`
        :param connection: Reference to a Spanner database connection.

        :rtype: :class:`Decimal`
        :returns: A converted decimal field.
        """
        if value is None:
            return value
        # Cloud Spanner returns a float.
        return Decimal(str(value))

    def convert_timefield_value(self, value, expression, connection):
        """Convert Spanner TimeField value for Django.

        :type value: :class:`~google.api_core.datetime_helpers.DatetimeWithNanoseconds`
        :param value: A datetime/time field.

        :type expression: :class:`django.db.models.expressions.BaseExpression`
        :param expression: A query expression.

        :type connection: :class:`~google.cloud.cpanner_dbapi.connection.Connection`
        :param connection: Reference to a Spanner database connection.

        :rtype: :class:`datetime.time`
        :returns: A converted datetime.
        """
        if value is None:
            return value
        # Convert DatetimeWithNanoseconds to time.
        return time(value.hour, value.minute, value.second, value.microsecond)

    def convert_uuidfield_value(self, value, expression, connection):
        """Convert a UUID field to Cloud Spanner.

        :type value: str
        :param value: A UUID-valued str.

        :type expression: :class:`django.db.models.expressions.BaseExpression`
        :param expression: A query expression.

        :type connection: :class:`~google.cloud.cpanner_dbapi.connection.Connection`
        :param connection: Reference to a Spanner database connection.

        :rtype: :class:`uuid.UUID`
        :returns: A converted UUID.
        """
        if value is not None:
            value = UUID(value)
        return value

    def date_extract_sql(self, lookup_type, field_name):
        """Extract date from the lookup.

        :type lookup_type: str
        :param lookup_type: A type of the lookup.

        :type field_name: str
        :param field_name: The name of the field.

        :rtype: str
        :returns: A SQL statement for extracting.
        """
        lookup_type = self.extract_names.get(lookup_type, lookup_type)
        return "EXTRACT(%s FROM %s)" % (lookup_type, field_name)

    def datetime_extract_sql(self, lookup_type, field_name, tzname):
        """Extract datetime from the lookup.

        :type lookup_type: str
        :param lookup_type: A type of the lookup.

        :type field_name: str
        :param field_name: The name of the field.

        :type tzname: str
        :param tzname: The time zone name. If using of time zone is not
                       allowed in settings default will be UTC.

        :rtype: str
        :returns: A SQL statement for extracting.
        """
        tzname = tzname if settings.USE_TZ else "UTC"
        lookup_type = self.extract_names.get(lookup_type, lookup_type)
        return 'EXTRACT(%s FROM %s AT TIME ZONE "%s")' % (
            lookup_type,
            field_name,
            tzname,
        )

    def time_extract_sql(self, lookup_type, field_name):
        """Extract time from the lookup.

        :type lookup_type: str
        :param lookup_type: A type of the lookup.

        :type field_name: str
        :param field_name: The name of the field.

        :rtype: str
        :returns: A SQL statement for extracting.
        """
        # Time is stored as TIMESTAMP with UTC time zone.
        return 'EXTRACT(%s FROM %s AT TIME ZONE "UTC")' % (
            lookup_type,
            field_name,
        )

    def date_trunc_sql(self, lookup_type, field_name):
        """Truncate date in the lookup.

        :type lookup_type: str
        :param lookup_type: A type of the lookup.

        :type field_name: str
        :param field_name: The name of the field.

        :rtype: str
        :returns: A SQL statement for truncating.
        """
        # https://cloud.google.com/spanner/docs/functions-and-operators#date_trunc
        if lookup_type == "week":
            # Spanner truncates to Sunday but Django expects Monday. First,
            # subtract a day so that a Sunday will be truncated to the previous
            # week...
            field_name = (
                "DATE_SUB(CAST(" + field_name + " AS DATE), INTERVAL 1 DAY)"
            )
        sql = "DATE_TRUNC(CAST(%s AS DATE), %s)" % (field_name, lookup_type)
        if lookup_type == "week":
            # ...then add a day to get from Sunday to Monday.
            sql = "DATE_ADD(CAST(" + sql + " AS DATE), INTERVAL 1 DAY)"
        return sql

    def datetime_trunc_sql(self, lookup_type, field_name, tzname):
        """Truncate datetime in the lookup.

        :type lookup_type: str
        :param lookup_type: A type of the lookup.

        :type field_name: str
        :param field_name: The name of the field.

        :rtype: str
        :returns: A SQL statement for truncating.
        """
        # https://cloud.google.com/spanner/docs/functions-and-operators#timestamp_trunc
        tzname = tzname if settings.USE_TZ else "UTC"
        if lookup_type == "week":
            # Spanner truncates to Sunday but Django expects Monday. First,
            # subtract a day so that a Sunday will be truncated to the previous
            # week...
            field_name = "TIMESTAMP_SUB(" + field_name + ", INTERVAL 1 DAY)"
        sql = 'TIMESTAMP_TRUNC(%s, %s, "%s")' % (
            field_name,
            lookup_type,
            tzname,
        )
        if lookup_type == "week":
            # ...then add a day to get from Sunday to Monday.
            sql = "TIMESTAMP_ADD(" + sql + ", INTERVAL 1 DAY)"
        return sql

    def time_trunc_sql(self, lookup_type, field_name):
        """Truncate time in the lookup.

        :type lookup_type: str
        :param lookup_type: A type of the lookup.

        :type field_name: str
        :param field_name: The name of the field.

        :rtype: str
        :returns: A SQL statement for truncating.
        """
        # https://cloud.google.com/spanner/docs/functions-and-operators#timestamp_trunc
        return 'TIMESTAMP_TRUNC(%s, %s, "UTC")' % (field_name, lookup_type)

    def datetime_cast_date_sql(self, field_name, tzname):
        """Cast date in the lookup.

        :type field_name: str
        :param field_name: The name of the field.

        :type tzname: str
        :param tzname: The time zone name. If using of time zone is not
                       allowed in settings default will be UTC.

        :rtype: str
        :returns: A SQL statement for casting.
        """
        # https://cloud.google.com/spanner/docs/functions-and-operators#date
        tzname = tzname if settings.USE_TZ else "UTC"
        return 'DATE(%s, "%s")' % (field_name, tzname)

    def datetime_cast_time_sql(self, field_name, tzname):
        """Cast time in the lookup.

        :type field_name: str
        :param field_name: The name of the field.

        :type tzname: str
        :param tzname: The time zone name. If using of time zone is not
                       allowed in settings default will be UTC.

        :rtype: str
        :returns: A SQL statement for casting.
        """
        tzname = tzname if settings.USE_TZ else "UTC"
        # Cloud Spanner doesn't have a function for converting
        # TIMESTAMP to another time zone.
        return (
            "TIMESTAMP(FORMAT_TIMESTAMP("
            "'%%Y-%%m-%%d %%R:%%E9S %%Z', %s, '%s'))" % (field_name, tzname)
        )

    def date_interval_sql(self, timedelta):
        """Get a date interval in microseconds.

        :type timedelta: datetime
        :param timedelta: A time delta for the interval.

        :rtype: str
        :returns: A SQL statement.
        """
        return "INTERVAL %s MICROSECOND" % duration_microseconds(timedelta)

    def format_for_duration_arithmetic(self, sql):
        """Do nothing since formatting is handled in the custom function.

        :type sql: str
        :param sql: A SQL statement.

        :rtype: str
        :return: A SQL statement.
        """
        return "INTERVAL %s MICROSECOND" % sql

    def combine_expression(self, connector, sub_expressions):
        """Recurrently combine expressions into single one using connector.

        :type connector: str
        :param connector: A type of connector operation.

        :type sub_expressions: list
        :param sub_expressions: A list of expressions to combine.

        :rtype: str
        :return: A SQL statement for combining.
        """
        if connector == "%%":
            return "MOD(%s)" % ", ".join(sub_expressions)
        elif connector == "^":
            return "POWER(%s)" % ", ".join(sub_expressions)
        elif connector == ">>":
            lhs, rhs = sub_expressions
            # Use an alternate computation because Cloud Sapnner's '>>'
            # operator does not do sign bit extension with a signed type (i.e.
            # produces different results for negative numbers than what
            # Django's tests expect). Cast float result as INT64 to allow
            # assigning to both INT64 and FLOAT64 columns (otherwise the FLOAT
            # result couldn't be assigned to INT64 columns).
            return "CAST(FLOOR(%(lhs)s / POW(2, %(rhs)s)) AS INT64)" % {
                "lhs": lhs,
                "rhs": rhs,
            }
        return super().combine_expression(connector, sub_expressions)

    def combine_duration_expression(self, connector, sub_expressions):
        """Combine duration expressions into single one using connector.

        :type connector: str
        :param connector: A type of connector operation.

        :type sub_expressions: list
        :param sub_expressions: A list of expressions to combine.

        :raises: :class:`~django.db.utils.DatabaseError`

        :rtype: str
        :return: A SQL statement for combining.
        """
        if connector == "+":
            return "TIMESTAMP_ADD(" + ", ".join(sub_expressions) + ")"
        elif connector == "-":
            return "TIMESTAMP_SUB(" + ", ".join(sub_expressions) + ")"
        else:
            raise DatabaseError(
                "Invalid connector for timedelta: %s." % connector
            )

    def lookup_cast(self, lookup_type, internal_type=None):
        """
        Cast text lookups to string to allow things like  filter(x__contains=4).

        :type lookup_type: str
        :param lookup_type: A type of the lookup.

        :type internal_type: str
        :param internal_type: (Optional)

        :rtype: str
        :return: A SQL statement.
        """
        # Cast text lookups to string to allow things like
        # filter(x__contains=4)
        if lookup_type in (
            "contains",
            "icontains",
            "startswith",
            "istartswith",
            "endswith",
            "iendswith",
            "regex",
            "iregex",
            "iexact",
        ):
            return "CAST(%s AS STRING)"
        return "%s"

    def prep_for_like_query(self, x):
        """Lookups that use this method use REGEXP_CONTAINS instead of LIKE.

        :type x: str
        :param x: A query to prepare.

        :rtype: str
        :returns: A prepared query.
        """
        return re.escape(str(x))

    prep_for_iexact_query = prep_for_like_query

    def no_limit_value(self):
        """The largest INT64: (2**63) - 1

        :rtype: int
        :returns: The largest INT64.
        """
        return 9223372036854775807

    def _get_limit_offset_params(self, low_mark, high_mark):
        limit, offset = super()._get_limit_offset_params(low_mark, high_mark)
        if offset and limit == self.connection.ops.no_limit_value():
            # Subtract offset from the limit to avoid an INT64 overflow error
            # from Cloud Spanner.
            limit -= offset
        return limit, offset
