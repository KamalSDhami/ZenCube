# ZenCube - Quick Reference Guide

## 🚀 Quick Commands

### Build
```bash
cd ZenCube/zencube
make                    # Build everything
make clean all          # Clean rebuild
make debug              # Debug build
make release            # Optimized build
```

### Test
```bash
make test               # Run all tests
make test-phase1        # Phase 1 tests only
make test-phase2        # Phase 2 tests only
./demo.sh               # Interactive demo
```

### Basic Usage
```bash
./sandbox <command>                           # No limits
./sandbox --cpu=5 <command>                   # CPU limit
./sandbox --mem=256 <command>                 # Memory limit
./sandbox --procs=10 <command>                # Process limit
./sandbox --fsize=100 <command>               # File size limit
./sandbox --cpu=5 --mem=256 <command>         # Multiple limits
```

## 📋 Test Cases Reference

### Windows (WSL2) Testing

#### Prerequisites
```powershell
# Check WSL version
wsl --status

# Navigate to project
cd "C:\Path\To\ZenCube\zencube"
```

#### Build Project
```powershell
# Clean and build
wsl make clean
wsl make all
```

#### Run Test Cases

**Test 1: Basic Execution (Phase 1)**
```powershell
wsl ./sandbox /bin/echo "Test Success"
```
Expected: Command executes, logs show process info, exit code 0

---

**Test 2: CPU Time Limit**
```powershell
wsl ./sandbox --cpu=3 ./tests/infinite_loop
```
Expected: Process killed after ~3 seconds, SIGKILL received

---

**Test 3: Memory Limit**
```powershell
wsl timeout 10 ./sandbox --mem=50 ./tests/memory_hog
```
Expected: malloc() fails around 40-50MB, graceful exit

---

**Test 4: File Size Limit**
```powershell
wsl timeout 10 ./sandbox --fsize=30 ./tests/file_size_test
```
Expected: SIGXFSZ after writing 30MB, violation logged

---

**Test 5: Process Limit**
```powershell
wsl timeout 10 ./sandbox --procs=10 ./tests/fork_bomb
```
Expected: fork() fails after limit (may vary in WSL)
Note: RLIMIT_NPROC has known WSL limitations

---

**Test 6: Multiple Limits**
```powershell
wsl timeout 10 ./sandbox --cpu=5 --mem=50 ./tests/memory_hog
```
Expected: Memory limit triggers first, process exits

---

**Test 7: Help Text**
```powershell
wsl ./sandbox --help
```
Expected: Usage information displays

---

### Linux/Native Testing

```bash
# Navigate to project
cd ZenCube/zencube

# Build
make clean all

# Test 1: Basic Execution
./sandbox /bin/ls -la
# Expected: Directory listing shown

# Test 2: CPU Limit
./sandbox --cpu=3 ./tests/infinite_loop
# Expected: Killed by SIGXCPU after 3 seconds

# Test 3: Memory Limit
timeout 10 ./sandbox --mem=50 ./tests/memory_hog
# Expected: malloc() fails near 50MB

# Test 4: Process Limit
timeout 10 ./sandbox --procs=10 ./tests/fork_bomb
# Expected: fork() fails after 10 processes

# Test 5: File Size Limit
timeout 10 ./sandbox --fsize=30 ./tests/file_size_test
# Expected: SIGXFSZ at 30MB

# Test 6: All Limits
./sandbox --cpu=10 --mem=256 --procs=5 --fsize=100 /bin/ls
# Expected: Normal execution with all limits set

# Test 7: Automated Suite
make test
# Expected: All tests pass with summary
```

## 📊 Expected Output Examples

### Successful Execution
```
[Sandbox] No resource limits applied (unlimited)
[Sandbox] Starting command: /bin/echo Hello
[Sandbox 14:30:25] Child PID: 12345
Hello
[Sandbox 14:30:25] Process exited normally with status 0
[Sandbox 14:30:25] Execution time: 0.005 seconds
```

### CPU Limit Violation
```
[Sandbox] Active resource limits:
  CPU Time: 3 seconds
[Sandbox] Starting command: ./tests/infinite_loop
Still running... counter: 1 billion
[Sandbox] Process terminated by signal 9 (Killed)
[Sandbox] Execution time before termination: 3.027 seconds
```

### Memory Limit Hit
```
[Sandbox] Active resource limits:
  Memory: 50 MB
Allocated chunk #1 (Total: 10 MB)
Allocated chunk #2 (Total: 20 MB)
Allocated chunk #3 (Total: 30 MB)
Allocated chunk #4 (Total: 40 MB)
malloc() failed after allocating 40 MB
[Sandbox] Process exited normally with status 0
```

### File Size Limit Violation
```
[Sandbox] Active resource limits:
  File Size: 30 MB
Wrote chunk #1 (Total: 10 MB)
Wrote chunk #2 (Total: 20 MB)
Wrote chunk #3 (Total: 30 MB)
[Sandbox] Process terminated by signal 25 (File size limit exceeded)
[Sandbox] ⚠️  RESOURCE LIMIT VIOLATED: File size limit exceeded
```

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| `sandbox: not found` | Run `make` to compile |
| `Permission denied` | Run `chmod +x sandbox` |
| `undefined reference to clock_gettime` | Use `make` (includes `-lrt`) |
| WSL tests fail | Ensure WSL2, not WSL1 |
| Process limit doesn't work | Known WSL limitation |

## 📁 File Structure

```
ZenCube/
├── README.md                    # This file
├── TEST_RESULTS.md              # Detailed test results
├── PHASE2_COMPLETE.md           # Phase 2 summary
└── zencube/
    ├── sandbox.c                # Main source code
    ├── sandbox                  # Compiled binary
    ├── Makefile                 # Build system
    ├── README.md                # Technical docs
    ├── demo.sh                  # Interactive demo
    ├── test_sandbox.sh          # Phase 1 tests
    ├── test_phase2.sh           # Phase 2 tests
    └── tests/
        ├── infinite_loop.c      # CPU test
        ├── memory_hog.c         # Memory test
        ├── fork_bomb.c          # Process test
        └── file_size_test.c     # File size test
```

## 🎯 Success Criteria

### Phase 1
- ✅ Executes commands successfully
- ✅ Captures exit codes
- ✅ Measures execution time
- ✅ Detects signals

### Phase 2
- ✅ CPU limits enforced
- ✅ Memory limits enforced
- ✅ File size limits enforced
- ✅ Violations detected and reported
- ✅ Multiple limits work together

## 📞 Quick Links

- **Full Documentation**: [README.md](README.md)
- **Test Results**: [TEST_RESULTS.md](TEST_RESULTS.md)
- **Phase 2 Details**: [PHASE2_COMPLETE.md](PHASE2_COMPLETE.md)
- **GitHub Repo**: https://github.com/KamalSDhami/ZenCube

---

**Last Updated**: October 12, 2025
