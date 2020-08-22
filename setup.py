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

import io
import os

from setuptools import find_packages, setup

# Package metadata.

name = "django-google-spanner"
description = "Bridge to enable using Django with Spanner."
version = "2.2a0"
# Should be one of:
# 'Development Status :: 3 - Alpha'
# 'Development Status :: 4 - Beta'
# 'Development Status :: 5 - Production/Stable'
release_status = "Development Status :: 3 - Alpha"
dependencies = [
    'sqlparse >= 0.3.0',
    'google-cloud-spanner >= 1.8.0',
]
extras = {}


# Setup boilerplate below this line.

package_root = os.path.abspath(os.path.dirname(__file__))

readme_filename = os.path.join(package_root, "README.md")
with io.open(readme_filename, encoding="utf-8") as readme_file:
    readme = readme_file.read()


setup(
        name=name,
        version=version,
        description=description,
        long_description=readme,
        author='Google LLC',
        author_email='cloud-spanner-developers@googlegroups.com',
        license='Apache 2.0',
        packages=find_packages(exclude=['tests']),
        install_requires=dependencies,
        url="https://github.com/googleapis/python-spanner-django",
        classifiers=[
            release_status,
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Topic :: Utilities',
            'Framework :: Django',
            'Framework :: Django :: 2.2',
        ],
        extras_require=extras,
        python_requires=">=3.5",
)
