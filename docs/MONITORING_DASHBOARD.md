# Monitoring Dashboard (Task C)

## Overview
- Native PySide6 dashboard panel that visualises CPU, memory, and open file usage while the sandbox executes a command.
- Lightweight sampler implemented in `monitor/resource_monitor.py` (prefers `psutil`, falls back to `/proc`).
- JSON Lines artefacts written to `monitor/logs/monitor_run_*.jsonl` with `start`, `sample`, and `stop` entries for auditing.
- Phase 3 enhancements add live charts with EWMA smoothing, threshold alerting, log rotation helpers, and an optional Prometheus exporter.
- CI (`.github/workflows/monitoring-ci.yml`) runs headless GUI and monitoring regression suites on pull requests.

## Sampling Behaviour
- Sample interval is user-selectable (0.2s–5.0s) from the Monitoring panel.
- Each sample records timestamp (UTC ISO-8601), CPU percentage, RSS (bytes), optional VMS, thread count, open file descriptors, and IO counters when accessible.
- A summary line captures total samples, duration, peak CPU, peak RSS, and the target exit code.

## GUI Workflow
1. Toggle **Enable monitoring for executions** in the Monitoring card.
2. Launch a command from the main ZenCube window.
3. Once the sandbox process starts, the panel rotates old logs, attaches automatically, and streams the newest readings.
4. Live charts render raw and smoothed series while the sample console lists the latest entries.
5. When the command exits, the panel stops sampling, displays a summary, links to the generated JSONL log, and clears Prometheus metrics (if enabled).

## Real-Time Charts & Controls
- Two Matplotlib charts (CPU %, RSS MB) overlay:
  - Raw measurements (solid line)
  - EWMA smoothing (dashed line; configurable α 0.01–1.0)
  - Shaded min/max band plus dashed mean reference line
- Controls include:
  - Sample window selector (30/60/120 samples; default 60)
  - EWMA α spin box for smoothing strength
  - Pause/Resume button to freeze chart updates without stopping sampling
  - Tooltips showing latest raw/EWMA values, mean, and window range
- Latest sample summary mirrors chart values so headless runs can inspect them via the textual UI.

## Log Rotation
- The worker rotates logs on every activation, keeping the newest `KEEP_LAST_N` JSONL files (default 10) and gzipping older entries into `monitor/logs/archive/`.
- Manual rotation: press **Rotate Logs** in the Monitoring card to trigger compression immediately.
- CLI usage for external runs:
  ```bash
  python -m monitor.log_rotate --keep 10            # rotate using default log dir
  python -m monitor.log_rotate /tmp/logs --dry-run  # preview actions
  ```
- Rotation skips files it cannot safely read (e.g., in-use handles) and logs any skipped paths via the main GUI console.

## Alerts & Acknowledgements
- Thresholds defined in `monitor/alerting.json` (defaults shown below) control alert triggers:
  ```json
  { "cpu_pct_high": 90, "rss_mb_high": 500, "duration_sec": 3 }
  ```
- When CPU% or RSS MB remain above the configured threshold for the specified duration, the panel raises an alert.
- Active alerts increment the **Alerts (N)** badge and append entries to `monitor/logs/alerts.jsonl`.
- Click the badge to open the alert dialog, review details, and acknowledge individual alerts (acks persist to the log).

## Optional Prometheus Exporter
- Enable by setting `PROMETHEUS_ENABLED=true` (and optionally `PROMETHEUS_PORT=<port>`) before launching the GUI.
- Metrics served on `127.0.0.1:<port>/metrics`:
  - `zencube_cpu_percent{run_id="..."}`
  - `zencube_memory_rss_megabytes{run_id="..."}`
- Exporter is disabled by default to avoid exposing listeners unintentionally; keep deployments local or behind a firewall.

## Logs and Artefacts
- Logs reside under `monitor/logs/` with the pattern `monitor_run_<timestamp>_<pid>.jsonl`.
- Each run emits at least a `start` and `stop` event plus `sample` entries for longer executions.
- Alert events live in `monitor/logs/alerts.jsonl`; rotated monitoring logs move to `monitor/logs/archive/*.gz`.
- Artefacts remain JSONL for compatibility with `jq`, pandas, and other analytics tools.

## Testing
- `./tests/test_gui_monitoring_py.sh` (Qt offscreen) validates live sampling and log creation.
- `./tests/test_alerting.sh` checks CPU/RSS alert triggers and acknowledgement persistence.
- `./tests/test_log_rotate.sh` ensures archival keeps only the newest JSONL files.
- `./tests/test_prom_exporter.sh` (optional) hits the local metrics endpoint when the exporter is enabled.
- CI runs all of the above via `.github/workflows/monitoring-ci.yml` on every PR.

## Future Enhancements
- Expand alerting to cover IO throughput and open FD ceilings.
- Add export-to-CSV shortcuts for monitored runs.
- Surface Prometheus scrape status inside the GUI when enabled.
