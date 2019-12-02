# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.db.models.lookups import (
    EndsWith, IEndsWith, IStartsWith, StartsWith,
)


def extract_fmtstr_params(self, compiler, connection, is_ends_with=False):
    lhs_sql, params = self.process_lhs(compiler, connection)
    rhs_sql, rhs_params = self.process_rhs(compiler, connection)
    params.extend(rhs_params)
    rhs_sql = self.get_rhs_op(connection, rhs_sql)
    if is_ends_with:
        params[0] = params[0][1:]
    else:
        params[0] = params[0][:-1]

    return rhs_sql % lhs_sql, params


def fmtstr_params_for_regexp_contains(self, compiler, connection, is_ends_with):
    """
    Extract the format string for istartswith and iendswith whose
    underlying implementation uses REGEXP_CONTAINS(%s, 'r"(?i)%s"',
    but unfortunately if we let parameters be bound at exec time,
    they'll just be replaced with the @variable which makes invalid
    Cloud Spanner SQL statements.

    In otherwords:
      Replace all the params inline otherwise we'll be stuck in the situation
      such as:
      SQL:
        SELECT blog_post.id FROM blog_post WHERE REGEXP_CONTAINS(blog_post.title, r"^(?i)@a0")
      and then
        Params={'a0': 'Cloud'}, param_types={}
      which unfortunately won't yield any results.
      but really we want that inline replacement to be
      SQL:
        SELECT blog_post.id FROM blog_post WHERE REGEXP_CONTAINS(blog_post.title, r"^(?i)Cloud")
    """
    fmtstr, params = extract_fmtstr_params(self, compiler, connection, is_ends_with)

    for param in params:
        fmtstr = fmtstr % param
    return fmtstr, ()


def endswith(self, compiler, connection):
    return extract_fmtstr_params(self, compiler, connection, is_ends_with=True)


def startswith(self, compiler, connection):
    return extract_fmtstr_params(self, compiler, connection, is_ends_with=False)


def istartswith(self, compiler, connection):
    return fmtstr_params_for_regexp_contains(self, compiler, connection, is_ends_with=False)


def iendswith(self, compiler, connection):
    return fmtstr_params_for_regexp_contains(self, compiler, connection, is_ends_with=True)


def register_lookups():
    EndsWith.as_spanner = endswith
    IEndsWith.as_spanner = iendswith
    StartsWith.as_spanner = startswith
    IStartsWith.as_spanner = istartswith
