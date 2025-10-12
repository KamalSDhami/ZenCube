# ZenCube - Development Notes & Architecture

## 🎨 System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                         User Interface                         │
│                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Execute    │  │   Monitor    │  │   History    │        │
│  │   Panel      │  │   Panel      │  │   Panel      │        │
│  │              │  │              │  │              │        │
│  │ • Command    │  │ • System     │  │ • Logs       │        │
│  │ • Limits     │  │   Metrics    │  │ • Stats      │        │
│  │ • Output     │  │ • Processes  │  │ • Export     │        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
│         │                  │                  │                │
│         └──────────────────┴──────────────────┘                │
│                            │                                   │
└────────────────────────────┼───────────────────────────────────┘
                             │
                   ┌─────────▼─────────┐
                   │   Main Window     │
                   │   (PySide6)       │
                   └─────────┬─────────┘
                             │
           ┌─────────────────┴─────────────────┐
           │                                   │
    ┌──────▼──────┐                    ┌──────▼──────┐
    │  Utils      │                    │  Resources  │
    │  Layer      │                    │  Layer      │
    ├─────────────┤                    ├─────────────┤
    │• Sandbox    │                    │• Icons      │
    │  Wrapper    │                    │• Themes     │
    │• Process    │                    │• Configs    │
    │  Monitor    │                    └─────────────┘
    │• Logger     │
    └──────┬──────┘
           │
           │ subprocess.Popen()
           │ JSON Communication
           │
    ┌──────▼──────────────────────────┐
    │   C Sandbox Core                │
    │   (sandbox_v2 executable)       │
    ├─────────────────────────────────┤
    │                                 │
    │  1. fork() → Create Process     │
    │  2. setrlimit() → Apply Limits  │
    │  3. execvp() → Run Command      │
    │  4. waitpid() → Monitor         │
    │  5. JSON Output → Results       │
    │                                 │
    └─────────────┬───────────────────┘
                  │
         ┌────────▼────────┐
         │  Linux Kernel   │
         │  - Process Mgmt │
         │  - Resource Ctl │
         │  - Signals      │
         └─────────────────┘
```

---

## 🔄 Execution Flow

### GUI Execution Path

```
User Input (Command + Limits)
    │
    ▼
ExecutionPanel.execute_command()
    │
    ▼
ExecutionWorker (QThread)
    │
    ▼
SandboxRunner.run()
    │
    ├─► Build command: [sandbox_v2, --cpu, N, --mem, M, ...]
    ├─► subprocess.Popen()
    │   │
    │   └─► C sandbox_v2 process
    │       │
    │       ├─► Parse arguments
    │       ├─► fork() → child process
    │       ├─► Child: setrlimit() + execvp()
    │       ├─► Parent: waitpid() + monitor
    │       └─► Output JSON
    │
    ├─► Parse JSON output
    └─► Return SandboxResult
        │
        ▼
ExecutionPanel._on_execution_finished()
    │
    ├─► Display results
    ├─► Log to ExecutionLogger
    └─► Emit signals
        │
        ▼
MainWindow updates
    ├─► History panel refresh
    └─► Status bar update
```

---

## 📊 Data Flow

### SandboxResult Object

```python
@dataclass
class SandboxResult:
    pid: int                        # Process ID
    exit_code: int                  # Exit status
    execution_time: float           # Seconds
    terminated_by_signal: bool      # Signal flag
    signal_number: Optional[int]    # Signal number
    signal_name: Optional[str]      # Signal name
    cpu_limit_exceeded: bool        # CPU limit
    memory_limit_exceeded: bool     # Memory limit
    timeout_exceeded: bool          # Timeout
    success: bool                   # Overall status
    output: str                     # stdout
    error: str                      # stderr
```

### JSON Communication Format

```json
{
  "pid": 12345,
  "exit_code": 0,
  "execution_time": 1.234,
  "terminated_by_signal": false,
  "signal_number": null,
  "signal_name": null,
  "limits": {
    "cpu_seconds": 5,
    "memory_mb": 256,
    "timeout_seconds": 10
  },
  "limit_exceeded": {
    "cpu": false,
    "memory": false,
    "timeout": false
  },
  "success": true
}
```

---

## 🧵 Threading Model

### Main Thread (GUI)
- Qt event loop
- UI updates
- User interactions
- Timer events (monitoring updates)

### Worker Threads
- **ExecutionWorker**: Runs sandbox commands
  - Prevents UI freezing
  - Signals back to main thread
  - Handles long-running processes

### Process Monitoring
- Separate from execution
- Periodic updates via QTimer
- Uses psutil in main thread (lightweight)

---

## 🔍 Code Organization

### ui/ Package

```
ui/
├── __init__.py              # Package exports
├── main_window.py           # Application window
│   └── MainWindow           # QMainWindow subclass
├── execution_panel.py       # Command execution
│   ├── ExecutionPanel       # QWidget subclass
│   └── ExecutionWorker      # QThread subclass
├── monitoring_panel.py      # Process monitoring
│   └── MonitoringPanel      # QWidget subclass
└── history_panel.py         # Execution logs
    └── HistoryPanel         # QWidget subclass
