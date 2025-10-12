#!/bin/bash
# ZenCube Setup Script
# Compiles the sandbox and sets up Python environment

set -e  # Exit on error

echo "╔═══════════════════════════════════════╗"
echo "║   ZenCube Setup & Installation        ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ Error: ZenCube requires Linux"
    echo "   Please run this on a Linux system (Ubuntu, Debian, etc.)"
    exit 1
fi

echo "✓ Linux system detected"

# Check for GCC
if ! command -v gcc &> /dev/null; then
    echo "❌ Error: GCC not found"
    echo "   Install with: sudo apt-get install build-essential"
    exit 1
fi

echo "✓ GCC compiler found"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 not found"
    echo "   Install with: sudo apt-get install python3 python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python $PYTHON_VERSION found"

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "⚠ Warning: pip3 not found"
    echo "   Install with: sudo apt-get install python3-pip"
    exit 1
fi

echo "✓ pip3 found"

# Compile sandbox
echo ""
echo "📦 Compiling sandbox executables..."
make clean
make all

if [ $? -eq 0 ]; then
    echo "✓ Sandbox compiled successfully"
else
    echo "❌ Error: Compilation failed"
    exit 1
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Python dependencies installed"
else
    echo "⚠ Warning: Some dependencies may have failed to install"
fi

# Test sandbox
echo ""
echo "🧪 Testing sandbox..."
./sandbox_v2 /bin/echo "Hello from ZenCube!"

if [ $? -eq 0 ]; then
    echo "✓ Sandbox test passed"
else
    echo "⚠ Warning: Sandbox test failed"
fi

# Make main.py executable
chmod +x main.py

echo ""
echo "╔═══════════════════════════════════════╗"
echo "║   Setup Complete! 🎉                  ║"
echo "╚═══════════════════════════════════════╝"
echo ""
echo "Quick Start:"
echo "  1. Run GUI:     python3 main.py"
echo "  2. Test CLI:    ./sandbox_v2 --help"
echo "  3. Run tests:   make test"
echo ""
echo "Documentation:"
echo "  - README.md     : Full documentation"
echo "  - UI_GUIDE.md   : GUI user guide"
echo ""
