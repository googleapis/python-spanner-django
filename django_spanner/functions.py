# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

import math

from django.db.models.expressions import Func, Value
from django.db.models.functions import (
    Cast,
    Chr,
    ConcatPair,
    Cot,
    Degrees,
    Left,
    Log,
    Ord,
    Pi,
    Radians,
    Right,
    StrIndex,
    Substr,
)


class IfNull(Func):
    function = "IFNULL"
    arity = 2


def cast(self, compiler, connection, **extra_context):
    """Cast SQL query for given parameters.

    TODO: describe all parameters when code will be ready.

    :rtype: str
    :returns: A SQL query.
    """
    # Account for a field's max_length using SUBSTR.
    max_length = getattr(self.output_field, "max_length", None)
    if max_length is not None:
        template = "SUBSTR(" + self.template + ", 0, %s)" % max_length
    else:
        template = self.template
    return self.as_sql(
        compiler, connection, template=template, **extra_context
    )


def chr_(self, compiler, connection, **extra_context):
    """Return a SQL query where the code points are displayed as a string.

    TODO: describe all parameters when code will be ready.

    :rtype: str
    :returns: A SQL query.
    """
    return self.as_sql(
        compiler,
        connection,
        template="CODE_POINTS_TO_STRING([%(expressions)s])",
        **extra_context
    )


def concatpair(self, compiler, connection, **extra_context):
    """Concatenates a SQL query into the sequence of :class:`IfNull` objects.

    TODO: describe all parameters when code will be ready.

    :rtype: str
    :returns: A SQL query.
    """
    # Spanner's CONCAT function returns null if any of its arguments are null.
    # Prevent that by converting null arguments to an empty string.
    clone = self.copy()
    clone.set_source_expressions(
        IfNull(e, Value("")) for e in self.get_source_expressions()
    )
    return clone.as_sql(compiler, connection, **extra_context)


def cot(self, compiler, connection, **extra_context):
    """Return a SQL query of calculated cotangent.

    TODO: describe all parameters when code will be ready.

    :rtype: str
    :returns: A SQL query.
    """
    return self.as_sql(
        compiler,
        connection,
        template="(1 / TAN(%(expressions)s))",
        **extra_context
    )


def degrees(self, compiler, connection, **extra_context):
    """Return a SQL query of the angle converted to degrees.

    TODO: describe all parameters when code will be ready.

    :rtype: str
    :returns: A SQL query.
    """
    return self.as_sql(
        compiler,
        connection,
        template="((%%(expressions)s) * 180 / %s)" % math.pi,
        **extra_context
    )


def left_and_right(self, compiler, connection, **extra_context):
    """

    TODO: describe all parameters when code will be ready.

    :rtype: str
    :returns: A SQL query.
    """
    return self.get_substr().as_spanner(compiler, connection, **extra_context)


def log(self, compiler, connection, **extra_context):
    """Return a SQL query of calculated logarithm.

    TODO: describe all parameters when code will be ready.

    :rtype: str
    :returns: A SQL query.
    """
    # This function is usually Log(b, x) returning the logarithm of x to the
    # base b, but on Spanner it's Log(x, b).
    clone = self.copy()
    clone.set_source_expressions(self.get_source_expressions()[::-1])
    return clone.as_sql(compiler, connection, **extra_context)


def ord_(self, compiler, connection, **extra_context):
    """Return a SQL query of the expression converted to ord.

    TODO: describe all parameters when code will be ready.

    :rtype: str
    :returns: A SQL query.
    """
    return self.as_sql(
        compiler,
        connection,
        template="TO_CODE_POINTS(%(expressions)s)[OFFSET(0)]",
        **extra_context
    )


def pi(self, compiler, connection, **extra_context):
    """Return a SQL query of PI constant.

    TODO: describe all parameters when code will be ready.

    :rtype: str
    :returns: A SQL query.
    """
    return self.as_sql(
        compiler, connection, template=str(math.pi), **extra_context
    )


def radians(self, compiler, connection, **extra_context):
    """Return a SQL query of the angle converted to radians.

    TODO: describe all parameters when code will be ready.

    :rtype: str
    :returns: A SQL query.
    """
    return self.as_sql(
        compiler,
        connection,
        template="((%%(expressions)s) * %s / 180)" % math.pi,
        **extra_context
    )


def strindex(self, compiler, connection, **extra_context):
    """Return a SQL query of the string position.

    TODO: describe all parameters when code will be ready.

    :rtype: str
    :returns: A SQL query.
    """
    return self.as_sql(
        compiler, connection, function="STRPOS", **extra_context
    )


def substr(self, compiler, connection, **extra_context):
    """Return a SQL query of substring.

    TODO: describe all parameters when code will be ready.

    :rtype: str
    :returns: A SQL query.
    """
    return self.as_sql(
        compiler, connection, function="SUBSTR", **extra_context
    )


def register_functions():
    """Register functions  in Spanner."""
    Cast.as_spanner = cast
    Chr.as_spanner = chr_
    ConcatPair.as_spanner = concatpair
    Cot.as_spanner = cot
    Degrees.as_spanner = degrees
    Left.as_spanner = left_and_right
    Log.as_spanner = log
    Ord.as_spanner = ord_
    Pi.as_spanner = pi
    Radians.as_spanner = radians
    Right.as_spanner = left_and_right
    StrIndex.as_spanner = strindex
    Substr.as_spanner = substr
