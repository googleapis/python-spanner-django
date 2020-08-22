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

import sys
from unittest import TestCase

from google.api_core.gapic_v1.client_info import ClientInfo
from spanner_dbapi.version import DEFAULT_USER_AGENT, google_client_info

vers = sys.version_info


class VersionUtils(TestCase):
    def test_google_client_info_default_useragent(self):
        got = google_client_info().to_grpc_metadata()
        want = ClientInfo(
            user_agent=DEFAULT_USER_AGENT,
            python_version='%d.%d.%d' % (vers.major, vers.minor, vers.micro or 0),
        ).to_grpc_metadata()
        self.assertEqual(got, want)

    def test_google_client_info_custom_useragent(self):
        got = google_client_info('custom-user-agent').to_grpc_metadata()
        want = ClientInfo(
            user_agent='custom-user-agent',
            python_version='%d.%d.%d' % (vers.major, vers.minor, vers.micro or 0),
        ).to_grpc_metadata()
        self.assertEqual(got, want)
