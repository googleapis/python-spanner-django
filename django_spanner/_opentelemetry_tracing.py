# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

"""Manages OpenTelemetry trace creation and handling"""

from contextlib import contextmanager

from google.api_core.exceptions import GoogleAPICallError
from google.cloud.spanner_v1 import SpannerClient

try:
    from opentelemetry import trace
    from opentelemetry.trace.status import Status, StatusCanonicalCode
    from opentelemetry.instrumentation.utils import (
        http_status_to_canonical_code,
    )

    HAS_OPENTELEMETRY_INSTALLED = True
except ImportError:
    HAS_OPENTELEMETRY_INSTALLED = False


@contextmanager
def trace_call(name, connection, extra_attributes=None):
    if not HAS_OPENTELEMETRY_INSTALLED or not connection:
        # Empty context manager. Users will have to check if the generated value is None or a span
        yield None
        return

    tracer = trace.get_tracer(__name__)

    # Set base attributes that we know for every trace created
    attributes = {
        "db.type": "spanner",
        "db.url": SpannerClient.DEFAULT_ENDPOINT,
        "db.instance": connection.get_connection_params()["db"],
        "net.host.name": SpannerClient.DEFAULT_ENDPOINT,
    }

    if extra_attributes:
        attributes.update(extra_attributes)

    with tracer.start_as_current_span(
        name, kind=trace.SpanKind.CLIENT, attributes=attributes
    ) as span:
        try:
            yield span
        except GoogleAPICallError as error:
            if error.code is not None:
                span.set_status(
                    Status(http_status_to_canonical_code(error.code))
                )
            elif error.grpc_status_code is not None:
                span.set_status(
                    # OpenTelemetry's StatusCanonicalCode maps 1-1 with grpc status codes
                    Status(
                        StatusCanonicalCode(error.grpc_status_code.value[0])
                    )
                )
            raise
