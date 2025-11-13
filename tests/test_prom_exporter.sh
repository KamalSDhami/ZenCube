#!/usr/bin/env bash
set -euo pipefail

TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

export MONITOR_LOG_DIR="$TMP_DIR"
export PROMETHEUS_ENABLED=true
export PROMETHEUS_PORT=9209

python - <<'PY'
import os
import time
import urllib.request

from monitor.prometheus_exporter import PrometheusExporter
from monitor.resource_monitor import Sample

exporter = PrometheusExporter.from_env()
assert exporter.is_enabled(), "Exporter should be enabled when PROMETHEUS_ENABLED is true"
exporter.start()

sample = Sample(
    timestamp="2025-11-13T00:00:00Z",
    cpu_percent=42.0,
    memory_rss=int(256 * 1024 * 1024),
    memory_vms=None,
    threads=4,
    open_files=None,
    read_bytes=None,
    write_bytes=None,
)
exporter.record_sample("test-run", sample)

time.sleep(0.2)
port = int(os.environ.get("PROMETHEUS_PORT", "9209"))
with urllib.request.urlopen(f"http://127.0.0.1:{port}/metrics", timeout=5) as response:
    metrics = response.read().decode("utf-8")

assert "zencube_cpu_percent" in metrics
assert "test-run" in metrics

exporter.clear_run("test-run")
PY
