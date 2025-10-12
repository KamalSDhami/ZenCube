# 🧊 ZenCube Project Summary

## Overview

**ZenCube** is a lightweight, educational sandbox and process isolation framework for Linux. It combines low-level C system programming for the core sandbox with a modern Python GUI for user interaction.

### Version: 2.0 (Phase 2 Complete)

---

## 🎯 Project Goals

1. **Educational**: Teach Linux system programming and containerization concepts
2. **Practical**: Provide a working sandbox for testing and experimentation
3. **Modular**: Clean separation between C core and Python interface
4. **User-Friendly**: Modern GUI for accessibility

---

## 🏗️ Architecture

### Two-Tier Design

```
┌─────────────────────────────────────┐
│     Python GUI Layer (PySide6)      │
│  - User Interface                   │
│  - Process Monitoring               │
│  - History Tracking                 │
└────────────┬────────────────────────┘
             │ JSON Communication
             ▼
┌─────────────────────────────────────┐
│     C Sandbox Core                  │
│  - Process Isolation                │
│  - Resource Limits                  │
│  - System Calls                     │
└─────────────────────────────────────┘
```

---

## 📦 Components

### C Sandbox (`sandbox_v2.c`)

**Technology**: C with POSIX system calls

**Features**:
- Process isolation via `fork()`
- Command execution via `execvp()`
- CPU limits via `setrlimit(RLIMIT_CPU)`
- Memory limits via `setrlimit(RLIMIT_AS)`
- Timeout enforcement via `waitpid()` with polling
- JSON output for integration

**Key System Calls**:
- `fork()`: Create child process
- `execvp()`: Execute command
- `waitpid()`: Monitor process
- `setrlimit()`: Apply resource limits
- `kill()`: Terminate on timeout
- `clock_gettime()`: Measure execution time

### Python GUI (`ui/`)

**Technology**: PySide6 (Qt for Python)

**Components**:

1. **Main Window** (`main_window.py`)
   - Tabbed interface
   - Menu bar
   - Status bar with system metrics

2. **Execution Panel** (`execution_panel.py`)
   - Command input
   - Resource limit controls
   - Real-time output display
   - Preset commands

3. **Monitoring Panel** (`monitoring_panel.py`)
   - System metrics
   - Process list
   - Real-time updates
   - Top processes by memory

4. **History Panel** (`history_panel.py`)
   - Execution log table
   - Statistics dashboard
   - Detailed view
   - Export functionality

### Utilities (`utils/`)

1. **Sandbox Wrapper** (`sandbox_wrapper.py`)
   - Python interface to C sandbox
   - Command validation
   - JSON parsing
   - Result handling

2. **Process Monitor** (`process_monitor.py`)
   - Real-time process metrics
   - System resource tracking
   - Process history
   - Uses `psutil` library

3. **Logger** (`logger.py`)
   - Execution history storage
   - Statistics calculation
   - JSON persistence
   - Export functionality

---

## 🔧 Technical Details

### Resource Limits Implementation

**CPU Limit**:
```c
struct rlimit limit;
limit.rlim_cur = cpu_seconds;
limit.rlim_max = cpu_seconds;
setrlimit(RLIMIT_CPU, &limit);
```
- Enforced by kernel
- Sends SIGXCPU when exceeded
- Accurate to the second

**Memory Limit**:
```c
struct rlimit limit;
limit.rlim_cur = memory_mb * 1024 * 1024;
limit.rlim_max = memory_mb * 1024 * 1024;
setrlimit(RLIMIT_AS, &limit);
```
- Limits address space
- Malloc fails when exceeded
- Prevents memory exhaustion

**Timeout**:
```c
while (timeout_count < timeout_seconds) {
    wait_result = waitpid(child_pid, &status, WNOHANG);
    if (wait_result > 0) break;
    sleep(1);
    timeout_count++;
}
if (timeout_count >= timeout_seconds) {
    kill(child_pid, SIGKILL);
}
```
- Parent process enforced
- Polls every second
- Kills with SIGKILL when exceeded

### JSON Output Format

