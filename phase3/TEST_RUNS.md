# Task A – Test Runs

| Timestamp (UTC) | Command | Result Summary |
|----------------|---------|----------------|
| 2025-11-12T03:57:19Z | `./tests/test_jail_dev.sh` | PASS – wrapper returned 2 and log captured `/etc/hosts` violation |
| 2025-11-12T16:04:20Z | `./tests/test_gui_file_jail_py.sh` | PASS – PySide6 panel prepared jail and logged run via jail_wrapper |
| 2025-11-12T17:21:54Z | `./tests/test_network_restrict.sh` | PASS – sandbox exited non-zero and net_restrict log captured at least one blocked socket |
| 2025-11-13T03:16:51Z | `./tests/test_gui_monitoring_py.sh` | PASS – monitoring panel produced JSONL log with sample and summary records |

