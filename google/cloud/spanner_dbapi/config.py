# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""Configurations module for DB API."""

# Cloud Spanner sessions pool, used by
# default for the whole DB API package.
# Is lazily initiated on a connection creation.
default_pool = None
