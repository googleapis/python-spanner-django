# Changelog

## 2.2.a0 (2020-09-15)


### Features

* [WIP] The first stage of `nox` implementation ([#468](https://www.github.com/googleapis/python-spanner-django/issues/468)) ([5551b58](https://www.github.com/googleapis/python-spanner-django/commit/5551b58d7983edc57f0482000254ea2df21476d6))
* add PyPI release support ([#451](https://www.github.com/googleapis/python-spanner-django/issues/451)) ([da82c41](https://www.github.com/googleapis/python-spanner-django/commit/da82c417815e607611743c828f3525e71f9a46f4)), closes [#449](https://www.github.com/googleapis/python-spanner-django/issues/449)
* cursor must detect if the parent connection is closed ([#463](https://www.github.com/googleapis/python-spanner-django/issues/463)) ([6028f88](https://www.github.com/googleapis/python-spanner-django/commit/6028f88fa268523d0b7e84fac2f5915655c423e7))
* refactor connect() function, cover it with unit tests ([#462](https://www.github.com/googleapis/python-spanner-django/issues/462)) ([bfde221](https://www.github.com/googleapis/python-spanner-django/commit/bfde2214ded7f7205286f62d5a5feac8687f0139))
* release 2.2a0 ([#457](https://www.github.com/googleapis/python-spanner-django/issues/457)) ([11222db](https://www.github.com/googleapis/python-spanner-django/commit/11222db2f82fd50ca87010321ded0b39021eb884))
* Release 2.2a1 ([#491](https://www.github.com/googleapis/python-spanner-django/issues/491)) ([6a4fda8](https://www.github.com/googleapis/python-spanner-django/commit/6a4fda8b4920f4d052317d87be0ddd0ed1a87cdd))
* Stage 2 of `nox` implementation - adding `docs` target ([#473](https://www.github.com/googleapis/python-spanner-django/issues/473)) ([e017901](https://www.github.com/googleapis/python-spanner-django/commit/e0179015ab49d13c9848086a939d7fb432133467))
* Stage 3-4 of `nox` implementation - adding auto-format targets ([#478](https://www.github.com/googleapis/python-spanner-django/issues/478)) ([7a1f6a6](https://www.github.com/googleapis/python-spanner-django/commit/7a1f6a642de967237ce0e8f511a9d12907e4647b))
* Stage 5 of `nox` implementation - adding coverage targets ([#479](https://www.github.com/googleapis/python-spanner-django/issues/479)) ([acd9209](https://www.github.com/googleapis/python-spanner-django/commit/acd9209c13bf726bbcba4fe1e1a9b368a3eeda23))
* Stage 6 of `nox` implementation - enabling system tests ([#480](https://www.github.com/googleapis/python-spanner-django/issues/480)) ([94ba284](https://www.github.com/googleapis/python-spanner-django/commit/94ba284118c6cb02fccc9d40bb6c1e52d3a532a0))


### Bug Fixes

* Change release script package name ([#489](https://www.github.com/googleapis/python-spanner-django/issues/489)) ([fdd7113](https://www.github.com/googleapis/python-spanner-django/commit/fdd71137f0aa196de9ec7b41422cfe78829be5ba))
* Fix black, isort compatibility  ([#469](https://www.github.com/googleapis/python-spanner-django/issues/469)) ([144bdc2](https://www.github.com/googleapis/python-spanner-django/commit/144bdc2d04643d55c59d054e796afcf20ba96755))
* update pypi package name ([#454](https://www.github.com/googleapis/python-spanner-django/issues/454)) ([47154d1](https://www.github.com/googleapis/python-spanner-django/commit/47154d1f6c7bf0b1d7150c24ba18e2f1dffd9cc1)), closes [#455](https://www.github.com/googleapis/python-spanner-django/issues/455)


### Reverts

* Revert "django_spanner: skip 57 expressions_case tests that assume serial pk" ([48909f6](https://www.github.com/googleapis/python-spanner-django/commit/48909f6aa2dc33aca6843de2d1ce18ab943294fe)), closes [#353](https://www.github.com/googleapis/python-spanner-django/issues/353)


### Documentation

* minor fixes to README.md ([#448](https://www.github.com/googleapis/python-spanner-django/issues/448)) ([f969000](https://www.github.com/googleapis/python-spanner-django/commit/f9690007603c94f4c99b244a92c639adfd360a8f))
* move test suite information to CONTRIBUTING.md ([#442](https://www.github.com/googleapis/python-spanner-django/issues/442)) ([05280ae](https://www.github.com/googleapis/python-spanner-django/commit/05280aecdcbe933e113616b5705f4e76303d9637))
