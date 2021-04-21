"""
Different models used for testing django-spanner code.
"""
import os
from django.db import models
import django
from django.db.models import Transform
from django.db.models import CharField, TextField

# Load django settings before loading dhango models.
os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"
django.setup()


# Register transformations for model fields.
class UpperCase(Transform):
    lookup_name = "upper"
    function = "UPPER"
    bilateral = True


CharField.register_lookup(UpperCase)
TextField.register_lookup(UpperCase)


# Models
class ModelDecimalField(models.Model):
    field = models.DecimalField()


class ModelCharField(models.Model):
    field = models.CharField()


class Item(models.Model):
    item_id = models.IntegerField()
    name = models.CharField(max_length=10)
    created = models.DateTimeField()
    modified = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["name"]


class Number(models.Model):
    num = models.IntegerField()
    decimal_num = models.DecimalField(max_digits=5, decimal_places=2)
    item = models.ForeignKey(Item, models.CASCADE)


class Author(models.Model):
    name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    num = models.IntegerField(unique=True)
    created = models.DateTimeField()
    modified = models.DateTimeField(blank=True, null=True)


class Report(models.Model):
    name = models.CharField(max_length=10)
    creator = models.ForeignKey(Author, models.CASCADE, null=True)

    class Meta:
        ordering = ["name"]
