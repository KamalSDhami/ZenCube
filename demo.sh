#!/bin/bash

###############################################################################
# ZenCube Quick Demo Script
# Demonstrates all Phase 2 resource limit features
###############################################################################

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║              ZenCube Phase 2 - Quick Demo                    ║"
echo "║         Resource Limits: CPU, Memory, Processes, Files        ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "./sandbox" ]; then
    echo "❌ Error: sandbox binary not found."
    echo "Please run 'make' first to build the project."
    exit 1
fi

if [ ! -f "./tests/infinite_loop" ]; then
    echo "❌ Error: test programs not found."
    echo "Please run 'make tests' to build test programs."
    exit 1
fi

echo "✅ All binaries found. Starting demo..."
echo ""

###############################################################################
# Demo 1: Basic Sandbox (No Limits)
###############################################################################
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Demo 1: Basic Sandbox - No Resource Limits"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Running: ./sandbox /bin/ls -la"
echo ""
./sandbox /bin/ls -la
echo ""
read -p "Press Enter to continue..."
echo ""

###############################################################################
# Demo 2: CPU Time Limit
###############################################################################
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Demo 2: CPU Time Limit"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Running: ./sandbox --cpu=3 ./tests/infinite_loop"
echo "Expected: Process killed by SIGXCPU after ~3 seconds"
echo ""
timeout 10 ./sandbox --cpu=3 ./tests/infinite_loop
echo ""
read -p "Press Enter to continue..."
echo ""

###############################################################################
# Demo 3: Memory Limit
###############################################################################
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Demo 3: Memory Limit"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Running: ./sandbox --mem=100 ./tests/memory_hog"
echo "Expected: malloc() fails when trying to exceed 100 MB"
echo ""
timeout 10 ./sandbox --mem=100 ./tests/memory_hog
echo ""
read -p "Press Enter to continue..."
echo ""

###############################################################################
# Demo 4: Process Count Limit
###############################################################################
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Demo 4: Process Count Limit (Fork Bomb Prevention)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Running: ./sandbox --procs=10 ./tests/fork_bomb"
echo "Expected: fork() fails after creating 10 processes"
echo ""
timeout 10 ./sandbox --procs=10 ./tests/fork_bomb
echo ""
read -p "Press Enter to continue..."
echo ""

###############################################################################
# Demo 5: File Size Limit
###############################################################################
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Demo 5: File Size Limit"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Running: ./sandbox --fsize=30 ./tests/file_size_test"
echo "Expected: Write fails or SIGXFSZ when exceeding 30 MB"
echo ""
timeout 15 ./sandbox --fsize=30 ./tests/file_size_test
echo ""
read -p "Press Enter to continue..."
echo ""

###############################################################################
# Demo 6: Multiple Limits Combined
###############################################################################
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Demo 6: Multiple Limits Combined"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Running: ./sandbox --cpu=5 --mem=50 --procs=5 ./tests/memory_hog"
echo "Expected: Killed by either CPU or memory limit"
echo ""
timeout 10 ./sandbox --cpu=5 --mem=50 --procs=5 ./tests/memory_hog
echo ""
read -p "Press Enter to continue..."
echo ""

###############################################################################
# Demo 7: Help Text
###############################################################################
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Demo 7: Help and Usage Information"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Running: ./sandbox --help"
echo ""
./sandbox --help
echo ""

###############################################################################
# Summary
###############################################################################
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                      Demo Complete!                          ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Phase 2 Features Demonstrated:"
echo "  ✅ CPU time limits (RLIMIT_CPU)"
echo "  ✅ Memory limits (RLIMIT_AS)"
echo "  ✅ Process count limits (RLIMIT_NPROC)"
echo "  ✅ File size limits (RLIMIT_FSIZE)"
echo "  ✅ Multiple limits combined"
echo "  ✅ Violation detection and reporting"
echo ""
echo "To run the full test suite:"
echo "  make test"
echo ""
echo "To run Phase 2 tests only:"
echo "  make test-phase2"
echo ""
echo "For more information:"
echo "  cat README.md"
echo "  cat PHASE2_COMPLETE.md"
echo ""
