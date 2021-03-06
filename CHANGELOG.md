# Changelog

## 2.2.1b0 (2021-01-29)


### ⚠ BREAKING CHANGES

* DBAPI code was moved into python-spanner in https://github.com/googleapis/python-spanner/pull/160. This change removes it from this repo and bumps the dependency on python-spanner to 2.0.0, the first released version to include DBAPI.
* Update python-spanner dep, drop py 3.5 (#557)

### Features

* [WIP] The first stage of `nox` implementation ([#468](https://www.github.com/googleapis/python-spanner-django/issues/468)) ([96f2223](https://www.github.com/googleapis/python-spanner-django/commit/96f2223e3389a0922e0f1db44df72c698cfa5263))
* Add dummy WHERE clause to certain statements ([#516](https://www.github.com/googleapis/python-spanner-django/issues/516)) ([af5d8e3](https://www.github.com/googleapis/python-spanner-django/commit/af5d8e3af808a8639e54c691c8f110be0a309d15))
* add PyPI release support ([#451](https://www.github.com/googleapis/python-spanner-django/issues/451)) ([da82c41](https://www.github.com/googleapis/python-spanner-django/commit/da82c417815e607611743c828f3525e71f9a46f4))
* clear session pool on connection close ([#543](https://www.github.com/googleapis/python-spanner-django/issues/543)) ([14e4cac](https://www.github.com/googleapis/python-spanner-django/commit/14e4cac77fd9ba5cf421c56c636528ec77b82451))
* cursor must detect if the parent connection is closed ([#463](https://www.github.com/googleapis/python-spanner-django/issues/463)) ([a9fd5a3](https://www.github.com/googleapis/python-spanner-django/commit/a9fd5a382463be47e34ec079a606fd9952048469))
* Implementing DB-API types according to the PEP-0249 specification ([#521](https://www.github.com/googleapis/python-spanner-django/issues/521)) ([62c22b1](https://www.github.com/googleapis/python-spanner-django/commit/62c22b113b470776cddacbab92c4428c6581c551))
* refactor connect() function, cover it with unit tests ([#462](https://www.github.com/googleapis/python-spanner-django/issues/462)) ([4fedcf1](https://www.github.com/googleapis/python-spanner-django/commit/4fedcf18a235c226d062ce7e61070477bfd3a107))
* Stage 2 of `nox` implementation - adding `docs` target ([#473](https://www.github.com/googleapis/python-spanner-django/issues/473)) ([45d6b97](https://www.github.com/googleapis/python-spanner-django/commit/45d6b970867627694684b628fb20900388f78663))
* Stage 3-4 of `nox` implementation - adding auto-format targets ([#478](https://www.github.com/googleapis/python-spanner-django/issues/478)) ([59e7c3f](https://www.github.com/googleapis/python-spanner-django/commit/59e7c3f2cb5ca8381a8674eb3f2aef59c37e9fa6))
* Stage 5 of `nox` implementation - adding coverage targets ([#479](https://www.github.com/googleapis/python-spanner-django/issues/479)) ([cec6b96](https://www.github.com/googleapis/python-spanner-django/commit/cec6b96d8b8ae662028d7f0901cacceeb2eb1c97))
* Stage 6 of `nox` implementation - enabling system tests ([#480](https://www.github.com/googleapis/python-spanner-django/issues/480)) ([dc73bf6](https://www.github.com/googleapis/python-spanner-django/commit/dc73bf65f9dbe0f9a62059ea23c6423dfcfd1901))
* support transactions management ([#535](https://www.github.com/googleapis/python-spanner-django/issues/535)) ([2f2cd86](https://www.github.com/googleapis/python-spanner-django/commit/2f2cd8631817c9f3d898c60e38778ae533c3f803))


### Bug Fixes

* add description for transaction autocommit ([#587](https://www.github.com/googleapis/python-spanner-django/issues/587)) ([8441edc](https://www.github.com/googleapis/python-spanner-django/commit/8441edcc161a5ad86f171dfc2cd4b9ccef19b2c0))
* add project env in readme file ([#586](https://www.github.com/googleapis/python-spanner-django/issues/586)) ([55b9d19](https://www.github.com/googleapis/python-spanner-django/commit/55b9d197f023067470f8769615a83e1a11df53ba))
* Bump version ahead of lateset release ([#571](https://www.github.com/googleapis/python-spanner-django/issues/571)) ([36e5b82](https://www.github.com/googleapis/python-spanner-django/commit/36e5b82facdc8e7a7286b2cf1ab20afa2e9e1aef))
* Change release script package name ([#489](https://www.github.com/googleapis/python-spanner-django/issues/489)) ([388ea6b](https://www.github.com/googleapis/python-spanner-django/commit/388ea6bc187bd5510e2aeab0fd5d6a6e46efb777))
* DatabaseWrapper method impl and potential bugfix ([#545](https://www.github.com/googleapis/python-spanner-django/issues/545)) ([d8453c7](https://www.github.com/googleapis/python-spanner-django/commit/d8453c7e458b0b476b91785d32ba234e333a4b9f))
* Fix black, isort compatibility  ([#469](https://www.github.com/googleapis/python-spanner-django/issues/469)) ([dd005d5](https://www.github.com/googleapis/python-spanner-django/commit/dd005d5a8f39634750a8c81b603782f1254dcccf))
* fix from-scratch tutorial ([#573](https://www.github.com/googleapis/python-spanner-django/issues/573)) ([59ce5e7](https://www.github.com/googleapis/python-spanner-django/commit/59ce5e7abd13a1793c7985ee4b4a092f6afdf770))
* fix healthchecks app tutorial ([#574](https://www.github.com/googleapis/python-spanner-django/issues/574)) ([65d2e9d](https://www.github.com/googleapis/python-spanner-django/commit/65d2e9dccf494c3283f1abcd936220b5f353c59e))
* Fix license classifier ([#507](https://www.github.com/googleapis/python-spanner-django/issues/507)) ([9244414](https://www.github.com/googleapis/python-spanner-django/commit/9244414d23fca9facdd05c0e10dde86891001001))
* Fix package name in README ([#556](https://www.github.com/googleapis/python-spanner-django/issues/556)) ([8b2329a](https://www.github.com/googleapis/python-spanner-django/commit/8b2329afca64863197790681d6bf8c64a9040823))
* fix typo in README ([#575](https://www.github.com/googleapis/python-spanner-django/issues/575)) ([d25fa86](https://www.github.com/googleapis/python-spanner-django/commit/d25fa86857409a4f0f17c9de3057465bef048df6))
* override django autocommit to spanner ([#583](https://www.github.com/googleapis/python-spanner-django/issues/583)) ([7ce685d](https://www.github.com/googleapis/python-spanner-django/commit/7ce685d76033fa8a46d4ccf8488af68ee8947ced))
* permanently broken date & time unit tests on Windows ([#524](https://www.github.com/googleapis/python-spanner-django/issues/524)) ([3f5db62](https://www.github.com/googleapis/python-spanner-django/commit/3f5db62863bd03c85b2a1b4614d5d782895b6d57))
* Replace repo name with pkg name ([#508](https://www.github.com/googleapis/python-spanner-django/issues/508)) ([fbba900](https://www.github.com/googleapis/python-spanner-django/commit/fbba9001344295a9e18cd153d7f8475bc3e1b684))
* s/installation/installation/ ([#509](https://www.github.com/googleapis/python-spanner-django/issues/509)) ([03c963a](https://www.github.com/googleapis/python-spanner-django/commit/03c963a7aaac61f3ea6575952c193e72c67f5bf2))
* s/useage/usage/ ([#511](https://www.github.com/googleapis/python-spanner-django/issues/511)) ([6b960ec](https://www.github.com/googleapis/python-spanner-django/commit/6b960ecea66cbe23fb7987763fbcd29ce0b8dc6d))
* update pypi package name ([#454](https://www.github.com/googleapis/python-spanner-django/issues/454)) ([47154d1](https://www.github.com/googleapis/python-spanner-django/commit/47154d1f6c7bf0b1d7150c24ba18e2f1dffd9cc1))
* Update README for alpha release ([#503](https://www.github.com/googleapis/python-spanner-django/issues/503)) ([3d31167](https://www.github.com/googleapis/python-spanner-django/commit/3d3116752acdc89ec90d56a9fa3b9d26d11ebf67))
* Update version to 2.2.0a1 ([#506](https://www.github.com/googleapis/python-spanner-django/issues/506)) ([a3a6344](https://www.github.com/googleapis/python-spanner-django/commit/a3a6344656d63e34d6110536aa6830b0db13343a))
* Use "any" default role in sphinx ([#550](https://www.github.com/googleapis/python-spanner-django/issues/550)) ([196c449](https://www.github.com/googleapis/python-spanner-django/commit/196c44949370fb818e610b21c3b00344fdc3d03a))


### Code Refactoring

* erase dbapi directory and all the related tests ([#554](https://www.github.com/googleapis/python-spanner-django/issues/554)) ([8183247](https://www.github.com/googleapis/python-spanner-django/commit/818324708e9ca46fbd80c47745bdf38e8a1a069c))
* Update python-spanner dep, drop py 3.5 ([#557](https://www.github.com/googleapis/python-spanner-django/issues/557)) ([5910833](https://www.github.com/googleapis/python-spanner-django/commit/5910833216288d2fd5cce57e98eb051d0cf82131))


### Documentation

* add a querying example into the main readme ([#515](https://www.github.com/googleapis/python-spanner-django/issues/515)) ([c477cc2](https://www.github.com/googleapis/python-spanner-django/commit/c477cc283ab1f036454eb446f0ca0599235b1e5c))
* minor fixes to README.md ([#448](https://www.github.com/googleapis/python-spanner-django/issues/448)) ([f969000](https://www.github.com/googleapis/python-spanner-django/commit/f9690007603c94f4c99b244a92c639adfd360a8f))
* move test suite information to CONTRIBUTING.md ([#442](https://www.github.com/googleapis/python-spanner-django/issues/442)) ([05280ae](https://www.github.com/googleapis/python-spanner-django/commit/05280aecdcbe933e113616b5705f4e76303d9637))
* Update docstrings for `django_spanner` ([#564](https://www.github.com/googleapis/python-spanner-django/issues/564)) ([7083f1d](https://www.github.com/googleapis/python-spanner-django/commit/7083f1d81dc8b412aab5a4e7d7f110152a87c5d9))
* updated `README.rst` file ([#563](https://www.github.com/googleapis/python-spanner-django/issues/563)) ([d70cb28](https://www.github.com/googleapis/python-spanner-django/commit/d70cb28c8a20511558fa47818103afb5e0492918))
* verify and comment the DB API exceptions ([#522](https://www.github.com/googleapis/python-spanner-django/issues/522)) ([5ed0845](https://www.github.com/googleapis/python-spanner-django/commit/5ed08453002a318245d9241cd1e24c222a588159))

## 2.2.0a1 (2020-09-29)


### Features

* [WIP] The first stage of `nox` implementation ([#468](https://www.github.com/googleapis/python-spanner-django/issues/468)) ([96f2223](https://www.github.com/googleapis/python-spanner-django/commit/96f2223e3389a0922e0f1db44df72c698cfa5263))
* add PyPI release support ([#451](https://www.github.com/googleapis/python-spanner-django/issues/451)) ([da82c41](https://www.github.com/googleapis/python-spanner-django/commit/da82c417815e607611743c828f3525e71f9a46f4)), closes [#449](https://www.github.com/googleapis/python-spanner-django/issues/449)
* cursor must detect if the parent connection is closed ([#463](https://www.github.com/googleapis/python-spanner-django/issues/463)) ([a9fd5a3](https://www.github.com/googleapis/python-spanner-django/commit/a9fd5a382463be47e34ec079a606fd9952048469))
* refactor connect() function, cover it with unit tests ([#462](https://www.github.com/googleapis/python-spanner-django/issues/462)) ([4fedcf1](https://www.github.com/googleapis/python-spanner-django/commit/4fedcf18a235c226d062ce7e61070477bfd3a107))
* Stage 2 of `nox` implementation - adding `docs` target ([#473](https://www.github.com/googleapis/python-spanner-django/issues/473)) ([45d6b97](https://www.github.com/googleapis/python-spanner-django/commit/45d6b970867627694684b628fb20900388f78663))
* Stage 3-4 of `nox` implementation - adding auto-format targets ([#478](https://www.github.com/googleapis/python-spanner-django/issues/478)) ([59e7c3f](https://www.github.com/googleapis/python-spanner-django/commit/59e7c3f2cb5ca8381a8674eb3f2aef59c37e9fa6))
* Stage 5 of `nox` implementation - adding coverage targets ([#479](https://www.github.com/googleapis/python-spanner-django/issues/479)) ([cec6b96](https://www.github.com/googleapis/python-spanner-django/commit/cec6b96d8b8ae662028d7f0901cacceeb2eb1c97))
* Stage 6 of `nox` implementation - enabling system tests ([#480](https://www.github.com/googleapis/python-spanner-django/issues/480)) ([dc73bf6](https://www.github.com/googleapis/python-spanner-django/commit/dc73bf65f9dbe0f9a62059ea23c6423dfcfd1901))


### Bug Fixes

* Change release script package name ([#489](https://www.github.com/googleapis/python-spanner-django/issues/489)) ([388ea6b](https://www.github.com/googleapis/python-spanner-django/commit/388ea6bc187bd5510e2aeab0fd5d6a6e46efb777))
* Fix black, isort compatibility  ([#469](https://www.github.com/googleapis/python-spanner-django/issues/469)) ([dd005d5](https://www.github.com/googleapis/python-spanner-django/commit/dd005d5a8f39634750a8c81b603782f1254dcccf))
* Fix license classifier ([#507](https://www.github.com/googleapis/python-spanner-django/issues/507)) ([9244414](https://www.github.com/googleapis/python-spanner-django/commit/9244414d23fca9facdd05c0e10dde86891001001))
* Replace repo name with pkg name ([#508](https://www.github.com/googleapis/python-spanner-django/issues/508)) ([fbba900](https://www.github.com/googleapis/python-spanner-django/commit/fbba9001344295a9e18cd153d7f8475bc3e1b684))
* s/installation/installation/ ([#509](https://www.github.com/googleapis/python-spanner-django/issues/509)) ([03c963a](https://www.github.com/googleapis/python-spanner-django/commit/03c963a7aaac61f3ea6575952c193e72c67f5bf2))
* s/useage/usage/ ([#511](https://www.github.com/googleapis/python-spanner-django/issues/511)) ([6b960ec](https://www.github.com/googleapis/python-spanner-django/commit/6b960ecea66cbe23fb7987763fbcd29ce0b8dc6d))
* update pypi package name ([#454](https://www.github.com/googleapis/python-spanner-django/issues/454)) ([47154d1](https://www.github.com/googleapis/python-spanner-django/commit/47154d1f6c7bf0b1d7150c24ba18e2f1dffd9cc1)), closes [#455](https://www.github.com/googleapis/python-spanner-django/issues/455)
* Update README for alpha release ([#503](https://www.github.com/googleapis/python-spanner-django/issues/503)) ([3d31167](https://www.github.com/googleapis/python-spanner-django/commit/3d3116752acdc89ec90d56a9fa3b9d26d11ebf67))
* Update version to 2.2.0a1 ([#506](https://www.github.com/googleapis/python-spanner-django/issues/506)) ([a3a6344](https://www.github.com/googleapis/python-spanner-django/commit/a3a6344656d63e34d6110536aa6830b0db13343a)), closes [#502](https://www.github.com/googleapis/python-spanner-django/issues/502)


### Reverts

* Revert "django_spanner: skip 57 expressions_case tests that assume serial pk" ([48909f6](https://www.github.com/googleapis/python-spanner-django/commit/48909f6aa2dc33aca6843de2d1ce18ab943294fe)), closes [#353](https://www.github.com/googleapis/python-spanner-django/issues/353)


### Documentation

* minor fixes to README.md ([#448](https://www.github.com/googleapis/python-spanner-django/issues/448)) ([f969000](https://www.github.com/googleapis/python-spanner-django/commit/f9690007603c94f4c99b244a92c639adfd360a8f))
* move test suite information to CONTRIBUTING.md ([#442](https://www.github.com/googleapis/python-spanner-django/issues/442)) ([05280ae](https://www.github.com/googleapis/python-spanner-django/commit/05280aecdcbe933e113616b5705f4e76303d9637))

## 2.2.0a1 (2020-09-15)


### Features

* [WIP] The first stage of `nox` implementation ([#468](https://www.github.com/googleapis/python-spanner-django/issues/468)) ([96f2223](https://www.github.com/googleapis/python-spanner-django/commit/96f2223e3389a0922e0f1db44df72c698cfa5263))
* add PyPI release support ([#451](https://www.github.com/googleapis/python-spanner-django/issues/451)) ([da82c41](https://www.github.com/googleapis/python-spanner-django/commit/da82c417815e607611743c828f3525e71f9a46f4)), closes [#449](https://www.github.com/googleapis/python-spanner-django/issues/449)
* cursor must detect if the parent connection is closed ([#463](https://www.github.com/googleapis/python-spanner-django/issues/463)) ([a9fd5a3](https://www.github.com/googleapis/python-spanner-django/commit/a9fd5a382463be47e34ec079a606fd9952048469))
* refactor connect() function, cover it with unit tests ([#462](https://www.github.com/googleapis/python-spanner-django/issues/462)) ([4fedcf1](https://www.github.com/googleapis/python-spanner-django/commit/4fedcf18a235c226d062ce7e61070477bfd3a107))
* Stage 2 of `nox` implementation - adding `docs` target ([#473](https://www.github.com/googleapis/python-spanner-django/issues/473)) ([45d6b97](https://www.github.com/googleapis/python-spanner-django/commit/45d6b970867627694684b628fb20900388f78663))
* Stage 3-4 of `nox` implementation - adding auto-format targets ([#478](https://www.github.com/googleapis/python-spanner-django/issues/478)) ([59e7c3f](https://www.github.com/googleapis/python-spanner-django/commit/59e7c3f2cb5ca8381a8674eb3f2aef59c37e9fa6))
* Stage 5 of `nox` implementation - adding coverage targets ([#479](https://www.github.com/googleapis/python-spanner-django/issues/479)) ([cec6b96](https://www.github.com/googleapis/python-spanner-django/commit/cec6b96d8b8ae662028d7f0901cacceeb2eb1c97))
* Stage 6 of `nox` implementation - enabling system tests ([#480](https://www.github.com/googleapis/python-spanner-django/issues/480)) ([dc73bf6](https://www.github.com/googleapis/python-spanner-django/commit/dc73bf65f9dbe0f9a62059ea23c6423dfcfd1901))


### Bug Fixes

* Change release script package name ([#489](https://www.github.com/googleapis/python-spanner-django/issues/489)) ([388ea6b](https://www.github.com/googleapis/python-spanner-django/commit/388ea6bc187bd5510e2aeab0fd5d6a6e46efb777))
* Fix black, isort compatibility  ([#469](https://www.github.com/googleapis/python-spanner-django/issues/469)) ([dd005d5](https://www.github.com/googleapis/python-spanner-django/commit/dd005d5a8f39634750a8c81b603782f1254dcccf))
* update pypi package name ([#454](https://www.github.com/googleapis/python-spanner-django/issues/454)) ([47154d1](https://www.github.com/googleapis/python-spanner-django/commit/47154d1f6c7bf0b1d7150c24ba18e2f1dffd9cc1)), closes [#455](https://www.github.com/googleapis/python-spanner-django/issues/455)
* Update README for alpha release ([#503](https://www.github.com/googleapis/python-spanner-django/issues/503)) ([3d31167](https://www.github.com/googleapis/python-spanner-django/commit/3d3116752acdc89ec90d56a9fa3b9d26d11ebf67))
* Update version to 2.2.0a1 ([#506](https://www.github.com/googleapis/python-spanner-django/issues/506)) ([a3a6344](https://www.github.com/googleapis/python-spanner-django/commit/a3a6344656d63e34d6110536aa6830b0db13343a)), closes [#502](https://www.github.com/googleapis/python-spanner-django/issues/502)


### Reverts

* Revert "django_spanner: skip 57 expressions_case tests that assume serial pk" ([48909f6](https://www.github.com/googleapis/python-spanner-django/commit/48909f6aa2dc33aca6843de2d1ce18ab943294fe)), closes [#353](https://www.github.com/googleapis/python-spanner-django/issues/353)


### Documentation

* minor fixes to README.md ([#448](https://www.github.com/googleapis/python-spanner-django/issues/448)) ([f969000](https://www.github.com/googleapis/python-spanner-django/commit/f9690007603c94f4c99b244a92c639adfd360a8f))
* move test suite information to CONTRIBUTING.md ([#442](https://www.github.com/googleapis/python-spanner-django/issues/442)) ([05280ae](https://www.github.com/googleapis/python-spanner-django/commit/05280aecdcbe933e113616b5705f4e76303d9637))
