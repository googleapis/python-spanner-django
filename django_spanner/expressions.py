# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

from django.db.models.expressions import OrderBy


def order_by(self, compiler, connection, **extra_context):
    """Order expressions in the SQL query.

    TODO: Make this function a part of the class.

    :rtype: str
    :returns: A SQL query.
    """
    # In Django 3.1, this can be replaced with
    # DatabaseFeatures.supports_order_by_nulls_modifier = False.
    template = None
    if self.nulls_last:
        template = "%(expression)s IS NULL, %(expression)s %(ordering)s"
    elif self.nulls_first:
        template = "%(expression)s IS NOT NULL, %(expression)s %(ordering)s"
    return self.as_sql(
        compiler, connection, template=template, **extra_context
    )


def register_expressions():
    """Register ordered expressions in Spanner."""
    OrderBy.as_spanner = order_by
