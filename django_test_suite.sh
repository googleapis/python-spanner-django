#!/bin/sh

# Copyright (c) 2020 Google LLC. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

set -x pipefail

# Disable buffering, so that the logs stream through.
export PYTHONUNBUFFERED=1

sudo apt-get update -y
sudo apt-get install -y libmemcached-dev

pip3 install .
pip3 uninstall -y google-cloud-spanner
pip3 uninstall -y django-google-spanner
pip3 install -e 'git+https://github.com/q-logic/python-spanner.git@autocommit_change#egg=google-cloud-spanner'
pip3 install -e 'git+https://github.com/q-logic/python-spanner-django.git@dj_tests_against_emulator#egg=django-google-spanner'

export DJANGO_TESTS_DIR="django_tests_dir"
mkdir -p $DJANGO_TESTS_DIR && git clone --depth 1 --single-branch --branch spanner-2.2.x https://github.com/timgraham/django.git $DJANGO_TESTS_DIR/django

# Install dependencies for Django tests.
sudo apt-get update
sudo apt-get install -y libffi-dev libjpeg-dev zlib1g-devel

cd $DJANGO_TESTS_DIR/django && pip3 install -e . && pip3 install -r tests/requirements/py3.txt; cd ../../

python3 create_test_instance.py

# If no SPANNER_TEST_DB is set, generate a unique one
# so that we can have multiple tests running without
# conflicting which changes and constraints. We'll always
# cleanup the created database.
TEST_DBNAME=${SPANNER_TEST_DB:-$(python3 -c 'import os, time; print(chr(ord("a") + time.time_ns() % 26)+os.urandom(10).hex())')}
TEST_DBNAME_OTHER="$TEST_DBNAME-ot"
TEST_APPS=${DJANGO_TEST_APPS:-basic}
INSTANCE=${SPANNER_TEST_INSTANCE:-django-tests}
PROJECT=${PROJECT_ID}
SPANNER_EMULATOR_HOST=${SPANNER_EMULATOR_HOST}
GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}
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

cd $TESTS_DIR/django/tests
create_settings
python3 runtests.py admin_changelist admin_docs admin_filters admin_inlines admin_ordering admin_utils admin_views aggregation aggregation_regress annotations auth_tests backends basic bulk_create cache choices constraints contenttypes_tests custom_columns custom_lookups custom_managers custom_methods custom_pk datatypes dates datetimes db_functions defer defer_regress delete delete_regress distinct_on_fields empty expressions expressions_case expressions_window extra_regress field_defaults file_storage file_uploads filtered_relation fixtures fixtures_model_package fixtures_regress flatpages_tests force_insert_update foreign_object forms_tests from_db_value generic_inline_admin generic_relations generic_relations_regress generic_views get_earliest_or_latest get_object_or_404 get_or_create i18n indexes inline_formsets inspectdb introspection invalid_models_tests known_related_objects lookup m2m_and_m2o m2m_intermediary m2m_multiple m2m_recursive m2m_regress m2m_signals m2m_through m2m_through_regress m2o_recursive managers_regress many_to_many many_to_one many_to_one_null max_lengths migrate_signals migrations migration_test_data_persistence modeladmin model_fields model_forms model_formsets model_formsets_regress model_indexes model_inheritance model_inheritance_regress model_options model_package model_regress multiple_database mutually_referential nested_foreign_keys null_fk null_fk_ordering null_queries one_to_one ordering order_with_respect_to or_lookups prefetch_related proxy_model_inheritance proxy_models queries queryset_pickle raw_query redirects_tests reserved_names reverse_lookup save_delete_hooks schema select_for_update select_related select_related_onetoone select_related_regress serializers servers sessions_tests signals sitemaps_tests sites_framework sites_tests string_lookup syndication_tests test_client test_client_regress test_runner test_utils timezones transaction_hooks transactions unmanaged_models update update_only_fields validation view_tests --verbosity=3 --noinput --settings $SETTINGS_FILE
