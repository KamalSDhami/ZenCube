# ZenCube Testing Checklist

Use this checklist to systematically test all ZenCube features.

---

## 🔧 Pre-Testing Setup

- [ ] WSL2 installed and running (Windows users)
- [ ] Navigate to `ZenCube/zencube` directory
- [ ] GCC compiler available (`gcc --version`)
- [ ] Make utility available (`make --version`)

---

## 🏗️ Build Phase

### Clean Build
```bash
cd ZenCube/zencube
make clean
make all
```

**Checklist:**
- [ ] `make clean` completes without errors
- [ ] `make all` compiles successfully
- [ ] `sandbox` binary created
- [ ] All 4 test programs in `tests/` directory compiled:
  - [ ] `tests/infinite_loop`
  - [ ] `tests/memory_hog`
  - [ ] `tests/fork_bomb`
  - [ ] `tests/file_size_test`
- [ ] No compilation errors (warnings are OK)

---

## ✅ Phase 1 Tests: Basic Functionality

### Test 1.1: Help Message
```bash
./sandbox --help
```
**Expected:**
- [ ] Usage information displays
- [ ] Options listed (--cpu, --mem, --procs, --fsize)
- [ ] Examples shown
- [ ] No errors

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail

---

### Test 1.2: Basic Command Execution
```bash
./sandbox /bin/echo "Hello, ZenCube!"
```
**Expected:**
- [ ] "Hello, ZenCube!" printed
- [ ] Log shows "No resource limits applied"
- [ ] Child PID logged
- [ ] Exit status 0
- [ ] Execution time shown (~0.001-0.010 seconds)

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail

---

### Test 1.3: Directory Listing
```bash
./sandbox /bin/ls -la
```
**Expected:**
- [ ] Directory contents listed
- [ ] Process logs shown
- [ ] Exit status 0
- [ ] Timing information displayed

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail

---

### Test 1.4: System Information
```bash
./sandbox /usr/bin/uname -a
```
**Expected:**
- [ ] System information displayed
- [ ] Normal exit (status 0)
- [ ] Logs show process creation and completion

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail

---

### Test 1.5: Exit Status Capture
```bash
./sandbox /bin/false
echo "Exit code: $?"
```
**Expected:**
- [ ] Exit status 1 reported
- [ ] Sandbox captures and returns child's exit code
- [ ] Logs show normal exit with status 1

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail

---

### Test 1.6: Command with Arguments
```bash
./sandbox /bin/sleep 1
```
**Expected:**
- [ ] Sleeps for ~1 second
- [ ] Execution time approximately 1.0 seconds
- [ ] Exit status 0

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail

---

## ✅ Phase 2 Tests: Resource Limits

### Test 2.1: CPU Time Limit
```bash
timeout 10 ./sandbox --cpu=3 ./tests/infinite_loop
```
**Expected:**
- [ ] Log shows "CPU Time: 3 seconds"
- [ ] Process runs for approximately 3 seconds
- [ ] Process terminated by signal (SIGKILL or SIGXCPU)
- [ ] Warning about resource violation displayed
- [ ] Execution time ~3.0 seconds

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail

**Notes:** _____________________________________________________

---

