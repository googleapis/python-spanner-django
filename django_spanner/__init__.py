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
from enum import Enum

import pkg_resources
from google.cloud.spanner_v1 import JsonObject
from django.db import (
    connection as connection_db,
    connections,
    transaction,
)
from django.db.models.fields import (
    AutoField,
    Field,
)
from django.db.models.query import QuerySet
from django.utils.functional import partition
from django.contrib.contenttypes.models import ContentType

from .expressions import register_expressions
from .functions import register_functions
from .lookups import register_lookups
from .utils import check_django_compatability

# Monkey-patch google.DatetimeWithNanoseconds's __eq__ compare against
# datetime.datetime.
from google.api_core.datetime_helpers import DatetimeWithNanoseconds


USING_DJANGO_3 = False
if django.VERSION[:2] == (3, 2):
    USING_DJANGO_3 = True

if USING_DJANGO_3:
    from django.db.models.fields import (
        SmallAutoField,
        BigAutoField,
    )
    from django.db.models import JSONField

__version__ = pkg_resources.get_distribution("django-google-spanner").version

USE_EMULATOR = os.getenv("SPANNER_EMULATOR_HOST") is not None

# Only active LTS django versions (2.2.*, 3.2.*) are supported by this library right now.
SUPPORTED_DJANGO_VERSIONS = [(2, 2), (3, 2)]

check_django_compatability(SUPPORTED_DJANGO_VERSIONS)
register_expressions(USING_DJANGO_3)
register_functions()
register_lookups()


class OnConflict(Enum):
    IGNORE = "ignore"
    UPDATE = "update"


def spanner_bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
    """
    Insert each of the instances into the database. Do *not* call
    save() on each of the instances, do not send any pre/post_save
    signals, and do not set the primary key attribute if it is an
    autoincrement field (except if features.can_return_rows_from_bulk_insert=True).
    Multi-table models are not supported.
    """
    # When you bulk insert you don't get the primary keys back (if it's an
    # autoincrement, except if can_return_rows_from_bulk_insert=True), so
    # you can't insert into the child tables which references this. There
    # are two workarounds:
    # 1) This could be implemented if you didn't have an autoincrement pk
    # 2) You could do it by doing O(n) normal inserts into the parent
    #    tables to get the primary keys back and then doing a single bulk
    #    insert into the childmost table.
    # We currently set the primary keys on the objects when using
    # PostgreSQL via the RETURNING ID clause. It should be possible for
    # Oracle as well, but the semantics for extracting the primary keys is
    # trickier so it's not done yet.
    if batch_size is not None and batch_size <= 0:
        raise ValueError("Batch size must be a positive integer.")
    # Check that the parents share the same concrete model with the our
    # model to detect the inheritance pattern ConcreteGrandParent ->
    # MultiTableParent -> ProxyChild. Simply checking self.model._meta.proxy
    # would not identify that case as involving multiple tables.
    for parent in self.model._meta.get_parent_list():
        if parent._meta.concrete_model is not self.model._meta.concrete_model:
            raise ValueError("Can't bulk create a multi-table inherited model")
    if not objs:
        return objs

    self._for_write = True
    connection = connections[self.db]
    opts = self.model._meta
    fields = opts.concrete_fields
    objs = list(objs)
    self._prepare_for_bulk_create(objs)

    batch_size = connection_db.features.max_query_params

    with transaction.atomic(using=self.db, savepoint=False):
        objs_with_pk, objs_without_pk = partition(lambda o: o.pk is None, objs)
        if objs_with_pk:
            for chunk_with_pk in [
                objs_with_pk[x : x + batch_size]
                for x in range(0, len(objs_with_pk), batch_size)
            ]:
                returned_columns = self._batched_insert(
                    chunk_with_pk,
                    fields,
                    batch_size,
                    ignore_conflicts=ignore_conflicts,
                )
                for obj_with_pk, results in zip(
                    chunk_with_pk, returned_columns
                ):
                    for result, field in zip(
                        results, opts.db_returning_fields
                    ):
                        if field != opts.pk:
                            setattr(obj_with_pk, field.attname, result)

                for obj_with_pk in chunk_with_pk:
                    obj_with_pk._state.adding = False
                    obj_with_pk._state.db = self.db

        if objs_without_pk:
            fields = [f for f in fields if not isinstance(f, AutoField)]
            returned_columns = self._batched_insert(
                objs_without_pk,
                fields,
                batch_size,
                ignore_conflicts=ignore_conflicts,
            )
            if (
                connection.features.can_return_rows_from_bulk_insert
                and not ignore_conflicts
            ):
                assert len(returned_columns) == len(objs_without_pk)
            for obj_without_pk, results in zip(
                objs_without_pk, returned_columns
            ):
                for result, field in zip(results, opts.db_returning_fields):
                    setattr(obj_without_pk, field.attname, result)
                obj_without_pk._state.adding = False
                obj_without_pk._state.db = self.db

    return objs


