# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

from django.db.backends.base.client import BaseDatabaseClient
from google.cloud.spanner_dbapi.exceptions import NotSupportedError


class DatabaseClient(BaseDatabaseClient):
    """Wraps the Django base class via implementing the `runshell` method.

    TODO: Missing actual implementation of `runshell`.

    :raises: :class:`~google.cloud.spanner_dbapi.exceptions.NotSupportedError`
    """
    def runshell(self, parameters):
        raise NotSupportedError("This method is not supported.")
