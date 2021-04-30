# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

import sys
import unittest

from django.test import TestCase
from django_spanner.schema import DatabaseSchemaEditor
from django.test.utils import CaptureQueriesContext
from django.db.models.fields import IntegerField
from .models import Author
from django.conf import settings
from django.db import DatabaseError
from google.cloud.spanner_v1 import Client
from google.cloud.spanner_v1.database import Database


@unittest.skipIf(
    sys.version_info < (3, 6), reason="Skipping Python versions <= 3.5"
)
class TestUtils(TestCase):
    @classmethod
    def setUpClass(cls):
        test_settings = settings.__dict__["_wrapped"].__dict__
        client = Client(project=test_settings["PROJECT"])
        instance = client.instance(
            test_settings["INSTANCE"], test_settings["INSTANCE_CONFIG"]
        )
        if not instance.exists():
            created_op = instance.create()
            created_op.result(120)  # block until completion
        db = Database(test_settings["NAME"], instance)
        db.create()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        test_settings = settings.__dict__["_wrapped"].__dict__
        client = Client(project=test_settings["PROJECT"])
        instance = client.instance(
            test_settings["INSTANCE"], test_settings["INSTANCE_CONFIG"]
        )
        if instance.exists():
            instance.delete()
        super().tearDownClass()

    def _get_target_class(self):
        from django_spanner.base import DatabaseWrapper

        return DatabaseWrapper

    def _make_one(self, *args, **kwargs):
        """
        Returns a connection to the database provided in settings.
        """
        test_settings = settings.__dict__["_wrapped"].__dict__
        return self._get_target_class()(settings_dict=test_settings)

    def _column_classes(self, connection, model):
        """
        Returns a dictionary mapping of columns in given model.
        """
        with connection.cursor() as cursor:
            columns = {
                d[0]: (connection.introspection.get_field_type(d[1], d), d)
                for d in connection.introspection.get_table_description(
                    cursor, model._meta.db_table,
                )
            }
        return columns

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

    def test_creation_deletion(self):
        """
        Tries creating a model's table, and then deleting it.
        """
        connection = self._make_one()
        with connection.schema_editor() as schema_editor:
            # Create the table
            schema_editor.create_model(Author)
            schema_editor.execute("select 1")
            # The table is there
            list(Author.objects.all())
            # Clean up that table
            schema_editor.delete_model(Author)
            schema_editor.execute("select 1")
            # No deferred SQL should be left over.
            self.assertEqual(schema_editor.deferred_sql, [])
        # The table is gone
        with self.assertRaises(DatabaseError):
            list(Author.objects.all())

    def test_add_field(self):
        """
        Tests adding fields to models
        """

        connection = self._make_one()

        # Create the table
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(Author)
            schema_editor.execute("select 1")
        # Ensure there's no age field
        columns = self._column_classes(connection, Author)
        self.assertNotIn("age", columns)
        # Add the new field
        new_field = IntegerField(null=True)
        new_field.set_attributes_from_name("age")
        with CaptureQueriesContext(
            connection
        ) as ctx, connection.schema_editor() as editor:
            editor.add_field(Author, new_field)
        drop_default_sql = editor.sql_alter_column_no_default % {
            "column": editor.quote_name(new_field.name),
        }
        self.assertFalse(
            any(
                drop_default_sql in query["sql"]
                for query in ctx.captured_queries
            )
        )
        # Ensure the field is right afterwards
        columns = self._column_classes(connection, Author)
        self.assertEqual(columns["age"][0], "IntegerField")
        self.assertEqual(columns["age"][1][6], True)

        # Delete the table
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(Author)
            schema_editor.execute("select 1")
