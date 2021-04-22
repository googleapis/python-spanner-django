# Copyright 2021 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

from django.test import SimpleTestCase
from django_spanner.compiler import SQLCompiler
from django.db.models import F
from .models import Report


class TestExpressions(SimpleTestCase):
    settings_dict = {"dummy_param": "dummy"}

    def _get_target_class(self):
        from django_spanner.base import DatabaseWrapper

        return DatabaseWrapper

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_order_by_sql_query_with_order_by_null_last(self):
        connection = self._make_one(self.settings_dict)

        qs1 = Report.objects.values("name").order_by(
            F("name").desc(nulls_last=True)
        )
        compiler = SQLCompiler(qs1.query, connection, "default")
        sql_compiled, _ = compiler.as_sql()
        self.assertEqual(
            sql_compiled,
            "SELECT tests_report.name FROM tests_report ORDER BY "
            + "tests_report.name IS NULL, tests_report.name DESC",
        )

    def test_order_by_sql_query_with_order_by_null_first(self):
        connection = self._make_one(self.settings_dict)

        qs1 = Report.objects.values("name").order_by(
            F("name").desc(nulls_first=True)
        )
        compiler = SQLCompiler(qs1.query, connection, "default")
        sql_compiled, _ = compiler.as_sql()
        self.assertEqual(
            sql_compiled,
            "SELECT tests_report.name FROM tests_report ORDER BY "
            + "tests_report.name IS NOT NULL, tests_report.name DESC",
        )

    def test_order_by_sql_query_with_order_by_name(self):
        connection = self._make_one(self.settings_dict)

        qs1 = Report.objects.values("name")
        compiler = SQLCompiler(qs1.query, connection, "default")
        sql_compiled, _ = compiler.as_sql()
        self.assertEqual(
            sql_compiled,
            "SELECT tests_report.name FROM tests_report ORDER BY "
            + "tests_report.name ASC",
        )
