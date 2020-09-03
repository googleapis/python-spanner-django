# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""DBAPI enum types."""

import enum


class TransactionModes(enum.Enum):
    READ_ONLY = "READ_ONLY"
    READ_WRITE = "READ_WRITE"


class AutocommitDMLModes(enum.Enum):
    TRANSACTIONAL = "TRANSACTIONAL"
    PARTITIONED_NON_ATOMIC = "PARTITIONED_NON_ATOMIC"
