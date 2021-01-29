#!/bin/bash
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -eo pipefail

cd github/python-spanner-django

# Disable buffering, so that the logs stream through.
export PYTHONUNBUFFERED=1

# Debug: show build environment
env | grep KOKORO

# Setup service account credentials.
export GOOGLE_APPLICATION_CREDENTIALS=${KOKORO_GFILE_DIR}/service-account.json

# Setup project id.
export PROJECT_ID=$(cat "${KOKORO_GFILE_DIR}/project-id.json")
export GOOGLE_CLOUD_PROJECT=$(cat "${KOKORO_GFILE_DIR}/project-id.json")

# Remove old nox
python3.6 -m pip uninstall --yes --quiet nox-automation

# Install nox
python3.6 -m pip install --upgrade --quiet nox
python3.6 -m nox --version

# If NOX_SESSION is set, it only runs the specified session,
# otherwise run all the sessions.
if [[ -n "${NOX_SESSION:-}" ]]; then
    python3.6 -m nox -s "${NOX_SESSION:-}"
else
    python3.6 -m nox
fi

# Export essential environment variables for Django tests.
export RUNNING_SPANNER_BACKEND_TESTS=1

# The emulator is currently unusable for our tests because:
# a) It doesn't support INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE
# b) Cannot accept parameters whose types aren't known, so can't be used for
#    Python and other dynamic languages.
export USE_SPANNER_EMULATOR=0

pip3 install .
# Create a unique DJANGO_TESTS_DIR per worker to avoid
# any clashes with configured tests by other workers.
export DJANGO_TESTS_DIR="django_tests_dir"
mkdir -p $DJANGO_TESTS_DIR && git clone --depth 1 --single-branch --branch spanner-2.2.x https://github.com/timgraham/django.git $DJANGO_TESTS_DIR/django

# Install dependencies for Django tests.
sudo apt-get update
apt-get install -y libffi-dev libjpeg-dev zlib1g-dev libmemcached-dev
cd $DJANGO_TESTS_DIR/django && pip3 install -e . && pip3 install -r tests/requirements/py3.txt; cd ../../

# Not using the emulator!
# Hardcode the max number of workers since Spanner has a very low
# QPS for administrative RPCs of 5QPS (averaged every 100 seconds)
if [[ $KOKORO_JOB_NAME == *"continuous"* ]]
then
    # Disable continuous build as it creates too many Spanner instances
    # ("Quota exceeded for quota metric 'Instance create requests' and
    # limit 'Instance create requests per minute' of service
    # 'spanner.googleapis.com').
    export DJANGO_WORKER_COUNT=0
else
    export DJANGO_WORKER_COUNT=4
fi

./bin/parallelize_tests_linux
