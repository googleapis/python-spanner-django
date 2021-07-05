import datetime
import random
import statistics
import time
from decimal import Decimal
from typing import Any

from django.db import connection
from django.test import TransactionTestCase
from google.api_core.exceptions import Aborted
from google.cloud import spanner_dbapi
from google.cloud.spanner_v1 import Client, KeySet
from scipy.stats import sem

from tests.system.django_spanner.utils import (
    setup_database,
    setup_instance,
    teardown_database,
    teardown_instance,
)
import pytest


val = "2.1"
from tests.performance.django_spanner.models import Author


def measure_execution_time(function):
    """Decorator to measure a wrapped method execution time."""

    def wrapper(self, measures):
        """Execute the wrapped method and measure its execution time.
        Args:
            measures (dict): Test cases and their execution time.
        """
        t_start = time.time()
        try:
            function(self)
            measures[function.__name__] = round(time.time() - t_start, 2)
        except Aborted:
            measures[function.__name__] = 0

    return wrapper


def insert_one_row(transaction, one_row):
    """A transaction-function for the original Spanner client.
    Inserts a single row into a database and then fetches it back.
    """
    transaction.execute_update(
        "INSERT Author (id, first_name, last_name, rating) "
        " VALUES {}".format(str(one_row))
    )
    last_name = transaction.execute_sql(
        "SELECT last_name FROM Author WHERE id=1"
    ).one()[0]
    if last_name != "Allison":
        raise ValueError("Received invalid last name: " + last_name)


def insert_many_rows(transaction, many_rows):
    """A transaction-function for the original Spanner client.
    Insert 100 rows into a database.
    """
    statements = []
    for row in many_rows:
        statements.append(
            "INSERT Author (id, first_name, last_name, rating) "
            " VALUES {}".format(str(row))
        )
    _, count = transaction.batch_update(statements)
    if sum(count) != 99:
        raise ValueError("Wrong number of inserts: " + str(sum(count)))


class DjangoBenchmarkTest(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        setup_instance()
        setup_database()
        with connection.schema_editor() as editor:
            # Create the tables
            editor.create_model(Author)

    @classmethod
    def tearDownClass(cls):
        with connection.schema_editor() as editor:
            # delete the table
            editor.delete_model(Author)
        teardown_database()
        # teardown_instance()

    def setUp(self):
        self._many_rows = []
        self._many_rows2 = []
        for i in range(99):
            num = round(random.random() * 1000000)
            self._many_rows.append(Author(num, "Pete", "Allison", val))
            num2 = round(random.random() * 1000000)
            self._many_rows2.append(Author(num2, "Pete", "Allison", val))

    @measure_execution_time
    def insert_one_row_with_fetch_after(self):
        author_kent = Author(
            id=2,
            first_name="Pete",
            last_name="Allison",
            rating=val,
        )
        author_kent.save()
        last_name = Author.objects.get(pk=author_kent.id).last_name
        if last_name != "Allison":
            raise ValueError("Received invalid last name: " + last_name)

    @measure_execution_time
    def insert_many_rows(self):
        for row in self._many_rows:
            row.save()

    @measure_execution_time
    def insert_many_rows_with_mutations(self):
        Author.objects.bulk_create(self._many_rows2)

    @measure_execution_time
    def read_one_row(self):
        row = Author.objects.all().first()
        if row is None:
            raise ValueError("No rows read")

    @measure_execution_time
    def select_many_rows(self):
        rows = Author.objects.all()
        if len(rows) != 100:
            raise ValueError("Wrong number of rows read")

    def test_run(self):
        """Execute every test case."""
        measures = {}
        for method in (
            self.insert_one_row_with_fetch_after,
            self.read_one_row,
            self.insert_many_rows,
            self.select_many_rows,
            self.insert_many_rows_with_mutations,
        ):
            method(measures)
        import pdb
        pdb.set_trace()
        return measures


class SpannerBenchmarkTest(TransactionTestCase):
    """The original Spanner performace testing class."""
    def setUp(self):
        self._create_table()
        self._one_row = (
            1,
            "Pete",
            "Allison",
            val,
        )
        self._client = Client()
        self._instance = self._client.instance("django-spanner-test")
        self._database = self._instance.database("spanner-testdb")

        self._many_rows = []
        self._many_rows2 = []
        for i in range(99):
            num = round(random.random() * 1000000)
            self._many_rows.append((num, "Pete", "Allison", val))
            num2 = round(random.random() * 1000000)
            self._many_rows2.append((num2, "Pete", "Allison", val))

        # initiate a session
        with self._database.snapshot():
            pass
    def _create_table(self):
        """Create a table for performace testing."""
        conn = spanner_dbapi.connect("django-spanner-test", "spanner-testdb")
        conn.database.update_ddl(
            [
                """
CREATE TABLE Author (
    id INT64,
    first_name STRING(20),
    last_name STRING(20),
    rating STRING(50),
) PRIMARY KEY (id)
        """
            ]
        ).result(120)

        conn.close()

    @measure_execution_time
    def insert_one_row_with_fetch_after(self):
        self._database.run_in_transaction(insert_one_row, self._one_row)

    @measure_execution_time
    def insert_many_rows(self):
        self._database.run_in_transaction(insert_many_rows, self._many_rows)

    @measure_execution_time
    def insert_many_rows_with_mutations(self):
        with self._database.batch() as batch:
            batch.insert(
                table="Author",
                columns=("id", "first_name", "last_name", "rating"),
                values=self._many_rows2,
            )

    @measure_execution_time
    def read_one_row(self):
        with self._database.snapshot() as snapshot:
            keyset = KeySet(all_=True)
            snapshot.read(
                table="Author",
                columns=("id", "first_name", "last_name", "rating"),
                keyset=keyset,
            ).one()

    @measure_execution_time
    def select_many_rows(self):
        with self._database.snapshot() as snapshot:
            rows = list(
                snapshot.execute_sql("SELECT * FROM Author ORDER BY last_name")
            )
            if len(rows) != 100:
                raise ValueError("Wrong number of rows read")

    def _cleanup(self):
        """Drop the test table."""
        conn = spanner_dbapi.connect("django-spanner-test", "spanner-testdb")
        conn.database.update_ddl(["DROP TABLE Author"])
        conn.close()

    def test_run(self):
        """Execute every test case."""
        measures = {}
        for method in (
            self.insert_one_row_with_fetch_after,
            self.read_one_row,
            self.insert_many_rows,
            self.select_many_rows,
            self.insert_many_rows_with_mutations,
        ):
            method(measures)
        self._cleanup()
        # import pdb
        # pdb.set_trace()
        return measures


    

#print(DjangoBenchmarkTest().test_run())
