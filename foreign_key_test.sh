pip install django==3.2

mkdir django_test
cd django_test

django-admin startproject foreign_keys
cd foreign_keys
python manage.py startapp applic

echo "
from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=32)


class City(models.Model):
    name = models.CharField(max_length=32)
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING)
" > applic/models.py


echo "from django.test import TestCase
from .models import City, Country


class EnqueuedRoutesTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name='Country123')
        self.city = City.objects.create(name='City123', country=self.country)
    
    def test_foreign_key(self):
        city = City.objects.get(pk=1)
        assert city.country == Country.objects.get(pk=1)" > applic/tests.py

sed -i -- 's/INSTALLED_APPS = \[/INSTALLED_APPS = \[\"applic\.apps\.ApplicConfig\"\,/g' foreign_keys/settings.py

python manage.py makemigrations
python manage.py migrate

python manage.py test
