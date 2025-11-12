# ZenCube Sandbox Makefile - Phase 2
# Provides convenient build targets for the sandbox project

CC = gcc
CFLAGS = -Wall -Wextra -std=c99
LDFLAGS = -lrt
TARGET = sandbox
SOURCE = sandbox.c
DEBUG_FLAGS = -g -DDEBUG
RELEASE_FLAGS = -O2 -DNDEBUG

# Test programs
TEST_DIR = tests
TEST_PROGRAMS = $(TEST_DIR)/infinite_loop $(TEST_DIR)/memory_hog $(TEST_DIR)/fork_bomb $(TEST_DIR)/file_size_test
TEST_SOURCES = $(TEST_DIR)/infinite_loop.c $(TEST_DIR)/memory_hog.c $(TEST_DIR)/fork_bomb.c $(TEST_DIR)/file_size_test.c

# Default target - build everything
all: $(TARGET) tests

# Build sandbox with standard flags
$(TARGET): $(SOURCE)
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCE) $(LDFLAGS)
	@echo "✅ Sandbox compiled successfully"

# Debug build with debugging symbols and debug output
debug: $(SOURCE)
	$(CC) $(CFLAGS) $(DEBUG_FLAGS) -o $(TARGET) $(SOURCE) $(LDFLAGS)
	@echo "✅ Debug build completed"

# Release build with optimizations
release: $(SOURCE)
	$(CC) $(CFLAGS) $(RELEASE_FLAGS) -o $(TARGET) $(SOURCE) $(LDFLAGS)
	@echo "✅ Release build completed"

# Build all test programs
tests: $(TEST_PROGRAMS)
	@echo "✅ All test programs compiled successfully"

# Build individual test programs
$(TEST_DIR)/infinite_loop: $(TEST_DIR)/infinite_loop.c
	$(CC) $(CFLAGS) -o $@ $<
	@echo "✅ Built infinite_loop test"

$(TEST_DIR)/memory_hog: $(TEST_DIR)/memory_hog.c
	$(CC) $(CFLAGS) -o $@ $<
	@echo "✅ Built memory_hog test"

$(TEST_DIR)/fork_bomb: $(TEST_DIR)/fork_bomb.c
	$(CC) $(CFLAGS) -o $@ $<
	@echo "✅ Built fork_bomb test"

$(TEST_DIR)/file_size_test: $(TEST_DIR)/file_size_test.c
	$(CC) $(CFLAGS) -o $@ $<
	@echo "✅ Built file_size_test"

# Run Phase 1 tests
test-phase1: $(TARGET)
	@echo "Running Phase 1 tests..."
	@chmod +x test_sandbox.sh
	@./test_sandbox.sh

# Run Phase 2 tests (resource limits)
test-phase2: $(TARGET) tests
	@echo "Running Phase 2 resource limit tests..."
	@chmod +x test_phase2.sh
	@./test_phase2.sh

# Run all tests
test: test-phase1 test-phase2
	@echo "✅ All tests completed"

# Clean build artifacts
clean:
	rm -f $(TARGET) $(TEST_PROGRAMS)
	rm -f test_output.dat
	@echo "✅ Cleaned build artifacts"

# Install to system (requires sudo)
install: $(TARGET)
	cp $(TARGET) /usr/local/bin/
	@echo "✅ Installed sandbox to /usr/local/bin/"

# Uninstall from system (requires sudo)
uninstall:
	rm -f /usr/local/bin/$(TARGET)
	@echo "✅ Uninstalled sandbox from /usr/local/bin/"

# Show help
help:
	@echo "ZenCube Sandbox Build System - Phase 2"
	@echo ""
	@echo "Available targets:"
	@echo "  all         - Build sandbox and test programs (default)"
	@echo "  sandbox     - Build only the sandbox"
	@echo "  tests       - Build only test programs"
	@echo "  debug       - Build with debug symbols"
	@echo "  release     - Build optimized release version"
	@echo "  test        - Run all test suites"
	@echo "  test-phase1 - Run Phase 1 tests only"
	@echo "  test-phase2 - Run Phase 2 resource limit tests"
	@echo "  clean       - Remove build artifacts"
	@echo "  install     - Install to /usr/local/bin (requires sudo)"
	@echo "  uninstall   - Remove from /usr/local/bin (requires sudo)"
	@echo "  help        - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make              # Build everything"
	@echo "  make tests        # Build test programs only"
	@echo "  make test-phase2  # Test resource limits"
	@echo "  make clean all    # Clean rebuild"
	@echo "  sudo make install # Install system-wide"

# Declare phony targets
.PHONY: all debug release tests test test-phase1 test-phase2 clean install uninstall help