# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

import unittest

# Copyright 2016 Google LLC All rights reserved.
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

import os

from google.api_core import exceptions

from google.cloud.spanner import Client
from google.cloud.spanner import BurstyPool
from google.cloud.spanner_dbapi.connection import Connection

from test_utils.retry import RetryErrors
from test_utils.system import unique_resource_id


CREATE_INSTANCE = (
    os.getenv("GOOGLE_CLOUD_TESTS_CREATE_SPANNER_INSTANCE") is not None
)

if CREATE_INSTANCE:
    INSTANCE_ID = "google-cloud" + unique_resource_id("-")
else:
    INSTANCE_ID = os.environ.get(
        "GOOGLE_CLOUD_TESTS_SPANNER_INSTANCE", "google-cloud-python-systest"
    )
EXISTING_INSTANCES = []

DDL_STATEMENTS = (
    """CREATE TABLE contacts (
            contact_id INT64,
            first_name STRING(1024),
            last_name STRING(1024),
            email STRING(1024)
        )
        PRIMARY KEY (contact_id)""",
)


class Config(object):
    """Run-time configuration to be modified at set-up.

    This is a mutable stand-in to allow test set-up to modify
    global state.
    """

    CLIENT = None
    INSTANCE_CONFIG = None
    INSTANCE = None


def _list_instances():
    return list(Config.CLIENT.list_instances())


def setUpModule():
    Config.CLIENT = Client()
    retry = RetryErrors(exceptions.ServiceUnavailable)

    configs = list(retry(Config.CLIENT.list_instance_configs)())

    instances = retry(_list_instances)()
    EXISTING_INSTANCES[:] = instances

    if CREATE_INSTANCE:
        configs = [config for config in configs if "-us-" in config.name]

        if not configs:
            raise ValueError("List instance configs failed in module set up.")

        Config.INSTANCE_CONFIG = configs[0]
        config_name = configs[0].name

        Config.INSTANCE = Config.CLIENT.instance(INSTANCE_ID, config_name)
        created_op = Config.INSTANCE.create()
        created_op.result(30)  # block until completion
    else:
        Config.INSTANCE = Config.CLIENT.instance(INSTANCE_ID)
        Config.INSTANCE.reload()


def tearDownModule():
    if CREATE_INSTANCE:
        Config.INSTANCE.delete()


class TestTransactionsManagement(unittest.TestCase):
    DATABASE_NAME = "db-api-transactions-management"

    @classmethod
    def setUpClass(cls):
        cls._db = Config.INSTANCE.database(
            cls.DATABASE_NAME,
            ddl_statements=DDL_STATEMENTS,
            pool=BurstyPool(labels={"testcase": "database_api"}),
        )
        cls._db.create().result(30)  # raises on failure / timeout.

    @classmethod
    def tearDownClass(cls):
        cls._db.drop()

    def tearDown(self):
        with self._db.snapshot() as snapshot:
            snapshot.execute_sql("DELETE FROM contacts WHERE true")

    def test_commit(self):
        want_row = (
            1,
            "updated-first-name",
            "last-name",
            "test.email_updated@domen.ru",
        )
        # connecting to the test database
        conn = Connection(Config.INSTANCE, self._db)
        conn.autocommit = False
        cursor = conn.cursor()

        # executing several DML statements with one transaction
        cursor.execute(
            """
INSERT INTO contacts (contact_id, first_name, last_name, email)
VALUES (1, 'first-name', 'last-name', 'test.email@domen.ru')
        """
        )
        cursor.execute(
            """
UPDATE contacts
SET first_name = 'updated-first-name'
WHERE first_name = 'first-name'
"""
        )
        cursor.execute(
            """
UPDATE contacts
SET email = 'test.email_updated@domen.ru'
WHERE email = 'test.email@domen.ru'
"""
        )
        conn.commit()

        # reading the resulting data from the database
        cursor.execute("SELECT * FROM contacts")
        got_rows = cursor.fetchall()
        conn.commit()

        self.assertEqual(got_rows, [want_row])