def spanner_prepare_for_bulk_create(self, objs):
    for obj in objs:
        if obj.pk is None:
            # Populate new PK values.
            obj.pk = obj._meta.pk.get_pk_value_on_save(obj)

        obj._prepare_related_fields_for_save(operation_name="bulk_create")


def spanner_prepare_related_fields_for_save(self, operation_name, fields=None):
    # Ensure that a model instance without a PK hasn't been assigned to
    # a ForeignKey, GenericForeignKey or OneToOneField on this model. If
    # the field is nullable, allowing the save would result in silent data
    # loss.
    for field in self._meta.concrete_fields:
        if fields and field not in fields:
            continue
        # If the related field isn't cached, then an instance hasn't been
        # assigned and there's no need to worry about this check.
        if field.is_relation and field.is_cached(self):
            obj = getattr(self, field.name, None)
            if not obj:
                continue
            # A pk may have been assigned manually to a model instance not
            # saved to the database (or auto-generated in a case like
            # UUIDField), but we allow the save to proceed and rely on the
            # database to raise an IntegrityError if applicable. If
            # constraints aren't supported by the database, there's the
            # unavoidable risk of data corruption.
            if obj.pk is None:
                # Remove the object from a related instance cache.
                if not field.remote_field.multiple:
                    field.remote_field.delete_cached_value(obj)
                raise ValueError(
                    "%s() prohibited to prevent data loss due to unsaved "
                    "related object '%s'." % (operation_name, field.name)
                )
            elif getattr(self, field.attname) in field.empty_values:
                # Set related object if it has been saved after an
                # assignment.
                setattr(self, field.name, obj)
            # If the relationship's pk/to_field was changed, clear the
            # cached relationship.
            if getattr(obj, field.target_field.attname) != getattr(
                self, field.attname
            ):
                field.delete_cached_value(self)
    # GenericForeignKeys are private.
    for field in self._meta.private_fields:
        if fields and field not in fields:
            continue
        if (
            field.is_relation
            and field.is_cached(self)
            and hasattr(field, "fk_field")
        ):
            obj = field.get_cached_value(self, default=None)
            if obj and obj.pk is None:
                raise ValueError(
                    f"{operation_name}() prohibited to prevent data loss due to "
                    f"unsaved related object '{field.name}'."
                )


QuerySet.bulk_create = spanner_bulk_create
QuerySet._prepare_for_bulk_create = spanner_prepare_for_bulk_create
ContentType._prepare_related_fields_for_save = (
    spanner_prepare_related_fields_for_save
)


def gen_rand_int64():
    # Credit to https://stackoverflow.com/a/3530326.
    return uuid4().int & 0x7FFFFFFFFFFFFFFF


def autofield_init(self, *args, **kwargs):
    kwargs["blank"] = True
    Field.__init__(self, *args, **kwargs)
    if django.db.connection.settings_dict["ENGINE"] == "django_spanner":
        self.default = gen_rand_int64


AutoField.__init__ = autofield_init
AutoField.db_returning = False
AutoField.validators = []
if USING_DJANGO_3:
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

# Sanity check here since tests can't easily be run for this file:
if __name__ == "__main__":
    from django.utils import timezone

    UTC = timezone.utc

    dt = datetime.datetime(2020, 1, 10, 2, 44, 57, 999, UTC)
    dtns = DatetimeWithNanoseconds(2020, 1, 10, 2, 44, 57, 999, UTC)
    equal = dtns == dt
    if not equal:
        raise Exception("%s\n!=\n%s" % (dtns, dt))
