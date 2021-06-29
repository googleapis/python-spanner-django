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



val="2.1"
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


@pytest.mark.django_db
class BenchmarkTestBase:
    """Base class for performance testing.
    Organizes testing data preparation and cleanup.
    """

    def __init__(self):
        self._create_table()

        self._one_row = (
            1,
            "Pete",
            "Allison",
            val,
        )

    def _cleanup(self):
        """Drop the test table."""
        conn = spanner_dbapi.connect("django-spanner-test", "spanner-testdb")
        conn.database.update_ddl(["DROP TABLE Author"])
        conn.close()

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

    def run(self):
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
        return measures


@pytest.mark.django_db
class SpannerBenchmarkTest(BenchmarkTestBase):
    """The original Spanner performace testing class."""
    def __init__(self):
        super().__init__()
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

@pytest.mark.django_db
class DjangoBenchmarkTest(BenchmarkTestBase):
    def __init__(self):
        setup_instance()
        setup_database()
        with connection.schema_editor() as editor:
            editor.create_model(Author)

        self._many_rows = []
        self._many_rows2 = []
        for i in range(99):
            self._many_rows.append(Author("Pete", "Allison", val))
            self._many_rows2.append(Author("Pete", "Allison", val))

    def _cleanup(self):
        """Drop the test table."""
        with connection.schema_editor() as editor:
            editor.delete_model(Author)

    def __del__(self):
        teardown_database()
        teardown_instance()

    @measure_execution_time
    def insert_one_row_with_fetch_after(self):
        author_kent = Author(
            first_name="Pete", last_name="Allison", rating=val,
        )
        author_kent.save()
        last_name = Author.objects.get(pk=author_kent.id).last_name
        if last_name != "Allison":
            raise ValueError("Received invalid last name: " + last_name)

    @measure_execution_time
    def insert_many_rows(self):
        Author.objects.bulk_create(self._many_rows)

    @measure_execution_time
    def insert_many_rows_with_mutations(self):
        pass

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


def compare_measurements(spanner, django):
    """
    Compare the original Spanner client performance measures
    with Spanner dialect for Django ones.
    """
    comparison = {}
    for key in django.keys():
        comparison[key] = {
            "Spanner, sec": spanner[key],
            "Django, sec": django[key],
            "Django deviation": round(django[key] - spanner[key], 2),
            "Django to Spanner, %": round(django[key] / spanner[key] * 100),
        }
    return comparison


measures = []
for _ in range(50):
    #spanner_measures = SpannerBenchmarkTest().run()
    django_measures = DjangoBenchmarkTest().run()
    #measures.append((spanner_measures, django_measures))

agg = {"spanner": {}, "django": {}}

for span, djan in measures:
    for key, value in span.items():
        #agg["spanner"].setdefault(key, []).append(value)
        agg["django"].setdefault(key, []).append(djan[key])

# spanner_stats = {}
# for key, value in agg["spanner"].items():
#     while 0 in value:
#         value.remove(0)
#     spanner_stats[key + "_aver"] = round(statistics.mean(value), 2)
#     spanner_stats[key + "_error"] = round(sem(value), 2)
#     spanner_stats[key + "_std_dev"] = round(statistics.pstdev(value), 2)

django_stats = {}
for key, value in agg["django"].items():
    while 0 in value:
        value.remove(0)
    django_stats[key + "_aver"] = round(statistics.mean(value), 2)
    django_stats[key + "_error"] = round(sem(value), 2)
    django_stats[key + "_std_dev"] = round(statistics.pstdev(value), 2)

# for key in spanner_stats:
#     print(key + ":")
#     print("spanner: ", spanner_stats[key])
#     print("django: ", django_stats[key])
    

