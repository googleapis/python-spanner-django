# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

import io
import os

import setuptools

# Disable version normalization performed by setuptools.setup()
try:
    # Try the approach of using sic(), added in setuptools 46.1.0
    from setuptools import sic
except ImportError:
    # Try the approach of replacing packaging.version.Version
    sic = lambda v: v
    try:
        # setuptools >=39.0.0 uses packaging from setuptools.extern
        from setuptools.extern import packaging
    except ImportError:
        # setuptools <39.0.0 uses packaging from pkg_resources.extern
        from pkg_resources.extern import packaging
    packaging.version.Version = packaging.version.LegacyVersion

# Package metadata.
name = "django-google-spanner"
description = "Bridge to enable using Django with Spanner."
# Should be one of:
# 'Development Status :: 3 - Alpha'
# 'Development Status :: 4 - Beta'
# 'Development Status :: 5 - Production/Stable'
release_status = "Development Status :: 3 - Alpha"
dependencies = ["sqlparse >= 0.3.0", "google-cloud-spanner >= 3.0.0"]
extras = {}

BASE_DIR = os.path.dirname(__file__)
VERSION_FILENAME = os.path.join(BASE_DIR, "version.py")
PACKAGE_INFO = {}
with open(VERSION_FILENAME) as f:
    exec(f.read(), PACKAGE_INFO)
version = PACKAGE_INFO["__version__"]

# Setup boilerplate below this line.

package_root = os.path.abspath(BASE_DIR)

readme_filename = os.path.join(package_root, "README.rst")
with io.open(readme_filename, encoding="utf-8") as readme_file:
    readme = readme_file.read()

setuptools.setup(
    name=name,
    version=sic(version),
    description=description,
    long_description=readme,
    author="Google LLC",
    author_email="googleapis-packages@google.com",
    license="BSD",
    packages=setuptools.find_packages(exclude=["tests"]),
    install_requires=dependencies,
    url="https://github.com/googleapis/python-spanner-django",
    classifiers=[
        release_status,
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
    ],
    extras_require=extras,
    python_requires=">=3.6",
)
