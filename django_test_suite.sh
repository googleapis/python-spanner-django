#!/bin/sh

# Copyright 2020 Google LLC
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

# exit when any command fails
set -e

# If no SPANNER_TEST_DB is set, generate a unique one
# so that we can have multiple tests running without
# conflicting which changes and constraints. We'll always
# cleanup the created database.
TEST_DBNAME=${SPANNER_TEST_DB:-$(python3 -c 'import os, time; print(chr(ord("a") + time.time_ns() % 26)+os.urandom(10).hex())')}
TEST_DBNAME_OTHER="$TEST_DBNAME-ot"
TEST_APPS=${DJANGO_TEST_APPS:-basic}
INSTANCE=${SPANNER_TEST_INSTANCE:-django-tests}
PROJECT=${PROJECT_ID:-appdev-soda-spanner-staging}
SETTINGS_FILE="$TEST_DBNAME-settings"
TESTS_DIR=${DJANGO_TESTS_DIR:-django_tests}

create_settings() {
    cat << ! > "$SETTINGS_FILE.py"
DATABASES = {
   'default': {
       'ENGINE': 'django_spanner',
       'PROJECT': "$PROJECT",
       'INSTANCE': "$INSTANCE",
       'NAME': "$TEST_DBNAME",
   },
   'other': {
       'ENGINE': 'django_spanner',
       'PROJECT': "$PROJECT",
       'INSTANCE': "$INSTANCE",
       'NAME': "$TEST_DBNAME_OTHER",
   },
}
SECRET_KEY = 'spanner_tests_secret_key'
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
!
}

setup_emulator_if_needed() {
    if [[ $SPANNER_EMULATOR_HOST != "" ]]
    then
        echo "Running the emulator at: $SPANNER_EMULATOR_HOST"
        ./emulator_main --host_port "$SPANNER_EMULATOR_HOST" &
        SPANNER_INSTANCE=$INSTANCE python3 .kokoro/ensure_instance_exists.py
    fi
}

run_django_tests() {
    cd $TESTS_DIR/django/tests
    create_settings
    echo -e "\033[32mRunning Django tests: $TEST_APPS\033[00m"
    python3 runtests.py $TEST_APPS --verbosity=2 --noinput --settings $SETTINGS_FILE
}

setup_emulator_if_needed
run_django_tests
