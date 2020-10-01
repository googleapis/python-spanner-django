# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""DBAPI enum types."""

import enum


class TransactionModes(enum.IntEnum):
    READ_ONLY = 0
    READ_WRITE = 1


class AutocommitDMLModes(enum.IntEnum):
    TRANSACTIONAL = 0
    PARTITIONED_NON_ATOMIC = 1
