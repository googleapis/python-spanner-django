# Copyright 2021 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd


from .models import Author
from django.db import NotSupportedError
from django.db.models import Index
from django.db.models.fields import IntegerField
from django_spanner.schema import DatabaseSchemaEditor
from tests._helpers import HAS_OPENTELEMETRY_INSTALLED
from tests.unit.django_spanner.simple_test import SpannerSimpleTestClass
from unittest import mock
from tests.unit.django_spanner.test__opentelemetry_tracing import (
    PROJECT,
    INSTANCE_ID,
    DATABASE_ID,
)


BASE_ATTRIBUTES = {
    "db.type": "spanner",
    "db.engine": "django_spanner",
    "db.project": PROJECT,
    "db.instance": INSTANCE_ID,
    "db.name": DATABASE_ID,
}


class TestUtils(SpannerSimpleTestClass):
    def test_quote_value(self):
        """
        Tries quoting input value.
        """
        schema_editor = DatabaseSchemaEditor(self.connection)
        self.assertEqual(schema_editor.quote_value(value=1.1), "1.1")

    def test_skip_default(self):
        """
        Tries skipping default as Cloud spanner doesn't support it.
        """
        schema_editor = DatabaseSchemaEditor(self.connection)
        self.assertTrue(schema_editor.skip_default(field=None))

    def test_create_model(self):
        """
        Tries creating a model's table.
        """
        with DatabaseSchemaEditor(self.connection) as schema_editor:
            schema_editor.execute = mock.MagicMock()
            schema_editor.create_model(Author)

            schema_editor.execute.assert_called_once_with(
                "CREATE TABLE tests_author (id INT64 NOT NULL, name STRING(40) "
                + "NOT NULL, last_name STRING(40) NOT NULL, num INT64 NOT "
                + "NULL, created TIMESTAMP NOT NULL, modified TIMESTAMP) "
                + "PRIMARY KEY(id)",
                None,
            )
        if HAS_OPENTELEMETRY_INSTALLED:
            span_list = self.ot_exporter.get_finished_spans()
            self.assertEqual(len(span_list), 1)
            self.assertSpanAttributes(
                "CloudSpannerDjango.create_model",
                attributes=dict(BASE_ATTRIBUTES, model_name="tests_author"),
                span=span_list[0],
            )

    def test_delete_model(self):
        """
        Tests deleting a model
        """
        with DatabaseSchemaEditor(self.connection) as schema_editor:
            schema_editor.execute = mock.MagicMock()
            schema_editor._constraint_names = mock.MagicMock()
            schema_editor.delete_model(Author)

            schema_editor.execute.assert_called_once_with(
                "DROP TABLE tests_author",
            )

        if HAS_OPENTELEMETRY_INSTALLED:
            span_list = self.ot_exporter.get_finished_spans()
            self.assertEqual(len(span_list), 1)
            self.assertSpanAttributes(
                "CloudSpannerDjango.delete_model",
                attributes=dict(BASE_ATTRIBUTES, model_name="tests_author"),
                span=span_list[0],
            )

    def test_delete_model_with_index(self):
        """
        Tests deleting a model with index
        """
        with DatabaseSchemaEditor(self.connection) as schema_editor:
            schema_editor.execute = mock.MagicMock()

            def delete_index_sql(*args, **kwargs):
                # Overriding Statement creation with sql string.
                return "DROP INDEX num_unique"

            def constraint_names(*args, **kwargs):
                return ["num_unique"]

            schema_editor._delete_index_sql = delete_index_sql
            schema_editor._constraint_names = constraint_names
            schema_editor.delete_model(Author)

            calls = [
                mock.call("DROP INDEX num_unique"),
                mock.call("DROP TABLE tests_author"),
            ]

            schema_editor.execute.assert_has_calls(calls)

        if HAS_OPENTELEMETRY_INSTALLED:
            span_list = self.ot_exporter.get_finished_spans()
            self.assertEqual(len(span_list), 2)
            self.assertSpanAttributes(
                "CloudSpannerDjango.delete_model.delete_index",
                attributes=dict(
                    BASE_ATTRIBUTES,
                    model_name="tests_author",
                    index_name="num_unique",
                ),
                span=span_list[0],
            )
            self.assertSpanAttributes(
                "CloudSpannerDjango.delete_model",
                attributes=dict(BASE_ATTRIBUTES, model_name="tests_author",),
                span=span_list[1],
            )

    def test_add_field(self):
        """
        Tests adding fields to models
        """
        with DatabaseSchemaEditor(self.connection) as schema_editor:
            schema_editor.execute = mock.MagicMock()
            new_field = IntegerField(null=True)
            new_field.set_attributes_from_name("age")
            schema_editor.add_field(Author, new_field)

            schema_editor.execute.assert_called_once_with(
                "ALTER TABLE tests_author ADD COLUMN age INT64", []
            )

    def test_remove_field(self):
        """
        Tests remove fields from models
        """
        with DatabaseSchemaEditor(self.connection) as schema_editor:
            schema_editor.execute = mock.MagicMock()
            schema_editor._constraint_names = mock.MagicMock()
            remove_field = IntegerField(unique=True)
            remove_field.set_attributes_from_name("num")
            schema_editor.remove_field(Author, remove_field)

            schema_editor.execute.assert_called_once_with(
                "ALTER TABLE tests_author DROP COLUMN num"
            )

        if HAS_OPENTELEMETRY_INSTALLED:
            span_list = self.ot_exporter.get_finished_spans()
            self.assertEqual(len(span_list), 1)
            self.assertSpanAttributes(
                "CloudSpannerDjango.remove_field",
                attributes=dict(
                    BASE_ATTRIBUTES, model_name="tests_author", field="num",
                ),
                span=span_list[0],
            )

    def test_remove_field_with_index(self):
        """
        Tests remove fields from models
        """
        with DatabaseSchemaEditor(self.connection) as schema_editor:
            schema_editor.execute = mock.MagicMock()

            def delete_index_sql(*args, **kwargs):
                # Overriding Statement creation with sql string.
                return "DROP INDEX num_unique"

            def constraint_names(*args, **kwargs):
                return ["num_unique"]

            schema_editor._delete_index_sql = delete_index_sql
            schema_editor._constraint_names = constraint_names

            remove_field = IntegerField(unique=True)
            remove_field.set_attributes_from_name("num")
            schema_editor.remove_field(Author, remove_field)

            calls = [
                mock.call("DROP INDEX num_unique"),
                mock.call("ALTER TABLE tests_author DROP COLUMN num"),
            ]
            schema_editor.execute.assert_has_calls(calls)

        if HAS_OPENTELEMETRY_INSTALLED:
            span_list = self.ot_exporter.get_finished_spans()
            self.assertEqual(len(span_list), 2)
            self.assertSpanAttributes(
                "CloudSpannerDjango.remove_field.delete_index",
                attributes=dict(
                    BASE_ATTRIBUTES,
                    model_name="tests_author",
                    field="num",
                    index_name="num_unique",
                ),
                span=span_list[0],
            )
            self.assertSpanAttributes(
                "CloudSpannerDjango.remove_field",
                attributes=dict(
                    BASE_ATTRIBUTES, model_name="tests_author", field="num",
                ),
                span=span_list[1],
            )

    def test_column_sql_not_null_field(self):
        """
        Tests column sql for not null field
        """
        with DatabaseSchemaEditor(self.connection) as schema_editor:
            schema_editor.execute = mock.MagicMock()
            new_field = IntegerField()
            new_field.set_attributes_from_name("num")
            sql, params = schema_editor.column_sql(Author, new_field)
            self.assertEqual(sql, "INT64 NOT NULL")
            self.assertEqual(params, [])

    def test_column_sql_nullable_field(self):
        """
        Tests column sql for nullable field
        """
        with DatabaseSchemaEditor(self.connection) as schema_editor:
            schema_editor.execute = mock.MagicMock()
            new_field = IntegerField(null=True)
            new_field.set_attributes_from_name("num")
            sql, params = schema_editor.column_sql(Author, new_field)
            self.assertEqual(sql, "INT64")
            self.assertEqual(params, [])

    def test_column_add_index(self):
        """
        Tests column add index
        """
        with DatabaseSchemaEditor(self.connection) as schema_editor:
            schema_editor.execute = mock.MagicMock()
            index = Index(name="test_author_index_num", fields=["num"])
            schema_editor.add_index(Author, index)
            name, args, kwargs = schema_editor.execute.mock_calls[0]
            self.assertEqual(
                str(args[0]),
                "CREATE INDEX test_author_index_num ON tests_author (num)",
            )
            self.assertEqual(kwargs["params"], None)
            self.assertEqual(name, "")
        if HAS_OPENTELEMETRY_INSTALLED:
            span_list = self.ot_exporter.get_finished_spans()
            self.assertEqual(len(span_list), 1)
            self.assertSpanAttributes(
                "CloudSpannerDjango.add_index",
                attributes=dict(
                    BASE_ATTRIBUTES, model_name="tests_author", index="num",
                ),
                span=span_list[0],
            )

    def test_alter_field(self):
        """
        Tests altering existing field in table
        """
        with DatabaseSchemaEditor(self.connection) as schema_editor:
            schema_editor.execute = mock.MagicMock()
            old_field = IntegerField()
            old_field.set_attributes_from_name("num")
            new_field = IntegerField()
            new_field.set_attributes_from_name("author_num")
            schema_editor.alter_field(Author, old_field, new_field)

            schema_editor.execute.assert_called_once_with(
                "ALTER TABLE tests_author RENAME COLUMN num TO author_num"
            )

    def test_alter_field_change_null_with_single_index(self):
        """
        Tests altering nullability of field with single index
        """
        with DatabaseSchemaEditor(self.connection) as schema_editor:
            schema_editor.execute = mock.MagicMock()

            def delete_index_sql(*args, **kwargs):
                # Overriding Statement creation with sql string.
                return "DROP INDEX num_unique"

            def create_index_sql(*args, **kwargs):
                # Overriding Statement creation with sql string.
                return "CREATE INDEX tests_author ON tests_author (author_num)"

            def constraint_names(*args, **kwargs):
                return ["num_unique"]

            schema_editor._delete_index_sql = delete_index_sql
            schema_editor._create_index_sql = create_index_sql
            schema_editor._constraint_names = constraint_names
            old_field = IntegerField(null=True, db_index=True)
            old_field.set_attributes_from_name("num")
            new_field = IntegerField(db_index=True)
            new_field.set_attributes_from_name("author_num")
            schema_editor.alter_field(Author, old_field, new_field)

            calls = [
                mock.call("DROP INDEX num_unique"),
                mock.call(
                    "ALTER TABLE tests_author RENAME COLUMN num TO author_num"
                ),
                mock.call(
                    "ALTER TABLE tests_author ALTER COLUMN author_num INT64 NOT NULL",
                    [],
                ),
                mock.call(
                    "CREATE INDEX tests_author ON tests_author (author_num)"
                ),
            ]
            schema_editor.execute.assert_has_calls(calls)
        if HAS_OPENTELEMETRY_INSTALLED:
            span_list = self.ot_exporter.get_finished_spans()
            self.assertEqual(len(span_list), 3)
            self.assertSpanAttributes(
                "CloudSpannerDjango.alter_field.delete_index",
                attributes=dict(
                    BASE_ATTRIBUTES,
                    model_name="tests_author",
                    index_name="num_unique",
                    alter_field="num",
                ),
                span=span_list[0],
            )
            self.assertSpanAttributes(
                "CloudSpannerDjango.alter_field",
                attributes=dict(
                    BASE_ATTRIBUTES,
                    model_name="tests_author",
                    alter_field="num",
                ),
                span=span_list[1],
            )
            self.assertSpanAttributes(
                "CloudSpannerDjango.alter_field.recreate_index",
                attributes=dict(
                    BASE_ATTRIBUTES,
                    model_name="tests_author",
                    alter_field="author_num",
                ),
                span=span_list[2],
            )

    def test_alter_field_nullability_change_raise_not_support_error(self):
        """
        Tests altering nullability of existing field in table
        """
        with DatabaseSchemaEditor(self.connection) as schema_editor:
            schema_editor.execute = mock.MagicMock()

            def constraint_names(*args, **kwargs):
                return ["num_unique"]

            schema_editor._constraint_names = constraint_names
            old_field = IntegerField(null=True)
            old_field.set_attributes_from_name("num")
            new_field = IntegerField()
            new_field.set_attributes_from_name("author_num")
            with self.assertRaises(NotSupportedError):
                schema_editor.alter_field(Author, old_field, new_field)

    def test_alter_field_change_null_with_multiple_index_error(self):
        """
        Tests altering nullability of field with multiple index not supported
        """
        with DatabaseSchemaEditor(self.connection) as schema_editor:
            schema_editor.execute = mock.MagicMock()

            def constraint_names(*args, **kwargs):
                return ["num_unique", "dummy_index"]

            schema_editor._constraint_names = constraint_names
            old_field = IntegerField(null=True, db_index=True)
            old_field.set_attributes_from_name("num")
            new_field = IntegerField()
            new_field.set_attributes_from_name("author_num")
            with self.assertRaises(NotSupportedError):
                schema_editor.alter_field(Author, old_field, new_field)
