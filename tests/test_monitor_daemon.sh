#!/usr/bin/env bash
set -euo pipefail

# Sanity check: sampling a short-lived process produces at least one sample without raising.
python - <<'PY'
import subprocess
import time

from monitor.resource_monitor import MonitorError, ProcessInspector

proc = subprocess.Popen(["sleep", "1"])
try:
    inspector = ProcessInspector(proc.pid)
    time.sleep(0.2)
    sample = inspector.sample()
    assert sample.cpu_percent >= 0.0
    assert sample.memory_rss >= 0
except MonitorError as exc:
    raise AssertionError(f"Sampling failed: {exc}")
finally:
    proc.terminate()
    proc.wait()
PY
