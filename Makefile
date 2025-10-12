# ZenCube Sandbox Makefile
# Provides convenient build targets for the sandbox project

CC = gcc
CFLAGS = -Wall -Wextra -std=c99
LDFLAGS = -lrt
TARGET = sandbox
TARGET_V2 = sandbox_v2
SOURCE = sandbox.c
SOURCE_V2 = sandbox_v2.c
DEBUG_FLAGS = -g -DDEBUG
RELEASE_FLAGS = -O2 -DNDEBUG

# Default target - build both versions
all: $(TARGET) $(TARGET_V2)

# Build sandbox with standard flags
$(TARGET): $(SOURCE)
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCE) $(LDFLAGS)
	@echo "✅ Sandbox (v1) compiled successfully"

# Build enhanced sandbox with resource limits
$(TARGET_V2): $(SOURCE_V2)
	$(CC) $(CFLAGS) -o $(TARGET_V2) $(SOURCE_V2) $(LDFLAGS)
	@echo "✅ Sandbox v2 (enhanced) compiled successfully"

# Debug build with debugging symbols and debug output
debug: $(SOURCE)
	$(CC) $(CFLAGS) $(DEBUG_FLAGS) -o $(TARGET) $(SOURCE) $(LDFLAGS)
	@echo "✅ Debug build completed"

# Release build with optimizations
release: $(SOURCE)
	$(CC) $(CFLAGS) $(RELEASE_FLAGS) -o $(TARGET) $(SOURCE) $(LDFLAGS)
	@echo "✅ Release build completed"

# Run tests
test: $(TARGET)
	@echo "Running ZenCube sandbox tests..."
	@chmod +x test_sandbox.sh
	@./test_sandbox.sh

# Clean build artifacts
clean:
	rm -f $(TARGET) $(TARGET_V2)
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
	@echo "ZenCube Sandbox Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  all       - Build sandbox (default)"
	@echo "  debug     - Build with debug symbols"
	@echo "  release   - Build optimized release version"
	@echo "  test      - Compile and run test suite"
	@echo "  clean     - Remove build artifacts"
	@echo "  install   - Install to /usr/local/bin (requires sudo)"
	@echo "  uninstall - Remove from /usr/local/bin (requires sudo)"
	@echo "  help      - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make              # Build sandbox"
	@echo "  make debug        # Build with debugging"
	@echo "  make test         # Build and test"
	@echo "  sudo make install # Install system-wide"

# Declare phony targets
.PHONY: all debug release test clean install uninstall help