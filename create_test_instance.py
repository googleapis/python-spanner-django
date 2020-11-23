# Copyright 2016 Google LLC All rights reserved.
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

import os

from google.auth.credentials import AnonymousCredentials
from google.cloud.spanner_v1 import Client


INSTANCE_ID = "google-cloud-django-backend-tests"


class Config(object):
    """Run-time configuration to be modified at set-up.

    This is a mutable stand-in to allow test set-up to modify
    global state.
    """

    CLIENT = None
    INSTANCE_CONFIG = None
    INSTANCE = None


emulator_project = os.getenv("GCLOUD_PROJECT", "emulator-test-project")
Config.CLIENT = Client(
    project=emulator_project, credentials=AnonymousCredentials()
)

configs = list(Config.CLIENT.list_instance_configs())

Config.INSTANCE_CONFIG = configs[0]
config_name = configs[0].name

Config.INSTANCE = Config.CLIENT.instance(INSTANCE_ID, config_name)
created_op = Config.INSTANCE.create()
created_op.result(30)  # block until completion
