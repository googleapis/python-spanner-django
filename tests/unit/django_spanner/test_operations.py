# Copyright 2021 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

from django.test import SimpleTestCase
from django.db.utils import DatabaseError
from datetime import timedelta
from django_spanner.operations import DatabaseOperations


class TestOperations(SimpleTestCase):
    def _get_target_class(self):
        from django_spanner.base import DatabaseWrapper

        return DatabaseWrapper

    def _make_one(self, *args, **kwargs):
        dummy_settings = {"dummy_param": "dummy"}
        conn = self._get_target_class()(settings_dict=dummy_settings)
        return DatabaseOperations(conn)

    def test_max_name_length(self):
        db_op = self._make_one()
        self.assertEqual(db_op.max_name_length(), 128)

    def test_quote_name(self):
        db_op = self._make_one()
        quoted_name = db_op.quote_name("abc")
        self.assertEqual(quoted_name, "abc")

    def test_quote_name_spanner_reserved_keyword_escaped(self):
        db_op = self._make_one()
        quoted_name = db_op.quote_name("ALL")
        self.assertEqual(quoted_name, "`ALL`")

    def test_bulk_batch_size(self):
        db_op = self._make_one()
        self.assertEqual(
            db_op.bulk_batch_size(fields=None, objs=None),
            db_op.connection.features.max_query_params,
        )

    def test_sql_flush(self):
        from django.core.management.color import no_style

        db_op = self._make_one()
        self.assertEqual(
            db_op.sql_flush(style=no_style(), tables=["Table1, Table2"]),
            ["DELETE FROM `Table1, Table2`"],
        )

    def test_sql_flush_empty_table_list(self):
        from django.core.management.color import no_style

        db_op = self._make_one()
        self.assertEqual(
            db_op.sql_flush(style=no_style(), tables=[]), [],
        )

    def test_adapt_datefield_value(self):
        from google.cloud.spanner_dbapi.types import DateStr

        db_op = self._make_one()
        self.assertIsInstance(
            db_op.adapt_datefield_value("dummy_date"), DateStr,
        )

    def test_adapt_datefield_value_none(self):
        db_op = self._make_one()
        self.assertIsNone(db_op.adapt_datefield_value(value=None),)

    def test_adapt_decimalfield_value(self):
        db_op = self._make_one()
        self.assertIsInstance(
            db_op.adapt_decimalfield_value(value=1), float,
        )

    def test_adapt_decimalfield_value_none(self):
        db_op = self._make_one()
        self.assertIsNone(db_op.adapt_decimalfield_value(value=None),)

    def test_convert_binaryfield_value(self):
        from base64 import b64encode

        db_op = self._make_one()
        self.assertEqual(
            db_op.convert_binaryfield_value(
                value=b64encode(b"abc"), expression=None, connection=None
            ),
            b"abc",
        )

    def test_convert_binaryfield_value_none(self):
        db_op = self._make_one()
        self.assertIsNone(
            db_op.convert_binaryfield_value(
                value=None, expression=None, connection=None
            ),
        )

    def test_adapt_datetimefield_value_none(self):
        db_op = self._make_one()
        self.assertIsNone(db_op.adapt_datetimefield_value(value=None),)

    def test_adapt_timefield_value_none(self):
        db_op = self._make_one()
        self.assertIsNone(db_op.adapt_timefield_value(value=None),)

    def test_convert_decimalfield_value(self):
        from decimal import Decimal

        db_op = self._make_one()
        self.assertIsInstance(
            db_op.convert_decimalfield_value(
                value=1.0, expression=None, connection=None
            ),
            Decimal,
        )

    def test_convert_decimalfield_value_none(self):
        db_op = self._make_one()
        self.assertIsNone(
            db_op.convert_decimalfield_value(
                value=None, expression=None, connection=None
            ),
        )

    def test_convert_uuidfield_value(self):
        import uuid

        db_op = self._make_one()
        uuid_obj = uuid.uuid4()
        self.assertEqual(
            db_op.convert_uuidfield_value(
                str(uuid_obj), expression=None, connection=None
            ),
            uuid_obj,
        )

    def test_convert_uuidfield_value_none(self):
        db_op = self._make_one()
        self.assertIsNone(
            db_op.convert_uuidfield_value(
                value=None, expression=None, connection=None
            ),
        )

    def test_date_extract_sql(self):
        db_op = self._make_one()
        self.assertEqual(
            db_op.date_extract_sql("week", "dummy_field"),
            "EXTRACT(isoweek FROM dummy_field)",
        )

    def test_date_extract_sql_lookup_type_dayofweek(self):
        db_op = self._make_one()
        self.assertEqual(
            db_op.date_extract_sql("dayofweek", "dummy_field"),
            "EXTRACT(dayofweek FROM dummy_field)",
        )

    def test_datetime_extract_sql(self):
        from django.conf import settings

        settings.USE_TZ = True
        db_op = self._make_one()
        self.assertEqual(
            db_op.datetime_extract_sql("dayofweek", "dummy_field", "IST"),
            'EXTRACT(dayofweek FROM dummy_field AT TIME ZONE "IST")',
        )

    def test_datetime_extract_sql_use_tz_false(self):
        from django.conf import settings

        settings.USE_TZ = False
        db_op = self._make_one()
        self.assertEqual(
            db_op.datetime_extract_sql("dayofweek", "dummy_field", "IST"),
            'EXTRACT(dayofweek FROM dummy_field AT TIME ZONE "UTC")',
        )
        settings.USE_TZ = True  # reset changes.

    def test_time_extract_sql(self):
        db_op = self._make_one()
        self.assertEqual(
            db_op.time_extract_sql("dayofweek", "dummy_field"),
            'EXTRACT(dayofweek FROM dummy_field AT TIME ZONE "UTC")',
        )

    def test_time_trunc_sql(self):
        db_op = self._make_one()
        self.assertEqual(
            db_op.time_trunc_sql("dayofweek", "dummy_field"),
            'TIMESTAMP_TRUNC(dummy_field, dayofweek, "UTC")',
        )

    def test_datetime_cast_date_sql(self):
        db_op = self._make_one()
        self.assertEqual(
            db_op.datetime_cast_date_sql("dummy_field", "IST"),
            'DATE(dummy_field, "IST")',
        )

    def test_datetime_cast_time_sql(self):
        from django.conf import settings

        settings.USE_TZ = True
        db_op = self._make_one()
        self.assertEqual(
            db_op.datetime_cast_time_sql("dummy_field", "IST"),
            "TIMESTAMP(FORMAT_TIMESTAMP('%Y-%m-%d %R:%E9S %Z', dummy_field, 'IST'))",
        )

    def test_datetime_cast_time_sql_use_tz_false(self):
        from django.conf import settings

        settings.USE_TZ = False
        db_op = self._make_one()
        self.assertEqual(
            db_op.datetime_cast_time_sql("dummy_field", "IST"),
            "TIMESTAMP(FORMAT_TIMESTAMP('%Y-%m-%d %R:%E9S %Z', dummy_field, 'UTC'))",
        )
        settings.USE_TZ = True  # reset changes.

    def test_date_interval_sql(self):
        db_op = self._make_one()
        self.assertEqual(
            db_op.date_interval_sql(timedelta(days=1)),
            "INTERVAL 86400000000 MICROSECOND",
        )

    def test_format_for_duration_arithmetic(self):
        db_op = self._make_one()
        self.assertEqual(
            db_op.format_for_duration_arithmetic(1200),
            "INTERVAL 1200 MICROSECOND",
        )

    def test_combine_expression_mod(self):
        db_op = self._make_one()
        self.assertEqual(
            db_op.combine_expression("%%", ["10", "2"]), "MOD(10, 2)",
        )

    def test_combine_expression_power(self):
        db_op = self._make_one()
        self.assertEqual(
            db_op.combine_expression("^", ["10", "2"]), "POWER(10, 2)",
        )

    def test_combine_expression_bit_extention(self):
        db_op = self._make_one()
        self.assertEqual(
            db_op.combine_expression(">>", ["10", "2"]),
            "CAST(FLOOR(10 / POW(2, 2)) AS INT64)",
        )

    def test_combine_expression_multiply(self):
        db_op = self._make_one()
        self.assertEqual(
            db_op.combine_expression("*", ["10", "2"]), "10 * 2",
        )

    def test_combine_duration_expression_add(self):
        db_op = self._make_one()
        self.assertEqual(
            db_op.combine_duration_expression(
                "+",
                ['TIMESTAMP "2008-12-25 15:30:00+00', "INTERVAL 10 MINUTE"],
            ),
            'TIMESTAMP_ADD(TIMESTAMP "2008-12-25 15:30:00+00, INTERVAL 10 MINUTE)',
        )

    def test_combine_duration_expression_subtract(self):
        db_op = self._make_one()
        self.assertEqual(
            db_op.combine_duration_expression(
                "-",
                ['TIMESTAMP "2008-12-25 15:30:00+00', "INTERVAL 10 MINUTE"],
            ),
            'TIMESTAMP_SUB(TIMESTAMP "2008-12-25 15:30:00+00, INTERVAL 10 MINUTE)',
        )

    def test_combine_duration_expression_database_error(self):
        db_op = self._make_one()
        msg = "Invalid connector for timedelta:"
        with self.assertRaisesMessage(DatabaseError, msg):
            db_op.combine_duration_expression(
                "*",
                ['TIMESTAMP "2008-12-25 15:30:00+00', "INTERVAL 10 MINUTE"],
            )

    def test_lookup_cast_match_lookup_type(self):
        db_op = self._make_one()
        self.assertEqual(
            db_op.lookup_cast("contains",), "CAST(%s AS STRING)",
        )

    def test_lookup_cast_unmatched_lookup_type(self):
        db_op = self._make_one()
        self.assertEqual(
            db_op.lookup_cast("dummy",), "%s",
        )
