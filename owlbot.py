# Copyright 2021 Google LLC
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

"""This script is used to synthesize generated parts of this library."""
import synthtool as s
import synthtool.gcp as gcp

# ----------------------------------------------------------------------------
# Add templated files
# ----------------------------------------------------------------------------
templated_files = gcp.CommonTemplates().py_library(microgenerator=True)

# Just move templates for building docs and releases
# Presubmit and continuous are configured differently
s.move(templated_files / ".kokoro" / "docs")
s.move(templated_files / ".kokoro" / "release.sh")
s.move(templated_files / ".kokoro" / "trampoline_v2.sh")
s.move(templated_files / ".kokoro" / "trampoline.sh")
s.move(templated_files / ".kokoro" / "populate_secrets.sh")
s.move(templated_files / ".kokoro" / "release")

s.shell.run(["nox", "-s", "blacken"], hide_output=False)
