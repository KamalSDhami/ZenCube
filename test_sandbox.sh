#!/bin/bash

# ZenCube Sandbox Test Suite
# Tests various aspects of the sandbox implementation

echo "=== ZenCube Sandbox Test Suite ==="
echo "Testing sandbox functionality..."
echo

# Compile the sandbox first
echo "1. Compiling sandbox..."
gcc -Wall -Wextra -g -o sandbox sandbox.c -lrt

if [ $? -ne 0 ]; then
    echo "❌ Compilation failed!"
    exit 1
fi
echo "✅ Compilation successful"
echo

# Test 1: Basic command execution
echo "2. Testing basic command execution..."
./sandbox /bin/echo "Hello from ZenCube!"
if [ $? -eq 0 ]; then
    echo "✅ Basic execution test passed"
else
    echo "❌ Basic execution test failed"
fi
echo

# Test 2: Command with arguments
echo "3. Testing command with arguments..."
./sandbox /bin/ls -la /tmp > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Arguments test passed"
else
    echo "❌ Arguments test failed"
fi
echo

# Test 3: Timing functionality
echo "4. Testing timing functionality..."
echo "Running sleep command to test timing..."
./sandbox /bin/sleep 1
if [ $? -eq 0 ]; then
    echo "✅ Timing test passed"
else
    echo "❌ Timing test failed"
fi
echo

# Test 4: Error handling - invalid command
echo "5. Testing error handling with invalid command..."
./sandbox /nonexistent/command 2>/dev/null
if [ $? -ne 0 ]; then
    echo "✅ Error handling test passed"
else
    echo "❌ Error handling test failed"
fi
echo

# Test 5: No arguments
echo "6. Testing no arguments error handling..."
./sandbox 2>/dev/null
if [ $? -ne 0 ]; then
    echo "✅ No arguments test passed"
else
    echo "❌ No arguments test failed"
fi
echo

# Test 6: Complex command with shell
echo "7. Testing complex command execution..."
./sandbox /bin/sh -c "whoami && date" > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Complex command test passed"
else
    echo "❌ Complex command test failed"
fi
echo

echo "=== Test Suite Complete ==="
echo "All tests finished. Check output above for results."