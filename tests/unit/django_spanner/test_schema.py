# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

import sys
import unittest

from django.test import SimpleTestCase
from django_spanner.schema import DatabaseSchemaEditor
from django.db.models.fields import IntegerField
from django.db.models import Index
from .models import Author
from unittest import mock


@unittest.skipIf(
    sys.version_info < (3, 6), reason="Skipping Python versions <= 3.5"
)
class TestUtils(SimpleTestCase):
    def _get_target_class(self):
        from django_spanner.base import DatabaseWrapper

        return DatabaseWrapper

    def _make_one(self, *args, **kwargs):
        """
        Returns a connection to the database provided in settings.
        """
        dummy_settings = {"dummy_param": "dummy"}
        return self._get_target_class()(settings_dict=dummy_settings)

    # Tests
    def test_quote_value(self):
        """
        Tries quoting input value.
        """
        db_wrapper = self._make_one()
        schema_editor = DatabaseSchemaEditor(db_wrapper)
        self.assertEqual(schema_editor.quote_value(value=1.1), "1.1")

    def test_skip_default(self):
        """
        Tries skipping default as Cloud spanner doesn't support it.
        """
        db_wrapper = self._make_one()
        schema_editor = DatabaseSchemaEditor(db_wrapper)
        self.assertTrue(schema_editor.skip_default(field=None))

    def test_create_model(self):
        """
        Tries creating a model's table.
        """
        connection = self._make_one()

        with DatabaseSchemaEditor(connection) as schema_editor:
            schema_editor.execute = mock.MagicMock()
            schema_editor.create_model(Author)

            schema_editor.execute.assert_called_once_with(
                "CREATE TABLE tests_author (id INT64 NOT NULL, name STRING(40) "
                + "NOT NULL, last_name STRING(40) NOT NULL, num INT64 NOT "
                + "NULL, created TIMESTAMP NOT NULL, modified TIMESTAMP) "
                + "PRIMARY KEY(id)",
                None,
            )

    def test_delete_model(self):
        """
        Tests deleting a model
        """
        connection = self._make_one()

        with DatabaseSchemaEditor(connection) as schema_editor:
            schema_editor.execute = mock.MagicMock()
            schema_editor._constraint_names = mock.MagicMock()
            schema_editor.delete_model(Author)

            schema_editor.execute.assert_called_once_with(
                "DROP TABLE tests_author",
            )

    def test_add_field(self):
        """
        Tests adding fields to models
        """
        connection = self._make_one()

        with DatabaseSchemaEditor(connection) as schema_editor:
            schema_editor.execute = mock.MagicMock()
            new_field = IntegerField(null=True)
            new_field.set_attributes_from_name("age")
            schema_editor.add_field(Author, new_field)

            schema_editor.execute.assert_called_once_with(
                "ALTER TABLE tests_author ADD COLUMN age INT64", []
            )

    def test_column_sql_not_null_field(self):
        """
        Tests column sql for not null field
        """
        connection = self._make_one()

        with DatabaseSchemaEditor(connection) as schema_editor:
            schema_editor.execute = mock.MagicMock()
            new_field = IntegerField()
            new_field.set_attributes_from_name("num")
            sql, params = schema_editor.column_sql(Author, new_field)
            self.assertEqual(sql, "INT64 NOT NULL")

    def test_column_sql_nullable_field(self):
        """
        Tests column sql for nullable field
        """
        connection = self._make_one()

        with DatabaseSchemaEditor(connection) as schema_editor:
            schema_editor.execute = mock.MagicMock()
            new_field = IntegerField(null=True)
            new_field.set_attributes_from_name("num")
            sql, params = schema_editor.column_sql(Author, new_field)
            self.assertEqual(sql, "INT64")

    def test_column_add_index(self):
        """
        Tests column add index
        """
        connection = self._make_one()

        with DatabaseSchemaEditor(connection) as schema_editor:
            schema_editor.execute = mock.MagicMock()
            index = Index(name="test_author_index_num", fields=["num"])
            schema_editor.add_index(Author, index)
            name, args, kwargs = schema_editor.execute.mock_calls[0]

            self.assertEqual(
                str(args[0]),
                "CREATE INDEX test_author_index_num ON tests_author (num)",
            )
            self.assertEqual(kwargs["params"], None)

    def test_alter_field(self):
        """
        Tests altering existing field in table
        """
        connection = self._make_one()

        with DatabaseSchemaEditor(connection) as schema_editor:
            schema_editor.execute = mock.MagicMock()
            old_field = IntegerField()
            old_field.set_attributes_from_name("num")
            new_field = IntegerField()
            new_field.set_attributes_from_name("author_num")
            schema_editor.alter_field(Author, old_field, new_field)

            schema_editor.execute.assert_called_once_with(
                "ALTER TABLE tests_author RENAME COLUMN num TO author_num"
            )
