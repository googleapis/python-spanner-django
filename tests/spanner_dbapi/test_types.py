# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

import datetime
import time
from unittest import TestCase

from google.cloud._helpers import UTC
from google.cloud.spanner_dbapi import types


utcOffset = time.timezone  # offset for current timezone


class TypesTests(TestCase):
    def test__time_from_ticks(self):
        ticks = 1572822862.9782631  # Sun 03 Nov 2019 23:14:22 UTC
        timezone = UTC

        actual = types.TimeFromTicks(ticks, tz=timezone)
        expected = datetime.datetime.fromtimestamp(ticks, tz=timezone).timetz()

        self.assertTrue(
            actual == expected, "`%s` doesn't match\n`%s`" % (actual, expected)
        )

    def test_type_equal(self):
        self.assertEqual(types.BINARY, "TYPE_CODE_UNSPECIFIED")
        self.assertEqual(types.BINARY, "BYTES")
        self.assertEqual(types.BINARY, "ARRAY")
        self.assertEqual(types.BINARY, "STRUCT")
        self.assertNotEqual(types.BINARY, "STRING")

        self.assertEqual(types.NUMBER, "BOOL")
        self.assertEqual(types.NUMBER, "INT64")
        self.assertEqual(types.NUMBER, "FLOAT64")
        self.assertEqual(types.NUMBER, "NUMERIC")
        self.assertNotEqual(types.NUMBER, "STRING")

        self.assertEqual(types.DATETIME, "TIMESTAMP")
        self.assertEqual(types.DATETIME, "DATE")
        self.assertNotEqual(types.DATETIME, "STRING")