```

### utils/ Package

```
utils/
├── __init__.py              # Package exports
├── sandbox_wrapper.py       # C sandbox interface
│   ├── SandboxResult        # @dataclass
│   └── SandboxRunner        # Main wrapper class
├── process_monitor.py       # Process metrics
│   ├── ProcessMetrics       # @dataclass
│   ├── ProcessInfo          # @dataclass
│   └── ProcessMonitor       # Monitor class
└── logger.py                # Execution logging
    ├── ExecutionLog         # @dataclass
    └── ExecutionLogger      # Logger class
```

---

## 🎯 Design Decisions

### Why C for Core?

1. **Direct syscall access**: No Python overhead
2. **Educational value**: Learn low-level programming
3. **Performance**: Minimal execution overhead
4. **Kernel integration**: Resource limits require kernel APIs

### Why PySide6 for GUI?

1. **Rich widget library**: Professional UI components
2. **Cross-platform**: Qt works on Linux/Mac/Windows
3. **Python integration**: Easy to use Python libraries
4. **Modern look**: Native OS styling

### Why JSON for IPC?

1. **Human-readable**: Easy debugging
2. **Language-agnostic**: C → Python seamlessly
3. **Structured data**: Type-safe parsing
4. **Extensible**: Easy to add fields

---

## 🧪 Testing Strategy

### C Sandbox Tests

```bash
# Basic execution
./sandbox_v2 /bin/echo "test"

# CPU limit
./sandbox_v2 --cpu 2 /usr/bin/yes > /dev/null

# Memory limit
./sandbox_v2 --mem 50 python3 -c "x='a'*100000000"

# Timeout
./sandbox_v2 --timeout 3 /bin/sleep 10

# JSON output
./sandbox_v2 --json /bin/ls
```

### Python GUI Tests

1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test UI → Backend flow
3. **Manual Tests**: User interaction scenarios

---

## 🚀 Performance Optimization

### Current Optimizations

1. **Threading**: Non-blocking execution
2. **Efficient monitoring**: Minimal polling
3. **Lazy loading**: On-demand data fetching
4. **Limited history**: Cap at 1000 entries

### Future Optimizations

1. **Async I/O**: Use asyncio for subprocess
2. **Caching**: Cache process info
3. **Batch updates**: Group UI updates
4. **Database**: SQLite for large history

---

## 🔐 Security Hardening Roadmap

### Phase 3: Namespaces

```c
// PID namespace
unshare(CLONE_NEWPID);

// Mount namespace
unshare(CLONE_NEWNS);

// Network namespace
unshare(CLONE_NEWNET);
```

### Phase 4: Filesystem Isolation

```c
// chroot jail
chroot("/sandbox");
chdir("/");
```

### Phase 5: Syscall Filtering

```c
// seccomp-bpf
prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog);
```

---

## 📚 Learning Path

### Beginner
1. Understand fork/exec model
2. Learn process states
3. Explore resource limits
4. Build basic GUI

### Intermediate
1. Implement namespaces
2. Add filesystem isolation
3. Create network controls
4. Advanced GUI features

### Advanced
1. seccomp filters
2. cgroups integration
3. Custom schedulers
4. Distributed sandboxing

---

## 🤔 Common Questions

### Q: Why not use Docker?
**A**: Educational purposes. ZenCube teaches fundamentals that Docker abstracts away.

### Q: Is it production-ready?
**A**: No. Educational/testing only. Use Docker, Podman, or Firejail for production.

### Q: Can it run on Windows?
**A**: No. Requires Linux syscalls (fork, setrlimit, etc.).

### Q: Why Phase 2 instead of full containerization?
**A**: Progressive learning. Master basics before advanced features.

### Q: How does it compare to Docker?
**A**: Docker has namespaces, layered filesystem, image management, networking, etc. ZenCube is minimal.

---

## 🎓 Educational Value

### Concepts Demonstrated

1. **Operating Systems**
   - Process management
   - Resource allocation
   - System calls
   - Signal handling

2. **Systems Programming**
   - C programming
   - Error handling
   - Process control
   - Timing and measurement

3. **Software Engineering**
   - Modular design
   - API design
   - Testing strategies
   - Documentation

4. **GUI Development**
   - Event-driven programming
   - Threading
   - User experience
   - Real-time updates

---

## 📖 Recommended Reading

1. **"The Linux Programming Interface"** - Michael Kerrisk
2. **"Advanced Programming in the UNIX Environment"** - Stevens & Rago
3. **"Linux System Programming"** - Robert Love
4. **PySide6 Documentation** - Qt for Python
5. **Docker Internals** - Docker blog posts

---

## 🎉 Project Achievements

✅ Full-featured C sandbox with resource limits
✅ Modern Python GUI with PySide6
✅ Real-time process monitoring
✅ Comprehensive execution logging
✅ JSON-based IPC
✅ Complete documentation
✅ Test suite
✅ Educational value

---

**ZenCube** - *From syscalls to GUI, understand containerization!* 🧊
