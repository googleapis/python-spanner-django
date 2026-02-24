# flake8: noqa: E402
# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

import datetime
import os
import django

# Monkey-patch AutoField to generate a random value since Cloud Spanner can't
# do that.
from uuid import uuid4

RANDOM_ID_GENERATION_ENABLED_SETTING = "RANDOM_ID_GENERATION_ENABLED"


from django.db import DEFAULT_DB_ALIAS  # noqa: E402
from google.cloud.spanner_v1 import JsonObject  # noqa: E402
from django.db.models.fields import (  # noqa: E402
    NOT_PROVIDED,
    AutoField,
    Field,
)

from .functions import register_functions  # noqa: E402
from .lookups import register_lookups  # noqa: E402
from .utils import check_django_compatability  # noqa: E402
from .version import __version__  # noqa: E402

# Monkey-patch google.DatetimeWithNanoseconds's __eq__ compare against
# datetime.datetime.
from google.api_core.datetime_helpers import (
    DatetimeWithNanoseconds,
)  # noqa: E402


from django.db.models.fields import (  # noqa: E402
    SmallAutoField,
    BigAutoField,
)
from django.db.models import JSONField  # noqa: E402

USE_EMULATOR = os.getenv("SPANNER_EMULATOR_HOST") is not None

SUPPORTED_DJANGO_VERSIONS = [(5, 2)]

check_django_compatability(SUPPORTED_DJANGO_VERSIONS)

__all__ = ["__version__", "USE_EMULATOR"]
register_functions()
register_lookups()


def gen_rand_int64():
    # Credit to https://stackoverflow.com/a/3530326.
    # Use 32-bit integer for Emulator compatibility (High-bit issues observed).
    return uuid4().int & 0xFFFFFFFF


def autofield_init(self, *args, **kwargs):
    kwargs["blank"] = True
    Field.__init__(self, *args, **kwargs)

    if getattr(self, "default", NOT_PROVIDED) == NOT_PROVIDED:
        self.default = gen_rand_int64


AutoField.__init__ = autofield_init
AutoField.db_returning = False
AutoField.validators = []

SmallAutoField.__init__ = autofield_init
BigAutoField.__init__ = autofield_init
SmallAutoField.db_returning = False
BigAutoField.db_returning = False
SmallAutoField.validators = []
BigAutoField.validators = []


def get_prep_value(self, value):
    # Json encoding and decoding for spanner is done in python-spanner.
    if not isinstance(value, JsonObject) and isinstance(value, dict):
        return JsonObject(value)

    return value


JSONField.get_prep_value = get_prep_value

old_datetimewithnanoseconds_eq = getattr(
    DatetimeWithNanoseconds, "__eq__", None
)


def datetimewithnanoseconds_eq(self, other):
    if old_datetimewithnanoseconds_eq:
        equal = old_datetimewithnanoseconds_eq(self, other)
        if equal:
            return True
        elif type(self) is type(other):
            return False

    # Otherwise try to convert them to an equvialent form.
    # See https://github.com/googleapis/python-spanner-django/issues/272
    if isinstance(other, datetime.datetime):
        return self.ctime() == other.ctime()

    return False


DatetimeWithNanoseconds.__eq__ = datetimewithnanoseconds_eq

# Retroactively patch existing AutoFields in registered models.
from django.apps import apps
try:
    for model in apps.get_models():
        for field in model._meta.fields:
            if isinstance(field, (AutoField, SmallAutoField, BigAutoField)):
                if getattr(field, "default", NOT_PROVIDED) == NOT_PROVIDED:
                    field.default = gen_rand_int64
except Exception:
    # App registry might not be ready yet.
    pass
