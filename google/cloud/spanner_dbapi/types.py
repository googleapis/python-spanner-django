# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""Implementation of the type objects and constructors according to the
   PEP-0249 specification.

   See
   https://www.python.org/dev/peps/pep-0249/#type-objects-and-constructors
"""

import datetime
from base64 import b64encode


def _time_from_ticks(ticks, tz=None):
    """A helper method used to construct a DB-API time value.

    :type ticks: float
    :param ticks: The number of seconds passed since the epoch.

    :type tz: :class:`datetime.tzinfo`
    :param tz: (Optional) The timezone information to use for conversion.

    :rtype: :class:`datetime.time`
    :returns: The corresponding time value.
    """
    return datetime.datetime.fromtimestamp(ticks, tz=tz).timetz()


class _DBAPITypeObject(object):
    """Implementation of a helper class used for type comparison among similar
    but possibly different types.

    See
    https://www.python.org/dev/peps/pep-0249/#implementation-hints-for-module-authors
    """

    def __init__(self, *values):
        self.values = values

    def __eq__(self, other):
        return other in self.values


Date = datetime.date
Time = datetime.time
Timestamp = datetime.datetime
DateFromTicks = datetime.date.fromtimestamp
TimeFromTicks = _time_from_ticks
TimestampFromTicks = datetime.datetime.fromtimestamp
Binary = b64encode

STRING = "STRING"
BINARY = _DBAPITypeObject("TYPE_CODE_UNSPECIFIED", "BYTES", "ARRAY", "STRUCT")
NUMBER = _DBAPITypeObject("BOOL", "INT64", "FLOAT64", "NUMERIC")
DATETIME = _DBAPITypeObject("TIMESTAMP", "DATE")
ROWID = "STRING"


class TimestampStr(str):
    """[inherited from the alpha release]

    TODO: Decide whether this class is necessary

    TimestampStr exists so that we can purposefully format types as timestamps
    compatible with Cloud Spanner's TIMESTAMP type, but right before making
    queries, it'll help differentiate between normal strings and the case of
    types that should be TIMESTAMP.
    """

    pass


class DateStr(str):
    """[inherited from the alpha release]

    TODO: Decide whether this class is necessary

    DateStr is a sentinel type to help format Django dates as
    compatible with Cloud Spanner's DATE type, but right before making
    queries, it'll help differentiate between normal strings and the case of
    types that should be DATE.
    """

    pass
