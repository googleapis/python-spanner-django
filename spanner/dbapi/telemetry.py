# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

import os
import time

from opencensus.ext.ocagent import stats_exporter
from opencensus.stats import (
    aggregation as aggregation_module, measure as measure_module,
    stats as stats_module, view as view_module,
)
from opencensus.tags import (
    tag_key as tag_key_module, tag_map as tag_map_module,
    tag_value as tag_value_module,
)

# Create the measures
# The latency in milliseconds
m_latency_ms = measure_module.MeasureFloat(
        "spanner/latency",
        "The latency in milliseconds per method",
        "ms")

m_object_lifetime_ms = measure_module.MeasureFloat(
        "spanner/object_lifetime",
        "The lifetime of various objects in milliseconds",
        "ms")

# The stats recorder
stats_recorder = stats_module.stats.stats_recorder

key_status = tag_key_module.TagKey("status")
key_error = tag_key_module.TagKey("error")
key_classification = tag_key_module.TagKey("class")
key_object = tag_key_module.TagKey("object")
key_pid = tag_key_module.TagKey("pid")
status_OK = tag_value_module.TagValue("OK")
status_ERROR = tag_value_module.TagValue("ERROR")
tag_value_PID = '%d' % os.getpid()
tag_value_object_CONNECTION = tag_value_module.TagValue("spanner.dbapi.Connection")
tag_value_object_CURSOR = tag_value_module.TagValue("spanner.dbapi.Cursor")


def registerAllViews(vmgr):
    latency_view = view_module.View(
        "latency", "The distribution of the latencies",
        [key_classification, key_status, key_error, key_pid],
        m_latency_ms,
        # Latency in buckets:
        # [>=0ms, >=25ms, >=50ms, >=75ms, >=100ms, >=200ms, >=400ms, >=600ms, >=800ms, >=1s, >=2s, >=4s, >=6s)
        aggregation_module.DistributionAggregation([1, 25, 50, 75, 100, 200, 400, 600, 800, 1000, 2000, 4000, 6000]))
    vmgr.register_view(latency_view)

    lifetime_view = view_module.View(
        "lifetime", "The distribution of lifetimes",
        [key_object, key_error, key_status, key_pid],
        m_object_lifetime_ms,
        # [>=0ms, >=50ms, >=200ms, >=800ms, >=2s, >=5s, >=10s, >=20s, >=50s, >=1m40sec, >=3m20s, >=8m20s, >=16m40s)
        aggregation_module.DistributionAggregation([1, 50, 2e2, 8e2, 2e3, 5e3, 1e4, 2e4, 5e4, 1e5, 2e5, 5e5, 1e6]))
    vmgr.register_view(lifetime_view)


def timed_do(classification_str, fn, *args, **kwargs):
    start = time.time()
    mm = stats_recorder.new_measurement_map()

    err = ''

    try:
        return fn(*args, **kwargs)
    except Exception as e:
        err = e
    finally:
        tm = tag_map_module.TagMap()
        tm.insert(key_classification, tag_value_module.TagValue(classification_str))
        tm.insert(key_pid, tag_value_PID)

        if not err:
            tm.insert(key_status, status_OK)
        else:
            tm.insert(key_error, tag_value_module.TagValue('%s' % err))
            tm.insert(key_status, status_ERROR)

        mm.measure_float_put(m_latency_ms, (time.time() - start) * 1000.0)
        mm.record(tm)

        if err:
            raise err


def record_connection_lifetime(start_time_sec, ending_exception):
    record_lifetime(tag_value_object_CONNECTION, start_time_sec, ending_exception)


def record_cursor_lifetime(start_time_sec, ending_exception):
    record_lifetime(tag_value_object_CURSOR, start_time_sec, ending_exception)


def record_lifetime(tag_value, start_time_sec, ending_exception):
    lifetime_ms = (time.time() - start_time_sec) * 1000.0
    mm = stats_recorder.new_measurement_map()
    tm = tag_map_module.TagMap()
    tm.insert(key_pid, tag_value_PID)
    tm.insert(key_object, tag_value)

    if not ending_exception:
        tm.insert(key_status, status_OK)
    else:
        tm.insert(key_error, tag_value_module.TagValue('%s' % (ending_exception)))
        tm.insert(key_status, status_ERROR)

    mm.measure_float_put(m_object_lifetime_ms, lifetime_ms)
    mm.record(tm)


def register_all(service_name):
    view_manager = stats_module.stats.view_manager
    view_manager.register_exporter(
        stats_exporter.new_stats_exporter(
            service_name=service_name,
            endpoint='localhost:55678',
            interval=5))
    registerAllViews(view_manager)
