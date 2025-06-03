# Copyright 2025 Google LLC All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from google.cloud.spanner_v1 import (
    BatchCreateSessionsRequest,
    ExecuteSqlRequest, CommitRequest,
)
from tests.mockserver_tests.mock_server_test_base import (
    MockServerTestBase,
    add_select1_result,
    add_singer_query_result, add_update_count,
)
from django.db import connection, models

from tests.mockserver_tests.models import Singer
from tests.settings import DATABASES


class TestBasics(MockServerTestBase):
    def verify_select1(self, results):
        result_list = []
        for row in results:
            result_list.append(row)
            self.assertEqual(row[0], 1)
        self.assertEqual(len(result_list), 1)
        requests = self.spanner_service.requests
        self.assertEqual(len(requests), 2)
        self.assertIsInstance(requests[0], BatchCreateSessionsRequest)
        self.assertIsInstance(requests[1], ExecuteSqlRequest)

    def test_select1(self):
        add_select1_result()
        with self.database.snapshot() as snapshot:
            results = snapshot.execute_sql("select 1")
            self.verify_select1(results)

    def test_django_select1(self):
        add_select1_result()
        with connection.cursor() as cursor:
            cursor.execute("select 1")
            self.verify_select1(cursor.fetchall())

    def test_django_select_singer(self):
        add_singer_query_result(
            "SELECT tests_singer.id, tests_singer.first_name, tests_singer.last_name FROM tests_singer"
        )
        singers = Singer.objects.all()
        self.assertEqual(len(singers), 2)
        requests = self.spanner_service.requests
        self.assertEqual(len(requests), 2)
        self.assertIsInstance(requests[0], BatchCreateSessionsRequest)
        self.assertIsInstance(requests[1], ExecuteSqlRequest)

    def test_django_select_singer_using_other_db(self):
        add_singer_query_result(
            "SELECT tests_singer.id, tests_singer.first_name, tests_singer.last_name FROM tests_singer"
        )
        singers = Singer.objects.using("secondary").all()
        self.assertEqual(len(singers), 2)
        requests = self.spanner_service.requests
        self.assertEqual(len(requests), 2)
        self.assertIsInstance(requests[0], BatchCreateSessionsRequest)
        self.assertIsInstance(requests[1], ExecuteSqlRequest)

    def test_insert_singer(self):
        add_update_count(
            "INSERT INTO tests_singer "
            "(id, first_name, last_name) "
            "VALUES (@a0, @a1, @a2)",
            1)
        singer = Singer(first_name="test", last_name="test")
        singer.save()
        requests = self.spanner_service.requests
        self.assertEqual(len(requests), 3)
        self.assertIsInstance(requests[0], BatchCreateSessionsRequest)
        self.assertIsInstance(requests[1], ExecuteSqlRequest)
        self.assertIsInstance(requests[2], CommitRequest)
        # The ExecuteSqlRequest should have 3 parameters:
        # 1. first_name
        # 2. last_name
        # 3. client-side auto-generated primary key
        self.assertEqual(len(requests[1].params), 3)

    def test_insert_singer_with_disabled_random_primary_key(self):
        for db, config in DATABASES.items():
            if config["ENGINE"] == "django_spanner":
                config["DISABLE_RANDOM_ID_GENERATION"] = "true"

        # Define a class locally in this test method to ensure that
        # it is initialized after disabling random ID generation.
        class LocalSinger(models.Model):
            first_name = models.CharField(max_length=200)
            last_name = models.CharField(max_length=200)

        try:
            add_update_count(
                "INSERT INTO tests_localsinger "
                "(first_name, last_name) "
                "VALUES (@a0, @a1)",
                1)
            singer = LocalSinger(first_name="test", last_name="test")
            singer.save()
            requests = self.spanner_service.requests
            self.assertEqual(len(requests), 3)
            self.assertIsInstance(requests[0], BatchCreateSessionsRequest)
            self.assertIsInstance(requests[1], ExecuteSqlRequest)
            self.assertIsInstance(requests[2], CommitRequest)
            # The ExecuteSqlRequest should have 2 parameters:
            # 1. first_name
            # 2. last_name
            # There should be no client-side auto-generated primary key.
            self.assertEqual(len(requests[1].params), 2)
        finally:
            for db, config in DATABASES.items():
                if config["ENGINE"] == "django_spanner":
                    config.pop("DISABLE_RANDOM_ID_GENERATION", None)
