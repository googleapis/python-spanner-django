pip install django==3.2

mkdir django_test
cd django_test

django-admin startproject foreign_keys
python manage.py startapp applic

models_code = "
from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=32)


class City(models.Model):
    name = models.CharField(max_length=32)
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING)
"

echo "$models_code" > applic/models.py

sed -i 's/INSTALLED_APPS = [/INSTALLED_APPS = ["applic.apps.ApplicConfig",/g' foreign_keys/setting.py

python manage.py makemigrations
python manage.py migrate
