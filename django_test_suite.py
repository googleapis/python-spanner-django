#!/usr/bin/env python

import asyncio
import logging
import os
import subprocess
import time
from contextlib import contextmanager

from google.cloud.spanner_v1 import Client

logger = logging.getLogger(__name__)


def get_temp_dbname():
    return chr(ord("a") + time.time_ns() % 26) + os.urandom(10).hex()


TEST_DBNAME = os.getenv("SPANNER_TEST_DB", get_temp_dbname())
SETTINGS_FILE = "{}-settings".format(TEST_DBNAME)
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "emulator-test-project")
INSTANCE = os.getenv("SPANNER_TEST_INSTANCE", "django-tests")
TEST_APPS = os.getenv("DJANGO_TEST_APPS", "basic")


@contextmanager
def create_settings(name=SETTINGS_FILE):
    fname = '{}.py'.format(name)
    with open(fname, 'w') as fil:
        fil.write(
            """
DATABASES = {{
   'default': {{
       'ENGINE': 'django_spanner',
       'PROJECT': "{project}",
       'INSTANCE': "{instance}",
       'NAME': "{dbname}",
   }}
 }}
SECRET_KEY = 'spanner_tests_secret_key'
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]\
            """.format(project='emulator-test-project',
                       instance='google-cloud-django-backend-tests-8',
                       dbname='fakedbname'))
    yield name
    try:
        os.remove(fname)
    except Exception as ex:
        logger.warning("Failed to delete test settings file")
        logger.error(ex)


@contextmanager
def create_instance():
    client = Client(
        project=os.getenv("GOOGLE_CLOUD_PROJECT", "emulator-test-project")
    )

    instance = client.instance("google-cloud-django-backend-tests-8")
    try:
        yield instance.create().result()
    finally:
        try:
            instance.delete()
        except Exception as ex:
            logger.warning("Failed to destroy test instance")
            logger.error(ex)


async def run_tests(tests, emulator_host):
    with create_settings() as fname:
        with create_instance() as ins:
            subenv = os.environ.copy()
            subenv['SPANNER_EMULATOR_HOST'] = emulator_host
            return subprocess.call(
                [
                    "./runtests.py",
                    " ".join(tests),
                    "--verbosity=2",
                    "--noinput",
                    "--settings={}".format(fname),
                ],
                env=subenv
            )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(run_tests(["basic"], "localhost:9010")),
        # loop.create_task(run_tests(["admin_changelist"], "localhost:9011"))
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    asyncio.wait(tasks)
