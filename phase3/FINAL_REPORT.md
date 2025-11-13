# Task A – Final Report

## Overview
- Added a `--jail=<path>` flag to `zencube/sandbox.c`. When the sandbox runs as root the child process now chroots into the specified directory before executing the target command. Non-root runs emit a warning and skip the chroot call (per requirements) without aborting the execution.
- The new path validation (realpath + `stat` + `access`) surfaces configuration mistakes immediately, preventing half-configured jails from silently failing at runtime.
- Implemented `setup_chroot_jail()` helper for clarity and reuse. The helper ensures we `chdir` into the jail prior to `chroot(".")` and moves to `/` afterwards so relative paths behave predictably.

## Developer Tooling
- Delivered `monitor/jail_wrapper.py` to emulate the file jail without root access. It prefers `strace` to capture `open*` syscalls and falls back to `/proc/<pid>/fd` monitoring when `strace` is unavailable. Detected escapes trigger exit code `2` and are logged to JSON artefacts in `monitor/logs/`.
- Added `scripts/build_jail_dev.sh` to assemble a minimal non-root jail tree (`sandbox_jail/`) containing `/bin/sh`, its loader dependencies, and a stub `/etc/passwd`.
- Created `tests/test_jail_dev.sh` which builds the jail if needed, stages a proof-of-escape Python script, runs it through the wrapper, and asserts the wrapper fails with exit code `2` while logging `/etc/hosts`.

## Validation
- Test command: `./tests/test_jail_dev.sh`
- Result: PASS (wrapper exit code `2`, JSON log includes `/etc/hosts`). See `phase3/TEST_RUNS.md` for timestamped entry and `monitor/logs/jail_run_20251112T035719Z.json` for full trace.

## Limitations & Follow-ups
- Without root the wrapper cannot *prevent* the read, only detect and mark the run as failed. Production deployments must execute the sandbox binary with the new `--jail` flag under root to obtain a real chroot.
- The fallback `/proc` watcher is best-effort; it may miss extremely short-lived file descriptors when `strace` is absent. Documented in `phase3/NOTES.md` with guidance to install `strace` for stronger guarantees.
- Additional filesystem-hardening goals listed in the master checklist remain open (mount namespaces, read-only mounts, etc.) and are out of scope for this task.

## Artefacts
- Code: `zencube/sandbox.c`, `monitor/jail_wrapper.py`, `gui/file_jail_panel.py`, `zencube/zencube_modern_gui.py`
- Scripts: `scripts/build_jail_dev.sh`, `tests/test_jail_dev.sh`, `tests/test_gui_file_jail_py.sh`
- Documentation & Logs: `docs/GUI_FILE_JAIL.md`, `phase3/NOTES.md`, `phase3/TEST_RUNS.md`, `phase3/SCORES.md`, `monitor/logs/jail_run_*.json`

## GUI Work (in-progress)

- Replaced the experimental web JSX component with a native PySide6 panel (`gui/file_jail_panel.py`) that plugs into `zencube_modern_gui.py`.
- The panel exposes Enable/Enforce toggles, jail path picker, and Prepare/Run actions that execute the existing dev-safe scripts in background threads.
- Added a headless regression test `tests/test_gui_file_jail_py.sh` to exercise the panel logic without launching a full GUI and refreshed `docs/GUI_FILE_JAIL.md` accordingly.

# Task B – Network Restrictions Report

## Overview
- Introduced a `--no-net` flag to the sandbox. When supported, a seccomp filter blocks outbound socket syscalls and returns `EPERM`, keeping the target process alive yet networkless.
- Integrated a dev-safe Python wrapper (`monitor/net_wrapper.py`) that monkey-patches `socket` APIs, records blocked attempts in `monitor/logs/net_restrict_*.json`, and raises `PermissionError` without requiring root.
- Added a PySide6 Network panel so users can toggle network isolation beside the file jail controls. Dev-safe mode wraps commands automatically; enforce mode surfaces the exact `sudo sandbox --no-net ...` command string.
- Created `scripts/disable_network_dev.sh` as an optional helper to run commands inside an `unshare --net` namespace for experiments without touching global iptables configuration.

## Validation
- Test command: `./tests/test_network_restrict.sh`
- Result: PASS – sandbox run exited with non-zero status, and the latest `net_restrict_*.json` log contained at least one recorded violation. Entry recorded in `phase3/TEST_RUNS.md`.

