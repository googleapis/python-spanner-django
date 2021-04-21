# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

import sys
import unittest

from django.test import SimpleTestCase
from django_spanner.compiler import SQLCompiler
from django.db.models import F
from .models import Number, Author


@unittest.skipIf(
    sys.version_info < (3, 6), reason="Skipping Python versions <= 3.5"
)
class TestUtils(SimpleTestCase):
    settings_dict = {"dummy_instance": "instance"}

    def _get_target_class(self):
        from django_spanner.base import DatabaseWrapper

        return DatabaseWrapper

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_cast_param_to_float_lte_sql_query(self):
        db_wrapper = self._make_one(self.settings_dict)

        qs1 = Number.objects.filter(decimal_num__lte=1.1).values("decimal_num")
        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()
        self.assertEqual(
            sql_compiled,
            "SELECT tests_number.decimal_num FROM tests_number WHERE "
            + "tests_number.decimal_num <= %s",
        )
        self.assertEqual(params, (1.1,))

    def test_cast_param_to_float_for_int_field_query(self):
        db_wrapper = self._make_one(self.settings_dict)

        qs1 = Number.objects.filter(num__lte=1.1).values("num")

        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()
        self.assertEqual(
            sql_compiled,
            "SELECT tests_number.num FROM tests_number WHERE "
            + "tests_number.num <= %s",
        )
        self.assertEqual(params, (1,))

    def test_cast_param_to_float_for_foreign_key_field_query(self):
        db_wrapper = self._make_one(self.settings_dict)

        qs1 = Number.objects.filter(item_id__exact="10").values("num")
        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()
        self.assertEqual(
            sql_compiled,
            "SELECT tests_number.num FROM tests_number WHERE "
            + "tests_number.item_id = %s",
        )
        self.assertEqual(params, (10,))

    def test_cast_param_to_float_with_no_params_query(self):
        db_wrapper = self._make_one(self.settings_dict)

        qs1 = Number.objects.filter(item_id__exact=F("num")).values("num")
        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()
        self.assertEqual(
            sql_compiled,
            "SELECT tests_number.num FROM tests_number WHERE "
            + "tests_number.item_id = (tests_number.num)",
        )
        self.assertEqual(params, ())

    def test_startswith_endswith_sql_query_with_startswith(self):
        db_wrapper = self._make_one(self.settings_dict)

        qs1 = Author.objects.filter(name__startswith="abc").values("num")
        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()
        self.assertEqual(
            sql_compiled,
            "SELECT tests_author.num FROM tests_author WHERE "
            + "REGEXP_CONTAINS(CAST(tests_author.name AS STRING), %s)",
        )
        self.assertEqual(params, ("^abc",))

    def test_startswith_endswith_sql_query_with_endswith(self):
        db_wrapper = self._make_one(self.settings_dict)

        qs1 = Author.objects.filter(name__endswith="abc").values("num")
        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()
        self.assertEqual(
            sql_compiled,
            "SELECT tests_author.num FROM tests_author WHERE "
            + "REGEXP_CONTAINS(CAST(tests_author.name AS STRING), %s)",
        )
        self.assertEqual(params, ("abc$",))

    def test_startswith_endswith_sql_query_case_insensitive(self):
        db_wrapper = self._make_one(self.settings_dict)

        qs1 = Author.objects.filter(name__istartswith="abc").values("num")
        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()
        self.assertEqual(
            sql_compiled,
            "SELECT tests_author.num FROM tests_author WHERE "
            + "REGEXP_CONTAINS(CAST(tests_author.name AS STRING), %s)",
        )
        self.assertEqual(params, ("(?i)^abc",))

    def test_startswith_endswith_sql_query_with_bileteral_transform(self):
        db_wrapper = self._make_one(self.settings_dict)

        qs1 = Author.objects.filter(name__upper__startswith="abc").values(
            "name"
        )

        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()
        self.assertEqual(
            sql_compiled,
            "SELECT tests_author.name FROM tests_author WHERE "
            + "REGEXP_CONTAINS(CAST(UPPER(tests_author.name) AS STRING), "
            + "REPLACE(REPLACE(REPLACE(CONCAT('^', (UPPER(%s))), "
            + '"\\\\", "\\\\\\\\"), "%%", r"\\%%"), "_", r"\\_"))',
        )
        self.assertEqual(params, ("abc",))

    def test_startswith_endswith_case_insensitive_transform_sql_query(self):
        db_wrapper = self._make_one(self.settings_dict)

        qs1 = Author.objects.filter(name__upper__istartswith="abc").values(
            "name"
        )

        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()
        self.assertEqual(
            sql_compiled,
            "SELECT tests_author.name FROM tests_author WHERE "
            + "REGEXP_CONTAINS(CAST(UPPER(tests_author.name) AS STRING), "
            + "REPLACE(REPLACE(REPLACE(CONCAT('^(?i)', (UPPER(%s))), "
            + '"\\\\", "\\\\\\\\"), "%%", r"\\%%"), "_", r"\\_"))',
        )
        self.assertEqual(params, ("abc",))

    def test_startswith_endswith_endswith_sql_query_with_transform(self):
        db_wrapper = self._make_one(self.settings_dict)

        qs1 = Author.objects.filter(name__upper__endswith="abc").values("name")

        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()

        self.assertEqual(
            sql_compiled,
            "SELECT tests_author.name FROM tests_author WHERE "
            + "REGEXP_CONTAINS(CAST(UPPER(tests_author.name) AS STRING), "
            + "REPLACE(REPLACE(REPLACE(CONCAT('', (UPPER(%s)), '$'), "
            + '"\\\\", "\\\\\\\\"), "%%", r"\\%%"), "_", r"\\_"))',
        )
        self.assertEqual(params, ("abc",))

    def test_regex_sql_query_case_sensitive(self):
        db_wrapper = self._make_one(self.settings_dict)

        qs1 = Author.objects.filter(name__regex="abc").values("num")
        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()
        self.assertEqual(
            sql_compiled,
            "SELECT tests_author.num FROM tests_author WHERE "
            "REGEXP_CONTAINS(CAST(tests_author.name AS STRING), %s)",
        )
        self.assertEqual(params, ("abc",))

    def test_regex_sql_query_case_insensitive(self):
        db_wrapper = self._make_one(self.settings_dict)

        qs1 = Author.objects.filter(name__iregex="abc").values("num")
        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()
        self.assertEqual(
            sql_compiled,
            "SELECT tests_author.num FROM tests_author WHERE "
            "REGEXP_CONTAINS(CAST(tests_author.name AS STRING), %s)",
        )
        self.assertEqual(params, ("(?i)abc",))

    def test_regex_sql_query_case_sensitive_with_transform(self):
        db_wrapper = self._make_one(self.settings_dict)

        qs1 = Author.objects.filter(name__upper__regex="abc").values("num")
        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()

        self.assertEqual(
            sql_compiled,
            "SELECT tests_author.num FROM tests_author WHERE "
            + "REGEXP_CONTAINS(CAST(UPPER(tests_author.name) AS STRING), "
            + "(UPPER(%s)))",
        )
        self.assertEqual(params, ("abc",))

    def test_regex_sql_query_case_insensitive_with_transform(self):
        db_wrapper = self._make_one(self.settings_dict)

        qs1 = Author.objects.filter(name__upper__iregex="abc").values("num")
        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()

        self.assertEqual(
            sql_compiled,
            "SELECT tests_author.num FROM tests_author WHERE "
            + "REGEXP_CONTAINS(CAST(UPPER(tests_author.name) AS STRING), "
            + "CONCAT('(?i)', (UPPER(%s))))",
        )
        self.assertEqual(params, ("abc",))

    def test_contains_sql_query_case_insensitive(self):
        db_wrapper = self._make_one(self.settings_dict)

        qs1 = Author.objects.filter(name__icontains="abc").values("num")
        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()
        self.assertEqual(
            sql_compiled,
            "SELECT tests_author.num FROM tests_author WHERE "
            + "REGEXP_CONTAINS(CAST(tests_author.name AS STRING), %s)",
        )
        self.assertEqual(params, ("(?i)abc",))

    def test_contains_sql_query_case_sensitive(self):
        db_wrapper = self._make_one(self.settings_dict)

        qs1 = Author.objects.filter(name__contains="abc").values("num")
        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()
        self.assertEqual(
            sql_compiled,
            "SELECT tests_author.num FROM tests_author WHERE "
            + "REGEXP_CONTAINS(CAST(tests_author.name AS STRING), %s)",
        )
        self.assertEqual(params, ("abc",))

    def test_contains_sql_query_case_insensitive_transform(self):
        db_wrapper = self._make_one(self.settings_dict)

        qs1 = Author.objects.filter(name__upper__icontains="abc").values(
            "name"
        )
        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()
        self.assertEqual(
            sql_compiled,
            "SELECT tests_author.name FROM tests_author WHERE "
            + "REGEXP_CONTAINS(CAST(UPPER(tests_author.name) AS STRING), "
            + "REPLACE(REPLACE(REPLACE(CONCAT('(?i)', (UPPER(%s))), "
            + '"\\\\", "\\\\\\\\"), "%%", r"\\%%"), "_", r"\\_"))',
        )
        self.assertEqual(params, ("abc",))

    def test_contains_sql_query_case_sensitive_transform(self):
        db_wrapper = self._make_one(self.settings_dict)

        qs1 = Author.objects.filter(name__upper__contains="abc").values("name")
        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()
        self.assertEqual(
            sql_compiled,
            "SELECT tests_author.name FROM tests_author WHERE "
            + "REGEXP_CONTAINS(CAST(UPPER(tests_author.name) AS STRING), "
            + 'REPLACE(REPLACE(REPLACE((UPPER(%s)), "\\\\", "\\\\\\\\"), '
            + '"%%", r"\\%%"), "_", r"\\_"))',
        )
        self.assertEqual(params, ("abc",))

    def test_iexact_sql_query_case_insensitive(self):
        db_wrapper = self._make_one(self.settings_dict)

        qs1 = Author.objects.filter(name__iexact="abc").values("num")
        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()

        self.assertEqual(
            sql_compiled,
            "SELECT tests_author.num FROM tests_author WHERE "
            + "REGEXP_CONTAINS(CAST(tests_author.name AS STRING), %s)",
        )
        self.assertEqual(params, ("^(?i)abc$",))

    def test_iexact_sql_query_case_insensitive_transform(self):
        db_wrapper = self._make_one(self.settings_dict)
        qs1 = Author.objects.filter(name__upper__iexact="abc").values("name")
        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()
        self.assertEqual(
            sql_compiled,
            "SELECT tests_author.name FROM tests_author WHERE "
            + "REGEXP_CONTAINS((UPPER(CONCAT('^(?i)', "
            + "CAST(UPPER(tests_author.name) AS STRING), '$'))), %s)",
        )
        self.assertEqual(params, ("abc",))

    def test_iexact_sql_query_case_insensitive_function_transform(self):
        db_wrapper = self._make_one(self.settings_dict)

        qs1 = Author.objects.filter(name__upper__iexact=F("last_name")).values(
            "name"
        )
        compiler = SQLCompiler(qs1.query, db_wrapper, "default")
        sql_compiled, params = compiler.as_sql()

        self.assertEqual(
            sql_compiled,
            "SELECT tests_author.name FROM tests_author WHERE "
            + "REGEXP_CONTAINS((UPPER(tests_author.last_name)), "
            + "CONCAT('^(?i)', CAST(UPPER(tests_author.name) AS STRING), '$'))",
        )
        self.assertEqual(params, ())
