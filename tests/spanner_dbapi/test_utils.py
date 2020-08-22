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

from unittest import TestCase

from spanner_dbapi.utils import PeekIterator


class UtilsTests(TestCase):
    def test_peekIterator_list_rows_converted_to_tuples(self):
        # Cloud Spanner returns results in lists e.g. [result].
        # PeekIterator is used by BaseCursor in its fetch* methods.
        # This test ensures that anything passed into PeekIterator
        # will be returned as a tuple.
        pit = PeekIterator([['a'], ['b'], ['c'], ['d'], ['e']])
        got = list(pit)
        want = [('a',), ('b',), ('c',), ('d',), ('e',)]
        self.assertEqual(got, want, 'Rows of type list must be returned as tuples')

        seventeen = PeekIterator([[17]])
        self.assertEqual(list(seventeen), [(17,)])

        pit = PeekIterator([['%', '%d']])
        self.assertEqual(next(pit), ('%', '%d',))

        pit = PeekIterator([('Clark', 'Kent')])
        self.assertEqual(next(pit), ('Clark', 'Kent',))

    def test_peekIterator_nonlist_rows_unconverted(self):
        pi = PeekIterator(['a', 'b', 'c', 'd', 'e'])
        got = list(pi)
        want = ['a', 'b', 'c', 'd', 'e']
        self.assertEqual(got, want, 'Values should be returned unchanged')
