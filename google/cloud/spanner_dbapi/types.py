# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

# Implements the types requested by the Python Database API in:
#   https://www.python.org/dev/peps/pep-0249/#type-objects-and-constructors

import datetime
import time
from base64 import b64encode


def Date(year, month, day):
    """This function constructs an object holding a date value."""
    return datetime.date(year, month, day)


def Time(hour, minute, second):
    """This function constructs an object holding a time value."""
    return datetime.time(hour, minute, second)


def Timestamp(year, month, day, hour, minute, second):
    """This function constructs an object holding a time stamp value."""
    return datetime.datetime(year, month, day, hour, minute, second)


def DateFromTicks(ticks):
    """
    This function constructs an object holding a date value from the given
    ticks value (number of seconds since the epoch; see
    https://docs.python.org/3/library/time.html for details).
    """
    return Date(*time.localtime(ticks)[:3])


def TimeFromTicks(ticks):
    """
    Constructs an object holding a time value from the given ticks value (
    number of seconds since the epoch; see the documentation of the standard
    Python time module for details).
    """
    return Time(*time.localtime(ticks)[3:6])


def TimestampFromTicks(ticks):
    """
    Constructs an object holding a time stamp value from the given ticks
    value (number of seconds since the epoch; see the documentation of the
    standard Python time module for details).
    """
    return Timestamp(*time.localtime(ticks)[:6])


def Binary(string):
    """
    Constructs an object capable of holding a binary (long) string value.
    """
    return b64encode(string)


class BINARY:
    """
    Describes (long) binary columns in a database (e.g. LONG, RAW, BLOBS).
    """

    # TODO: Implement me.
    pass


class STRING:
    """
    Describes columns in a database that are string-based (e.g. CHAR).
    """

    # TODO: Implement me.
    pass


class NUMBER:
    """
    Describes numeric columns in a database.
    """

    # TODO: Implement me.
    pass


class DATETIME:
    """
    Describes date/time columns in a database.
    """

    # TODO: Implement me.
    pass


class ROWID:
    """Describes the "Row ID" column in a database."""

    # TODO: Implement me.
    pass


class TimestampStr(str):
    """
    TimestampStr exists so that we can purposefully format types as timestamps
    compatible with Cloud Spanner's TIMESTAMP type, but right before making
    queries, it'll help differentiate between normal strings and the case of
    types that should be TIMESTAMP.
    """

    pass


class DateStr(str):
    """
    DateStr is a sentinel type to help format Django dates as
    compatible with Cloud Spanner's DATE type, but right before making
    queries, it'll help differentiate between normal strings and the case of
    types that should be DATE.
    """

    pass
