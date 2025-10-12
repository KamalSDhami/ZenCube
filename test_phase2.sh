#!/bin/bash

##############################################################################
# ZenCube Phase 2 Test Script
# Tests resource limit enforcement (CPU, memory, processes, file size)
##############################################################################

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Print test header
print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Print test result
print_result() {
    local test_name=$1
    local result=$2
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Check if sandbox exists
if [ ! -f "./sandbox" ]; then
    echo -e "${RED}Error: sandbox binary not found. Please run 'make' first.${NC}"
    exit 1
fi

# Check if test programs exist
if [ ! -f "./tests/infinite_loop" ]; then
    echo -e "${RED}Error: test programs not found. Please run 'make tests' first.${NC}"
    exit 1
fi

echo -e "${YELLOW}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║        ZenCube Phase 2 - Resource Limit Test Suite          ║"
echo "║              Testing CPU, Memory, Process & File Limits       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

##############################################################################
# Test 1: CPU Time Limit
##############################################################################
print_header "Test 1: CPU Time Limit (RLIMIT_CPU)"

echo "Testing: CPU limit of 3 seconds on infinite loop..."
timeout 10 ./sandbox --cpu=3 ./tests/infinite_loop > /tmp/zencube_test_cpu.log 2>&1
EXIT_CODE=$?

# Check if process was killed by signal (exit code > 128 typically means signal)
if grep -q "SIGXCPU" /tmp/zencube_test_cpu.log || grep -q "CPU time limit exceeded" /tmp/zencube_test_cpu.log; then
    print_result "CPU limit enforcement" "PASS"
else
    print_result "CPU limit enforcement" "FAIL"
    echo "  Expected: Process killed by SIGXCPU"
    echo "  Output: $(cat /tmp/zencube_test_cpu.log | tail -5)"
fi

##############################################################################
# Test 2: Memory Limit
##############################################################################
print_header "Test 2: Memory Limit (RLIMIT_AS)"

echo "Testing: Memory limit of 100 MB on memory hog..."
timeout 10 ./sandbox --mem=100 ./tests/memory_hog > /tmp/zencube_test_mem.log 2>&1
EXIT_CODE=$?

# Check if memory allocation failed or process was killed
if grep -q "malloc() failed" /tmp/zencube_test_mem.log || grep -q "killed" /tmp/zencube_test_mem.log || [ $EXIT_CODE -ne 0 ]; then
    print_result "Memory limit enforcement" "PASS"
else
    print_result "Memory limit enforcement" "FAIL"
    echo "  Expected: malloc() failure or process kill"
    echo "  Output: $(cat /tmp/zencube_test_mem.log | tail -5)"
fi

##############################################################################
# Test 3: Process Count Limit
##############################################################################
print_header "Test 3: Process Count Limit (RLIMIT_NPROC)"

echo "Testing: Process limit of 10 on fork test..."
timeout 10 ./sandbox --procs=10 ./tests/fork_bomb > /tmp/zencube_test_proc.log 2>&1
EXIT_CODE=$?

# Check if fork failed
if grep -q "fork() failed" /tmp/zencube_test_proc.log; then
    print_result "Process limit enforcement" "PASS"
else
    print_result "Process limit enforcement" "FAIL"
    echo "  Expected: fork() should fail after limit"
    echo "  Output: $(cat /tmp/zencube_test_proc.log | tail -5)"
fi

##############################################################################
# Test 4: File Size Limit
##############################################################################
print_header "Test 4: File Size Limit (RLIMIT_FSIZE)"

echo "Testing: File size limit of 50 MB..."
timeout 15 ./sandbox --fsize=50 ./tests/file_size_test > /tmp/zencube_test_fsize.log 2>&1
EXIT_CODE=$?

# Check if file write failed or SIGXFSZ received
if grep -q "Write failed" /tmp/zencube_test_fsize.log || grep -q "SIGXFSZ" /tmp/zencube_test_fsize.log || grep -q "File size limit exceeded" /tmp/zencube_test_fsize.log; then
    print_result "File size limit enforcement" "PASS"
else
    print_result "File size limit enforcement" "FAIL"
    echo "  Expected: Write failure or SIGXFSZ"
    echo "  Output: $(cat /tmp/zencube_test_fsize.log | tail -5)"
fi

##############################################################################
# Test 5: Multiple Limits Combined
##############################################################################
print_header "Test 5: Multiple Limits Combined"

echo "Testing: CPU=5s + Memory=50MB limits..."
timeout 10 ./sandbox --cpu=5 --mem=50 ./tests/memory_hog > /tmp/zencube_test_multi.log 2>&1
EXIT_CODE=$?

# Should be killed by either CPU or memory limit
if [ $EXIT_CODE -ne 0 ]; then
    print_result "Multiple limits enforcement" "PASS"
else
    print_result "Multiple limits enforcement" "FAIL"
    echo "  Expected: Process should be killed"
fi

##############################################################################
# Test 6: Normal Process (No Limits)
##############################################################################
print_header "Test 6: Normal Process Execution (No Limits)"

echo "Testing: Normal ls command without limits..."
./sandbox /bin/ls -la > /tmp/zencube_test_normal.log 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    print_result "Normal execution without limits" "PASS"
else
    print_result "Normal execution without limits" "FAIL"
fi

##############################################################################
# Test 7: Help and Usage
##############################################################################
print_header "Test 7: Help and Command-Line Interface"

echo "Testing: --help flag..."
./sandbox --help > /tmp/zencube_test_help.log 2>&1
if grep -q "OPTIONS" /tmp/zencube_test_help.log && grep -q "cpu" /tmp/zencube_test_help.log; then
    print_result "Help message displays correctly" "PASS"
else
    print_result "Help message displays correctly" "FAIL"
fi

##############################################################################
# Test 8: Invalid Arguments
##############################################################################
print_header "Test 8: Error Handling"

echo "Testing: Invalid CPU limit..."
./sandbox --cpu=-5 /bin/ls > /tmp/zencube_test_error.log 2>&1
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    print_result "Invalid argument detection" "PASS"
else
    print_result "Invalid argument detection" "FAIL"
fi

##############################################################################
# Summary
##############################################################################
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}                    TEST SUMMARY                       ${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "Total Tests:  ${BLUE}$TESTS_TOTAL${NC}"
echo -e "Passed:       ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed:       ${RED}$TESTS_FAILED${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Cleanup
rm -f /tmp/zencube_test_*.log
rm -f test_output.dat

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Phase 2 complete.${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Please review the output above.${NC}"
    exit 1
fi
