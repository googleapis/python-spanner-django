# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""API to calculate checksums of SQL statements results."""

import hashlib
import pickle

from google.cloud.spanner_dbapi.exceptions import AbortedRetried


class ResultsChecksum:
    """Cumulative checksum.

    Used to calculate a total checksum of all the results
    returned by operations executed within transaction.
    Includes methods for checksums comparison.
    These checksums are used while retrying an aborted
    transaction to check if the results of a retried transaction
    are equal to the results of the original transaction.
    """

    def __init__(self):
        self.checksum = hashlib.sha256()
        self.count = 0  # counter of consumed results

    def __len__(self):
        """Return the number of consumed results.

        :rtype: :class:`int`
        :returns: The number of results.
        """
        return self.count

    def __eq__(self, other):
        """Check if checksums are equal.

        :type other: :class:`google.cloud.spanner_dbapi.checksum.ResultsChecksum`
        :param other: Another checksum to compare with this one.
        """
        return self.checksum.digest() == other.checksum.digest()

    def consume_result(self, result):
        """Add the given result into the checksum.

        :type result: Union[int, list]
        :param result: Streamed row or row count from an UPDATE operation.
        """
        self.checksum.update(pickle.dumps(result))
        self.count += 1


def _compare_checksums(original, retried):
    """Compare the given checksums.

    Raise an error if the given checksums are not equal.

    :type original: :class:`~google.cloud.spanner_dbapi.checksum.ResultsChecksum`
    :param original: results checksum of the original transaction.

    :type retried: :class:`~google.cloud.spanner_dbapi.checksum.ResultsChecksum`
    :param retried: results checksum of the retried transaction.

    :raises: :exc:`google.cloud.spanner_dbapi.exceptions.AbortedRetried` in case if checksums are not equal.
    """
    if retried != original:
        raise AbortedRetried(
            "The transaction was aborted and could not be retried due to a concurrent modification."
        )
