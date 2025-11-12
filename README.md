# ZenCube 🧊

**A Lightweight Sandbox for Process Isolation and Resource Control**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://www.linux.org/)
[![Language](https://img.shields.io/badge/language-C-orange.svg)](https://en.wikipedia.org/wiki/C_(programming_language))
[![Phase](https://img.shields.io/badge/phase-2%20complete-green.svg)](#project-status)

---

## 📖 Table of Contents

- [Overview](#overview)
- [Project Status](#project-status)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [GUI Usage](#gui-usage)
- [Usage Guide](#usage-guide)
- [Testing](#testing)
- [Architecture](#architecture)
- [Project Roadmap](#project-roadmap)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## 🎯 Overview

**ZenCube** is an educational containerization project that demonstrates process isolation, resource management, and sandbox security concepts using low-level Linux system calls. Built in incremental phases, ZenCube provides a production-quality sandbox environment for safely executing untrusted code with enforced resource limits.

### Why ZenCube?

- **Zen** → Simplicity, focus, discipline (enforcing boundaries)
- **Cube** → Container, isolated space, structured environment
- **Together** → "A calm, contained box" = Perfect metaphor for sandboxing

### Use Cases

- 🔒 Execute untrusted code safely
- 🎓 Learn containerization concepts
- 🛡️ Prevent resource exhaustion attacks
- 🧪 Test applications with resource constraints
- 📚 Understand Linux process management

---

## 📊 Project Status

### Current Implementation

| Phase | Status | Completion |
|-------|--------|------------|
| **Phase 1** - Process Isolation | ✅ Complete | 100% |
| **Phase 2** - Resource Limits | ✅ Complete | 100% |
| **GUI** - Graphical Interface | ✅ Complete | 100% |
| **Phase 3** - Filesystem Restrictions | ⏳ Planned | 0% |
| **Phase 4** - Network Control | ⏳ Planned | 0% |
| **Phase 5** - Monitoring & Logging | ⏳ Planned | 0% |

**Last Updated**: October 12, 2025  
**Version**: 2.0  
**Branch**: `dev`

---

## ✨ Features

### Phase 1: Process Isolation ✅

- ✅ **Process Creation** - Creates isolated child processes using `fork()`
- ✅ **Command Execution** - Executes commands using `execvp()`
- ✅ **Process Monitoring** - Tracks process lifecycle with `waitpid()`
- ✅ **Execution Timing** - High-precision timing with `clock_gettime()`
- ✅ **Signal Handling** - Detects and reports signal termination
- ✅ **Exit Status Tracking** - Captures and reports exit codes
- ✅ **Professional Logging** - Timestamped logs with detailed information

### Phase 2: Resource Limits ✅

- ✅ **CPU Time Limits** - Prevent runaway processes (`RLIMIT_CPU`)
- ✅ **Memory Limits** - Cap address space usage (`RLIMIT_AS`)
- ✅ **Process Count Limits** - Prevent fork bombs (`RLIMIT_NPROC`)
- ✅ **File Size Limits** - Control file creation (`RLIMIT_FSIZE`)
- ✅ **Violation Detection** - Clear reporting when limits are exceeded
- ✅ **Flexible Configuration** - Command-line options for all limits
- ✅ **Multiple Limits** - Combine any limits simultaneously

---

## 💻 System Requirements

### Minimum Requirements

- **Operating System**: Linux (Ubuntu 18.04+, Debian 10+, or similar)
- **Compiler**: GCC 7.0+ with C99 support
- **Libraries**: POSIX real-time library (`librt`)
- **Memory**: 50MB minimum
- **Disk Space**: 10MB for project files

### Recommended Setup

- **OS**: Ubuntu 22.04 LTS or WSL2 on Windows 10/11
- **Compiler**: GCC 11.0+
- **Memory**: 256MB+ for testing
- **CPU**: Any modern x86_64 processor

### For Windows Users

- **WSL2** (Windows Subsystem for Linux 2) is required
- WSL1 is **not supported** due to system call limitations
- Install WSL2: `wsl --install` in PowerShell (Admin)

---

## 📦 Installation

### Step 1: Clone the Repository

```bash
# Using HTTPS
git clone https://github.com/KamalSDhami/ZenCube.git
cd ZenCube/zencube

# Or using SSH
git clone git@github.com:KamalSDhami/ZenCube.git
cd ZenCube/zencube
```

### Step 2: Install Dependencies (if needed)

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential gcc make

# Fedora/RHEL
sudo dnf install gcc make

# Arch Linux
sudo pacman -S gcc make
```

### Step 3: Build the Project

```bash
# Build sandbox and all test programs
make

# Or build individually
make sandbox    # Build sandbox only
make tests      # Build test programs only

# For debugging
make debug

# For optimized release
make release
```

### Step 4: Verify Installation

```bash
# Check if sandbox binary exists
ls -la sandbox

# Test basic functionality
./sandbox --help
```

---

## 🚀 Quick Start

### 1. Basic Execution (No Limits)

```bash
# Run a simple command
./sandbox /bin/echo "Hello, ZenCube!"

# List directory contents
./sandbox /bin/ls -la

# Check system information
./sandbox /usr/bin/uname -a
```

### 2. With Resource Limits

```bash
# CPU time limit of 5 seconds
./sandbox --cpu=5 /bin/sleep 10

# Memory limit of 256 MB
./sandbox --mem=256 ./myapp

# Multiple limits combined
./sandbox --cpu=10 --mem=512 --procs=5 ./application
```

### 3. Run Test Suite

```bash
# Run all tests
make test

# Run Phase 1 tests only
make test-phase1

# Run Phase 2 tests only
make test-phase2

# Interactive demo
chmod +x demo.sh
./demo.sh
```

---

## �️ GUI Usage

ZenCube now includes a **graphical user interface** for easier interaction without using the command line!

### Launching the GUI

```bash
# From the parent ZenCube directory
cd ..
python zencube_gui.py
```

### GUI Features

✨ **User-Friendly Interface** - No command line needed!  
📁 **File Browser** - Visually select executables  
⚡ **Quick Commands** - Pre-configured test buttons  
☑️ **Toggle Limits** - Enable/disable each limit individually  
🎯 **Preset Configurations** - Quick limit presets (None/Light/Medium/Strict)  
📺 **Live Terminal** - Real-time color-coded output  
⏹️ **Stop Button** - Terminate running processes  

### Quick GUI Tutorial

1. **Launch GUI**: `python zencube_gui.py`
2. **Select Command**: Click "Browse..." or use quick command buttons
3. **Configure Limits**: Check/uncheck limits, adjust values as needed
4. **Execute**: Click "▶ Execute Command"
5. **View Output**: Watch the terminal for real-time results

### GUI Presets

| Preset | Configuration | Use Case |
|--------|--------------|----------|
| **No Limits** | All disabled | Trusted code |
| **Light** | CPU:30s, Mem:1GB | Development |
| **Medium** | CPU:10s, Mem:512MB, Procs:10 | Testing |
| **Strict** | CPU:5s, Mem:256MB, Procs:5, File:50MB | Untrusted code |

📖 **For detailed GUI documentation, see:** [`GUI_USAGE.md`](../GUI_USAGE.md)

---

## �📚 Usage Guide

### Command-Line Syntax

```bash
./sandbox [OPTIONS] <command> [arguments...]
```

### Available Options

| Option | Description | Example | Default |
|--------|-------------|---------|---------|
| `--cpu=<seconds>` | Limit CPU time in seconds | `--cpu=5` | Unlimited |
| `--mem=<MB>` | Limit memory in megabytes | `--mem=256` | Unlimited |
| `--procs=<count>` | Limit number of processes | `--procs=10` | Unlimited |
| `--fsize=<MB>` | Limit file size in megabytes | `--fsize=100` | Unlimited |
| `--help` | Display help message | `--help` | N/A |

### Detailed Examples

#### Example 1: CPU Time Limit

Prevent infinite loops and CPU exhaustion:

```bash
# Allow maximum 3 seconds of CPU time
./sandbox --cpu=3 ./tests/infinite_loop
```

**Output:**
```
[Sandbox] Active resource limits:
  CPU Time: 3 seconds
[Sandbox] Starting command: ./tests/infinite_loop
Starting infinite loop...
[Sandbox] Process terminated by signal 9 (Killed)
[Sandbox] ⚠️  Process was killed (possibly by memory limit)
[Sandbox] Execution time before termination: 3.027 seconds
```

#### Example 2: Memory Limit

Prevent memory exhaustion:

```bash
# Allow maximum 100 MB of memory
./sandbox --mem=100 ./tests/memory_hog
```

**Output:**
```
[Sandbox] Active resource limits:
  Memory: 100 MB
Allocated chunk #1 (Total: 10 MB)
Allocated chunk #2 (Total: 20 MB)
...
malloc() failed after allocating 90 MB
This is expected when memory limit is enforced
```

#### Example 3: Process Limit

Prevent fork bombs:

```bash
# Allow maximum 10 processes
./sandbox --procs=10 ./tests/fork_bomb
```

**⚠️ WARNING**: Never run fork bomb tests without `--procs` limit!

#### Example 4: File Size Limit

Prevent disk space exhaustion:

```bash
# Allow maximum 50 MB file writes
./sandbox --fsize=50 ./tests/file_size_test
```

**Output:**
```
[Sandbox] Active resource limits:
  File Size: 50 MB
Wrote chunk #1 (Total: 10 MB)
...
[Sandbox] Process terminated by signal 25 (File size limit exceeded)
[Sandbox] ⚠️  RESOURCE LIMIT VIOLATED: File size limit exceeded
```

#### Example 5: Multiple Limits

Combine multiple limits for maximum security:

```bash
# Strict sandbox environment
./sandbox --cpu=10 --mem=128 --procs=5 --fsize=50 ./untrusted_app

# Web scraper with limits
./sandbox --cpu=30 --mem=512 python3 scraper.py

# Compile code safely
./sandbox --cpu=60 --mem=1024 gcc mycode.c -o mycode
```

#### Example 6: Real-World Use Cases

```bash
# Run student code submission
./sandbox --cpu=5 --mem=256 python3 student_submission.py

# Test potentially buggy application
./sandbox --cpu=10 --mem=512 --procs=3 ./buggy_app

# Generate reports with limits
./sandbox --cpu=120 --mem=1024 --fsize=500 ./report_generator

# Run untrusted script
./sandbox --cpu=30 --mem=256 --procs=1 bash untrusted_script.sh
```

---

## 🧪 Testing

### Overview

ZenCube includes comprehensive test suites for both Phase 1 and Phase 2 functionality.

### Test Programs Location

All test programs are in the `tests/` directory:

```
tests/
├── infinite_loop.c       # CPU limit testing
├── memory_hog.c          # Memory limit testing
├── fork_bomb.c           # Process limit testing
└── file_size_test.c      # File size limit testing
```

### Running Tests

#### Method 1: Using Makefile (Recommended)

```bash
# Build and run all tests
make test

# Run specific phase tests
make test-phase1    # Basic functionality tests
make test-phase2    # Resource limit tests

# Build test programs only (without running)
make tests
```

#### Method 2: Using Test Scripts

```bash
# Make scripts executable
chmod +x test_sandbox.sh test_phase2.sh demo.sh

# Run Phase 1 tests
./test_sandbox.sh

# Run Phase 2 tests
./test_phase2.sh

# Run interactive demo
./demo.sh
```

#### Method 3: Manual Testing

```bash
# Build everything first
make clean all

# Test 1: Basic Execution
./sandbox /bin/echo "Phase 1 Test"

# Test 2: CPU Limit
./sandbox --cpu=3 ./tests/infinite_loop

# Test 3: Memory Limit
./sandbox --mem=50 ./tests/memory_hog

# Test 4: Process Limit
./sandbox --procs=10 ./tests/fork_bomb

# Test 5: File Size Limit
./sandbox --fsize=30 ./tests/file_size_test

# Test 6: Multiple Limits
./sandbox --cpu=5 --mem=100 ./tests/memory_hog
```

### Expected Test Results

#### Phase 1 Tests

| Test | Command | Expected Result |
|------|---------|-----------------|
| Basic Execution | `./sandbox /bin/ls` | Exit code 0, files listed |
| Timing | `./sandbox /bin/sleep 1` | ~1 second execution time |
| Exit Status | `./sandbox /bin/false` | Exit code 1 captured |
| Signal Handling | `./sandbox /bin/kill $$` | Signal detected and logged |

#### Phase 2 Tests

| Test | Command | Expected Result |
|------|---------|-----------------|
| CPU Limit | `--cpu=3 ./tests/infinite_loop` | Killed after ~3 seconds |
| Memory Limit | `--mem=50 ./tests/memory_hog` | malloc() fails near 50MB |
| File Limit | `--fsize=30 ./tests/file_size_test` | SIGXFSZ after 30MB |
| Multiple Limits | `--cpu=5 --mem=50 ./tests/memory_hog` | Memory limit triggered |

### Understanding Test Output

#### Successful Execution
```
[Sandbox] No resource limits applied (unlimited)
[Sandbox] Starting command: /bin/echo Hello
[Sandbox 14:30:25] Child PID: 12345
Hello
[Sandbox 14:30:25] Process exited normally with status 0
[Sandbox 14:30:25] Execution time: 0.005 seconds
```

#### Resource Limit Violation
```
[Sandbox] Active resource limits:
  CPU Time: 3 seconds
[Sandbox] Starting command: ./tests/infinite_loop
[Sandbox 14:35:10] Child PID: 12350
Still running... counter: 1 billion
[Sandbox 14:35:13] Process terminated by signal 9 (Killed)
[Sandbox 14:35:13] ⚠️  Process was killed (possibly by memory limit)
[Sandbox 14:35:13] Execution time before termination: 3.027 seconds
```

### Test Troubleshooting

**Issue**: `Permission denied` when running tests  
**Solution**: `chmod +x test_sandbox.sh test_phase2.sh demo.sh`

**Issue**: `sandbox: command not found`  
**Solution**: Run `make` to build the sandbox binary

**Issue**: Test programs not found  
**Solution**: Run `make tests` to build test programs

**Issue**: Tests fail in WSL  
**Solution**: Ensure you're using WSL2 (check with `wsl --status`)

### Creating Custom Tests

You can create your own test programs:

```c
// my_test.c
#include <stdio.h>
#include <unistd.h>

int main() {
    printf("Custom test running...\n");
    sleep(2);
    printf("Test completed!\n");
    return 0;
}
```

Compile and run:
```bash
gcc -o my_test my_test.c
./sandbox --cpu=5 --mem=100 ./my_test
```

---

## 🏗️ Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        User Space                           │
│                                                             │
│  ┌──────────────┐                                          │
│  │   User       │                                          │
│  │   Command    │                                          │
│  └──────┬───────┘                                          │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────────────────────────────────────────────┐ │
│  │           ZenCube Sandbox (Parent Process)           │ │
│  │  - Parse arguments                                   │ │
│  │  - Setup resource limits                             │ │
│  │  - Fork child process                                │ │
│  │  - Monitor execution                                 │ │
│  │  - Report results                                    │ │
│  └──────────────┬───────────────────────────────────────┘ │
│                 │ fork()                                   │
│                 ▼                                          │
│  ┌──────────────────────────────────────────────────────┐ │
│  │        Child Process (Sandboxed)                     │ │
│  │  - Apply resource limits (setrlimit)                 │ │
│  │  - Execute target command (execvp)                   │ │
│  │  - Runs with constraints                             │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      Kernel Space                           │
│  - Enforce resource limits                                  │
│  - Send signals (SIGXCPU, SIGXFSZ)                         │
│  - Kill processes exceeding limits                          │
└─────────────────────────────────────────────────────────────┘
```

### Process Flow

1. **Argument Parsing**
   - Parse command-line options (`--cpu`, `--mem`, etc.)
   - Validate inputs
   - Store configuration

2. **Process Creation**
   - Call `fork()` to create child process
   - Parent and child processes diverge

3. **Child Process Setup**
   - Apply resource limits using `setrlimit()`
   - Log applied limits
   - Execute target command with `execvp()`

4. **Parent Process Monitoring**
   - Wait for child completion using `waitpid()`
   - Capture exit status
   - Measure execution time

5. **Result Analysis**
   - Check if process exited normally
   - Detect signal termination
   - Report resource limit violations
   - Display detailed logs

### System Calls Used

| System Call | Purpose | Phase |
|-------------|---------|-------|
| `fork()` | Create child process | 1 |
| `execvp()` | Execute command | 1 |
| `waitpid()` | Wait for child completion | 1 |
| `clock_gettime()` | High-precision timing | 1 |
| `setrlimit(RLIMIT_CPU)` | Set CPU time limit | 2 |
| `setrlimit(RLIMIT_AS)` | Set memory limit | 2 |
| `setrlimit(RLIMIT_NPROC)` | Set process limit | 2 |
| `setrlimit(RLIMIT_FSIZE)` | Set file size limit | 2 |

### Signal Handling

| Signal | Number | Meaning | Trigger |
|--------|--------|---------|---------|
| `SIGXCPU` | 24 | CPU time limit exceeded | `RLIMIT_CPU` violated |
| `SIGKILL` | 9 | Process killed | Memory limit or kernel kill |
| `SIGXFSZ` | 25 | File size limit exceeded | `RLIMIT_FSIZE` violated |
| `SIGTERM` | 15 | Termination request | User or system termination |

---

## 🗺️ Project Roadmap

### ✅ Phase 1: Foundations (Complete)

**Goal**: Basic sandbox with process isolation

- ✅ Process creation with `fork()`
- ✅ Command execution with `execvp()`
- ✅ Process monitoring with `waitpid()`
- ✅ Execution timing
- ✅ Signal detection
- ✅ Professional logging system

**Milestone**: Can launch and monitor processes safely

---

### ✅ Phase 2: Resource Limits (Complete)

**Goal**: Prevent resource exhaustion attacks

- ✅ CPU time limits (`RLIMIT_CPU`)
- ✅ Memory limits (`RLIMIT_AS`)
- ✅ Process count limits (`RLIMIT_NPROC`)
- ✅ File size limits (`RLIMIT_FSIZE`)
- ✅ Command-line configuration
- ✅ Violation detection and reporting
- ✅ Comprehensive test suite

**Milestone**: Sandbox enforces all resource limits

---

### ⏳ Phase 3: Filesystem Restrictions (Planned)

**Goal**: Control file system access

- [ ] Implement `chroot()` jail
- [ ] Read-only filesystem mounts
- [ ] Mount namespaces with `unshare(CLONE_NEWNS)`
- [ ] Isolated `/tmp` directories
- [ ] Directory whitelisting/blacklisting
- [ ] Test programs for filesystem isolation

**Milestone**: App runs in isolated directory tree

---

### ⏳ Phase 4: Network Control (Planned)

**Goal**: Network isolation and control

- [ ] Network namespace isolation
- [ ] Network on/off toggle
- [ ] Localhost-only mode
- [ ] Port restrictions
- [ ] Bandwidth limiting (optional)

**Milestone**: Sandbox supports network configuration

---

### ⏳ Phase 5: Monitoring & Logging (Planned)

**Goal**: Runtime monitoring and statistics

- [ ] Real-time resource usage tracking
- [ ] `/proc` filesystem monitoring
- [ ] Detailed violation logs
- [ ] Performance metrics
- [ ] JSON log output option

**Milestone**: Complete runtime visibility

---

### ⏳ Phase 6: GUI Dashboard (Planned)

**Goal**: User-friendly interface

- [ ] Command-line improvements
- [ ] Tkinter desktop GUI (optional)
- [ ] Flask web dashboard (optional)
- [ ] Real-time monitoring display
- [ ] Log visualization

**Milestone**: Usable interface beyond CLI

---

### ⏳ Phase 7: Advanced Features (Stretch Goals)

**Goal**: Production-grade features

- [ ] `seccomp` syscall filtering
- [ ] User namespaces
- [ ] OverlayFS snapshots
- [ ] Multi-sandbox orchestration
- [ ] Container registry integration

**Milestone**: Enterprise-ready sandbox system

---

## 🤝 Contributing

We welcome contributions! Here's how to get involved:

### Development Setup

```bash
# Fork the repository
git clone https://github.com/YOUR_USERNAME/ZenCube.git
cd ZenCube

# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes
# ... edit files ...

# Build and test
make clean all
make test

# Commit and push
git add .
git commit -m "Add: your feature description"
git push origin feature/your-feature-name

# Create a Pull Request on GitHub
```

### Contribution Guidelines

1. **Code Style**
   - Follow existing C code style
   - Use meaningful variable names
   - Add comments for complex logic
   - Keep functions focused and small

2. **Testing**
   - Add tests for new features
   - Ensure all existing tests pass
   - Test on multiple Linux distributions

3. **Documentation**
   - Update README for new features
   - Add usage examples
   - Document system calls used

4. **Commits**
   - Write clear commit messages
   - Reference issues if applicable
   - Keep commits atomic and focused

### Areas for Contribution

- 🐛 Bug fixes
- 📝 Documentation improvements
- ✨ New features (follow roadmap)
- 🧪 Additional test cases
- 🎨 Code optimizations
- 🌐 Platform support (BSD, etc.)

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Compilation Errors

**Error**: `undefined reference to 'clock_gettime'`

**Solution**: Ensure `-lrt` flag is used (Makefile handles this automatically)

```bash
gcc -o sandbox sandbox.c -lrt
```

---

**Error**: `sandbox.c: No such file or directory`

**Solution**: Navigate to the `zencube` directory

```bash
cd ZenCube/zencube
make
```

---

#### 2. Runtime Errors

**Error**: `./sandbox: Permission denied`

**Solution**: Set executable permissions

```bash
chmod +x sandbox
./sandbox --help
```

---

**Error**: `./sandbox: command not found`

**Solution**: Use relative or absolute path

```bash
./sandbox /bin/ls        # Relative path
/full/path/to/sandbox /bin/ls  # Absolute path
```

---

#### 3. WSL-Specific Issues

**Error**: Resource limits not working properly

**Solution**: Ensure you're using WSL2, not WSL1

```bash
# Check WSL version
wsl --status

# Upgrade to WSL2 if needed
wsl --set-default-version 2
```

---

**Error**: `bash: not found` when running test scripts

**Solution**: WSL might use different shell

```bash
# Try with sh
sh test_phase2.sh

# Or install bash
apt-get update && apt-get install bash
```

---

#### 4. Test Failures

**Error**: CPU test doesn't kill process

**Solution**: CPU limits apply to CPU time, not wall-clock time

```bash
# ✅ This works (infinite loop uses CPU)
./sandbox --cpu=3 ./tests/infinite_loop

# ❌ This won't trigger CPU limit (sleep doesn't use CPU)
./sandbox --cpu=3 /bin/sleep 10
```

---

**Error**: Process limit (RLIMIT_NPROC) not working

**Solution**: This is a known limitation in some environments

- `RLIMIT_NPROC` applies to entire user in some systems
- Works correctly on native Linux
- May not work as expected in Docker/WSL

---

#### 5. Memory Issues

**Error**: Memory test doesn't get killed

**Solution**: Memory limits work differently on different systems

- Some systems: `malloc()` fails gracefully
- Others: Process gets `SIGKILL`
- Both behaviors are correct

---

### Getting Help

If you encounter issues not covered here:

1. **Check Test Results**: Review `TEST_RESULTS.md`
2. **Read Documentation**: See `PHASE2_COMPLETE.md`
3. **Search Issues**: Check GitHub issues
4. **Ask Questions**: Open a new GitHub issue
5. **Debug**: Compile with `make debug` and use `gdb`

### Debug Mode

```bash
# Build with debug symbols
make debug

# Run with GDB
gdb ./sandbox

# GDB commands
(gdb) run --cpu=5 ./tests/infinite_loop
(gdb) break main
(gdb) step
(gdb) print variable_name
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary

✅ Commercial use  
✅ Modification  
✅ Distribution  
✅ Private use  
❌ Liability  
❌ Warranty  

---

## 👥 Authors

**Kamal Singh Dhami** - [@KamalSDhami](https://github.com/KamalSDhami)

**Systems Programming Team**

- Phase 1: September 2025
- Phase 2: October 2025

---

## 🙏 Acknowledgments

- Inspired by **Docker**, **Firejail**, and **LXC** containerization technologies
- Based on Linux system programming concepts
- Educational project for learning OS internals

### Learning Resources

- **Books**:
  - *Linux System Programming* by Robert Love
  - *The Linux Programming Interface* by Michael Kerrisk
  - *Understanding the Linux Kernel* by Bovet & Cesati

- **Man Pages**:
  - `man 2 fork`
  - `man 2 execvp`
  - `man 2 setrlimit`
  - `man 7 signal`

- **Online Resources**:
  - [Linux Kernel Documentation](https://www.kernel.org/doc/)
  - [POSIX Standards](https://pubs.opengroup.org/onlinepubs/9699919799/)

---

## 📞 Contact & Support

- **GitHub**: [@KamalSDhami](https://github.com/KamalSDhami)
- **Repository**: [ZenCube](https://github.com/KamalSDhami/ZenCube)
- **Issues**: [Report a Bug](https://github.com/KamalSDhami/ZenCube/issues)
- **Discussions**: [GitHub Discussions](https://github.com/KamalSDhami/ZenCube/discussions)

---

## 🌟 Project Stats

![GitHub stars](https://img.shields.io/github/stars/KamalSDhami/ZenCube?style=social)
![GitHub forks](https://img.shields.io/github/forks/KamalSDhami/ZenCube?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/KamalSDhami/ZenCube?style=social)

---

<div align="center">

**ZenCube** - *A calm, contained box for process execution* 🧊

Made with ❤️ for learning and education

[⬆ Back to Top](#zencube-)

</div>
