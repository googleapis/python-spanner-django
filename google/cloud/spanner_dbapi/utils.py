# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

import re


class PeekIterator:
    """
    Peeks at the first element out of an iterator for the sake of operations
    like auto-population of fields on reading the first element.
    If next's result is an instance of list, it'll be converted into a tuple
    to conform with DBAPI v2's sequence expectations.

    :type source: list
    :param source: A list of source for Iterator.
    """

    def __init__(self, source):
        itr_src = iter(source)

        self.__iters = []
        self.__index = 0

        try:
            head = next(itr_src)
            # Restitch and prepare to read from multiple iterators.
            self.__iters = [iter(itr) for itr in [[head], itr_src]]
        except StopIteration:
            pass

    def __next__(self):
        if self.__index >= len(self.__iters):
            raise StopIteration

        iterator = self.__iters[self.__index]
        try:
            head = next(iterator)
        except StopIteration:
            # That iterator has been exhausted, try with the next one.
            self.__index += 1
            return self.__next__()
        else:
            return tuple(head) if isinstance(head, list) else head

    def __iter__(self):
        return self


re_UNICODE_POINTS = re.compile(r"([^\s]*[\u0080-\uFFFF]+[^\s]*)")


def backtick_unicode(sql):
    """Checks sql to be valid and splits it by segments.

    :type sql: str
    :param sql: SQL request.

    :rtype: str
    :returns: SQL parsed by segments in unicode if initial
             SQL is valid, initial string otherwise.
    """
    matches = list(re_UNICODE_POINTS.finditer(sql))
    if not matches:
        return sql

    segments = []

    last_end = 0
    for match in matches:
        start, end = match.span()
        if sql[start] != "`" and sql[end - 1] != "`":
            segments.append(sql[last_end:start] + "`" + sql[start:end] + "`")
        else:
            segments.append(sql[last_end:end])

        last_end = end

    return "".join(segments)


def sanitize_literals_for_upload(s):
    """Convert literals in s, to be fit for consumption by Cloud Spanner.

    * Convert %% (escaped percent literals) to %. Percent signs must be escaped
      when values like %s are used as SQL parameter placeholders but Spanner's query
      language uses placeholders like @a0 and doesn't expect percent signs to be
      escaped.

    * Quote words containing non-ASCII, with backticks, for example föö to `föö`.

    :rtype: str
    :returns: Sanitized string for uploading.
    """
    return backtick_unicode(s.replace("%%", "%"))
