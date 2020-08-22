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

import os

from django.core import checks
from django.db.backends.base.validation import BaseDatabaseValidation
from django.db.models import DecimalField


class DatabaseValidation(BaseDatabaseValidation):

    def check_field_type(self, field, field_type):
        errors = []
        # Disable the error when running the Django test suite.
        if os.environ.get('RUNNING_SPANNER_BACKEND_TESTS') != '1' and isinstance(field, DecimalField):
            errors.append(
                checks.Error(
                    'DecimalField is not yet supported by Spanner.',
                    obj=field,
                    id='spanner.E001',
                )
            )
        return errors