## Limitations & Follow-ups
- Seccomp filters require kernels with `PR_SET_NO_NEW_PRIVS` support. When installation fails the sandbox logs a warning and relies on the Python wrapper; deeper coverage (e.g., non-Python binaries) will need future work such as network namespaces or iptables.
- The wrapper targets Python workloads. Native binaries still depend on the seccomp or namespace paths.
- Namespace helper currently assumes `unshare --user --map-root-user --net`; environments without user namespaces must fallback to the wrapper.

## Artefacts
- Code: `zencube/sandbox.c`, `monitor/net_wrapper.py`, `gui/network_panel.py`, `zencube/zencube_modern_gui.py`
- Scripts & Tests: `scripts/disable_network_dev.sh`, `tests/test_network_restrict.sh`
- Documentation & Logs: `docs/NETWORK_RESTRICTIONS.md`, `phase3/NOTES.md`, `phase3/TEST_RUNS.md`, `monitor/logs/net_restrict_*.json`

# Task C – Monitoring & Dashboard Report

## Overview
- Added a reusable sampler in `monitor/resource_monitor.py` that collects CPU, RSS memory, open file counts, and IO bytes for a target PID. The helper prefers `psutil` when installed and automatically falls back to `/proc` parsing, keeping development environments dependency-light.
- Extended the PySide6 application with a "Monitoring & Metrics" card (`gui/monitor_panel.py`) that can be armed for any execution. When enabled the panel streams live samples, highlights peaks, and provides a direct link to the JSONL log.
- Updated `CommandExecutor` to emit the sandbox PID on launch and taught `zencube_modern_gui.py` to wire the lifecycle events (start/finish/close) so monitoring is automatic and cleans up correctly.

## Enhancements (Phase 3)
- Embedded twin Matplotlib charts for CPU% and RSS MB with EWMA smoothing, rolling window controls, pause/resume, and mean/peak overlays. Chart updates now run on the GUI thread via a queued signal from the sampling worker.
- Introduced `monitor/log_rotate.py` and a GUI rotate button that compresses older JSONL logs into `monitor/logs/archive/` while keeping the latest runs on disk. Dry-run mode and CLI flags keep the helper dev-safe.
- Added `monitor/alert_manager.py` to evaluate threshold breaches (configurable via JSON) and surface alert badges in the GUI. Alerts append to `alerts.jsonl`, support acknowledgement, and persist context between runs.
- Delivered `monitor/prometheus_exporter.py` so operators can opt-in to a local metrics endpoint via `PROMETHEUS_ENABLED=true`. The exporter is off by default, guards missing dependencies, and exposes CPU/memory gauges keyed by run id.
- Created a dedicated monitoring CI workflow (`.github/workflows/monitoring-ci.yml`) that executes the shell regression suite headlessly on pull requests.

## Developer Tooling
- Created `tests/test_gui_monitoring_py.sh`, an offscreen Qt regression test that verifies logs are generated and at least one sample is captured for a short-lived Python process.
- Documented operator guidance in `docs/MONITORING_DASHBOARD.md`, covering sampling behaviour, artefact format, and future enhancements.

## Validation
- Test command: `QT_QPA_PLATFORM=offscreen bash tests/test_monitor_daemon.sh`
- Test command: `QT_QPA_PLATFORM=offscreen bash tests/test_gui_monitoring_py.sh`
- Test command: `bash tests/test_alerting.sh`
- Test command: `bash tests/test_log_rotate.sh`
- Test command: `bash tests/test_prom_exporter.sh`
- Result: All monitoring tests PASS. Headless GUI run produced `/monitor/logs/monitor_run_20251113T124526Z_10287.jsonl` with two samples and a summary record. Alerting and log rotation populated JSONL artefacts, and the Prometheus exporter exposed `zencube_cpu_percent`/`zencube_memory_rss_megabytes` metrics for `test-run`.

## Artefacts
- Code: `monitor/resource_monitor.py`, `monitor/log_rotate.py`, `monitor/alert_manager.py`, `monitor/prometheus_exporter.py`, `gui/monitor_panel.py`, `gui/_mpl_canvas.py`, `zencube/zencube_modern_gui.py`
- Tests: `tests/test_monitor_daemon.sh`, `tests/test_gui_monitoring_py.sh`, `tests/test_alerting.sh`, `tests/test_log_rotate.sh`, `tests/test_prom_exporter.sh`
- Documentation & Logs: `docs/MONITORING_DASHBOARD.md`, `phase3/TEST_RUNS.md`, `phase3/SCORES.md`, `monitor/logs/monitor_run_*.jsonl`, `monitor/logs/alerts.jsonl`, `monitor/logs/archive/*.gz`

