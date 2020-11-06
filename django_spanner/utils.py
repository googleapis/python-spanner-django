import django
import sqlparse
from django.core.exceptions import ImproperlyConfigured
from django.utils.version import get_version_tuple


def check_django_compatability():
    """
    Verify that this version of django-spanner is compatible with the installed
    version of Django. For example, any django-spanner 2.2.x is compatible
    with Django 2.2.y.
    """
    from . import __version__

    if django.VERSION[:2] != get_version_tuple(__version__)[:2]:
        raise ImproperlyConfigured(
            "You must use the latest version of django-spanner {A}.{B}.x "
            "with Django {A}.{B}.y (found django-spanner {C}).".format(
                A=django.VERSION[0], B=django.VERSION[1], C=__version__
            )
        )


def ensure_where_clause(sql):
    """
    Cloud Spanner requires a WHERE clause on UPDATE and DELETE statements.
    Add a dummy WHERE clause if necessary.
    """
    if any(
        isinstance(token, sqlparse.sql.Where)
        for token in sqlparse.parse(sql)[0]
    ):
        return sql

    return sql + " WHERE 1=1"
