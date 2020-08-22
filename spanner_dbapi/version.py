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

from google.api_core.gapic_v1.client_info import ClientInfo

VERSION = '0.0.1'
DEFAULT_USER_AGENT = 'django_spanner/' + VERSION

vers = sys.version_info


def google_client_info(user_agent=None):
    """
    Return a google.api_core.gapic_v1.client_info.ClientInfo
    containg the user_agent and python_version for this library
    """

    return ClientInfo(
        user_agent=user_agent or DEFAULT_USER_AGENT,
        python_version='%d.%d.%d' % (vers.major, vers.minor, vers.micro or 0),
    )