```json
{
  "pid": 12345,
  "exit_code": 0,
  "execution_time": 0.123,
  "terminated_by_signal": false,
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

## 📊 Features Matrix

| Feature | Phase 1 | Phase 2 | Phase 3 (Future) |
|---------|---------|---------|------------------|
| Process Isolation | ✅ | ✅ | ✅ |
| CPU Limits | ❌ | ✅ | ✅ |
| Memory Limits | ❌ | ✅ | ✅ |
| Timeout | ❌ | ✅ | ✅ |
| JSON Output | ❌ | ✅ | ✅ |
| Python GUI | ❌ | ✅ | ✅ |
| Process Monitoring | ❌ | ✅ | ✅ |
| Execution History | ❌ | ✅ | ✅ |
| Namespaces | ❌ | ❌ | 🚧 |
| Filesystem Isolation | ❌ | ❌ | 🚧 |
| Network Isolation | ❌ | ❌ | 🚧 |
| seccomp Filtering | ❌ | ❌ | 🚧 |

---

## 🎓 Learning Outcomes

### Systems Programming Concepts

1. **Process Management**
   - Fork-exec model
   - Process lifecycle
   - Parent-child relationships
   - Zombie processes

2. **Resource Management**
   - Linux resource limits
   - Memory management
   - CPU scheduling
   - Time measurement

3. **Inter-Process Communication**
   - Exit codes
   - Signals
   - JSON data exchange
   - Subprocess management

4. **Error Handling**
   - System call failures
   - Signal handling
   - Graceful degradation
   - User feedback

### GUI Development

1. **Qt Framework**
   - Widget hierarchy
   - Signal-slot mechanism
   - Threading model
   - Event handling

2. **Application Architecture**
   - MVC pattern
   - Separation of concerns
   - Modular design
   - Code organization

3. **User Experience**
   - Responsive interface
   - Real-time updates
   - Visual feedback
   - Error messaging

---

## 🔬 Testing Strategy

### Unit Testing

**C Sandbox**:
- Command execution
- Resource limit enforcement
- Error handling
- JSON output format

**Python Components**:
- Sandbox wrapper
- Process monitoring
- Logger functionality
- UI components

### Integration Testing

- C sandbox + Python wrapper
- GUI + backend communication
- Real-time monitoring
- History persistence

### Manual Testing

Test script (`test_sandbox.sh`):
- Basic execution
- CPU limits
- Memory limits
- Timeout enforcement
- Error conditions

---

## 📈 Performance

### C Sandbox Overhead

- **Fork**: ~0.1-1 ms
- **Exec**: ~1-5 ms
- **Resource Limit Setup**: <0.1 ms
- **Total Overhead**: ~1-6 ms

### Python GUI Performance

- **Startup Time**: ~1-2 seconds
- **UI Responsiveness**: <100 ms
- **Monitoring Update**: Every 2-3 seconds
- **Memory Usage**: ~50-100 MB

---

## 🔒 Security Considerations

### Current Implementation

**Limitations**:
- No namespace isolation
- No filesystem restrictions
- No network filtering
- Root processes can escape limits
- Signal-based enforcement bypassable

**Safe For**:
- Educational environments
- Local testing
- Development VMs
- Controlled experiments

**NOT Safe For**:
- Production workloads
- Untrusted code
- Multi-tenant systems
- Security-critical applications

### Phase 3 Enhancements

Planned security improvements:
- Linux namespaces (PID, Mount, Network)
- Filesystem chroot
- seccomp syscall filtering
- Capability dropping
- AppArmor/SELinux profiles

---

## 📚 Code Statistics

### C Sandbox
- **Lines of Code**: ~450
- **Functions**: 8
- **System Calls**: 10+
- **Complexity**: Moderate

### Python Code
- **Lines of Code**: ~1,500
- **Modules**: 7
- **Classes**: 10+
- **Complexity**: Moderate-High

---

## 🎯 Use Cases

### Educational

- **OS Courses**: Process management, resource limits
- **Systems Programming**: Low-level APIs, C programming
- **Security**: Sandboxing, isolation techniques
- **GUI Development**: Desktop application design

### Practical

- **Testing**: Run untrusted code safely
- **Benchmarking**: Measure resource usage
- **Development**: Debug resource issues
- **Demonstrations**: Show OS concepts

---

## 🚀 Future Roadmap

### Phase 3: Advanced Isolation

1. **Namespaces**
   - PID namespace (process isolation)
   - Mount namespace (filesystem)
   - Network namespace (network stack)
   - UTS namespace (hostname)

2. **Filesystem Isolation**
   - chroot implementation
   - Read-only mounts
   - Temporary filesystems
   - Bind mounts

3. **Network Control**
   - Network on/off
   - Port restrictions
   - Traffic monitoring
   - Virtual interfaces

4. **Advanced Security**
   - seccomp-bpf filters
   - Capability management
   - AppArmor profiles
   - Audit logging

### Phase 4: Enhanced Features

1. **GUI Improvements**
   - Real-time graphs
   - Resource visualizations
   - Configuration profiles
   - Command templates

2. **API Development**
   - REST API
   - WebSocket support
   - Remote execution
   - Cluster management

3. **Performance**
   - cgroups v2 integration
   - Better resource accounting
   - Parallel execution
   - Result caching

---

## 🤝 Contributing

Areas for contribution:
- Phase 3 feature implementation
- Test coverage expansion
- Documentation improvements
- Bug fixes and optimizations
- GUI enhancements
- Platform support (BSD, etc.)

---

## 📖 References

### Documentation
- Linux man pages (fork, exec, setrlimit)
- POSIX standards
- PySide6 documentation
- Container internals

### Similar Projects
- Docker
- Firejail
- systemd-nspawn
- LXC/LXD
- Podman

### Learning Resources
- "The Linux Programming Interface" by Michael Kerrisk
- "Advanced Programming in the UNIX Environment" by Stevens
- Linux kernel documentation
- Qt documentation

---

## 📄 License

MIT License - Free for educational and personal use

---

## ✨ Acknowledgments

Built as an educational project to demonstrate:
- Linux systems programming
- Process isolation
- Resource management
- Modern GUI development
- Software architecture

---

**ZenCube** - *Understanding containerization from first principles* 🧊