### Test 2.2: CPU Limit with Non-CPU-Intensive Task
```bash
./sandbox --cpu=5 /bin/sleep 10
```
**Expected:**
- [ ] Sleeps for full 10 seconds
- [ ] CPU limit NOT triggered (sleep doesn't use CPU)
- [ ] Exit status 0
- [ ] Execution time ~10 seconds

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail

---

### Test 2.3: Memory Limit (Low)
```bash
timeout 10 ./sandbox --mem=50 ./tests/memory_hog
```
**Expected:**
- [ ] Log shows "Memory: 50 MB"
- [ ] Allocates chunks successfully up to limit
- [ ] `malloc() failed` message appears
- [ ] Total allocated close to 50 MB (e.g., 40-50 MB)
- [ ] Exit status 0 (graceful failure) OR killed by kernel

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail

**Allocated before failure:** _______ MB

---

### Test 2.4: Memory Limit (High)
```bash
timeout 10 ./sandbox --mem=256 ./tests/memory_hog
```
**Expected:**
- [ ] Log shows "Memory: 256 MB"
- [ ] Allocates more memory than Test 2.3
- [ ] Eventually hits limit or malloc fails
- [ ] Process completes or is killed

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail

---

### Test 2.5: Process Count Limit
```bash
timeout 10 ./sandbox --procs=10 ./tests/fork_bomb
```
**Expected:**
- [ ] Log shows "Processes: 10"
- [ ] Successfully creates some child processes
- [ ] `fork() failed` message appears (may be delayed in WSL)
- [ ] Total processes created logged
- [ ] No system freeze or crash

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail | ⚠️ WSL Limitation

**Note:** This test may not work as expected in WSL2 due to `RLIMIT_NPROC` limitations.

---

### Test 2.6: File Size Limit
```bash
timeout 15 ./sandbox --fsize=30 ./tests/file_size_test
```
**Expected:**
- [ ] Log shows "File Size: 30 MB"
- [ ] Writes chunks successfully (10, 20, 30 MB)
- [ ] Process terminated by signal 25 (SIGXFSZ)
- [ ] Warning: "File size limit exceeded"
- [ ] File size limit violation clearly reported

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail

---

### Test 2.7: Multiple Limits (CPU + Memory)
```bash
timeout 10 ./sandbox --cpu=5 --mem=50 ./tests/memory_hog
```
**Expected:**
- [ ] Both limits shown in log
- [ ] Memory limit likely triggers first
- [ ] Process completes or is killed
- [ ] Correct limit violation reported

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail

**Which limit triggered:** CPU ⬜ | Memory ⬜ | Both ⬜

---

### Test 2.8: All Limits Combined
```bash
./sandbox --cpu=10 --mem=256 --procs=5 --fsize=100 /bin/ls -la
```
**Expected:**
- [ ] All 4 limits shown in log
- [ ] Command executes normally (ls uses minimal resources)
- [ ] Exit status 0
- [ ] Directory listing shown

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail

---

### Test 2.9: Invalid Arguments
```bash
./sandbox --cpu=-5 /bin/ls
```
**Expected:**
- [ ] Error message about invalid CPU limit
- [ ] Usage information displayed
- [ ] Non-zero exit code
- [ ] No command execution

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail

---

### Test 2.10: Missing Command
```bash
./sandbox --cpu=5
```
**Expected:**
- [ ] Error: "No command specified"
- [ ] Usage information displayed
- [ ] Non-zero exit code

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail

---

## 🔄 Automated Test Suites

### Makefile Tests
```bash
make test
```
**Expected:**
- [ ] Phase 1 tests run
- [ ] Phase 2 tests run
- [ ] Test summary displayed
- [ ] Most/all tests pass

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail

**Test Results:** _____ / _____ passed

---

### Phase 2 Script
```bash
chmod +x test_phase2.sh
./test_phase2.sh
```
**Expected:**
- [ ] Colored output (if terminal supports it)
- [ ] All tests execute
- [ ] Pass/fail for each test
- [ ] Summary at end

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail

---

### Interactive Demo
```bash
chmod +x demo.sh
./demo.sh
```
**Expected:**
- [ ] Welcome message displayed
- [ ] Each demo runs sequentially
- [ ] Wait for user input between demos
- [ ] All demos complete successfully

**Status:** ⬜ Not Run | ✅ Pass | ❌ Fail

---

## 📊 Test Summary

### Phase 1 Results
- Total Tests: 6
- Passed: _____
- Failed: _____
- Success Rate: _____% 

### Phase 2 Results
- Total Tests: 10
- Passed: _____
- Failed: _____
- WSL Limitations: _____
- Success Rate: _____%

### Overall Results
- Total Tests: 16
- Passed: _____
- Failed: _____
- **Overall Success Rate: _____%**

---

## 🎯 Minimum Acceptance Criteria

For Phase 1 & 2 to be considered complete:
- [ ] At least 90% of tests pass
- [ ] All core features (CPU, memory, file limits) working
- [ ] No crashes or segmentation faults
- [ ] Clean compilation with no errors
- [ ] Documentation complete

---

## 📝 Testing Notes

**Date Tested:** __________________

**Environment:**
- OS: __________________ 
- WSL Version: __________________
- GCC Version: __________________

**Issues Encountered:**
___________________________________________________________________
___________________________________________________________________
___________________________________________________________________

**Additional Observations:**
___________________________________________________________________
___________________________________________________________________
___________________________________________________________________

---

## ✅ Sign-off

**Tested By:** __________________

**Date:** __________________

**Overall Status:** ⬜ Pass | ⬜ Fail | ⬜ Partial Pass

**Recommendation:**
⬜ Ready for Phase 3
⬜ Needs minor fixes
⬜ Needs major revision

---

**Notes:**
- ⬜ = Not tested/Not selected
- ✅ = Pass
- ❌ = Fail
- ⚠️ = Known limitation/Partial pass
