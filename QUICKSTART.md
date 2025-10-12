# ZenCube Quick Reference

## 🚀 Installation
```bash
chmod +x setup.sh
./setup.sh
```

## ⚡ Quick Start

### GUI
```bash
python3 main.py
```

### Command Line
```bash
# Basic usage
./sandbox_v2 /bin/ls -la

# With limits
./sandbox_v2 --cpu 5 --mem 256 --timeout 10 /bin/command

# JSON output
./sandbox_v2 --json /bin/echo "test"
```

## 📖 Command Options

| Option | Description | Example |
|--------|-------------|---------|
| `--cpu N` | CPU limit (seconds) | `--cpu 5` |
| `--mem N` | Memory limit (MB) | `--mem 256` |
| `--timeout N` | Timeout (seconds) | `--timeout 10` |
| `--json` | JSON output | `--json` |
| `-h, --help` | Show help | `-h` |

## 🧪 Quick Tests

```bash
# CPU limit test
./sandbox_v2 --cpu 2 /usr/bin/yes > /dev/null

# Memory limit test
./sandbox_v2 --mem 50 /usr/bin/python3 -c "x='a'*100000000"

# Timeout test
./sandbox_v2 --timeout 3 /bin/sleep 10
```

## 🎨 GUI Tabs

1. **Execute**: Run commands with limits
2. **Monitor**: View processes and metrics
3. **History**: Browse execution logs

## 🔧 Build Commands

```bash
make all      # Compile both sandbox versions
make clean    # Remove compiled files
make test     # Run test suite
```

## 📊 Understanding Output

### Exit Codes
- `0`: Success
- `Non-zero`: Error or failure

### Signals
- `SIGXCPU`: CPU limit exceeded
- `SIGKILL`: Killed (timeout/memory)
- `SIGSEGV`: Segmentation fault

### Status Indicators
- ✓ Success
- ✗ Failed
- ⚠ Warning/Limit exceeded

## 💡 Tips

1. **Use absolute paths**: `/bin/ls` not `ls`
2. **Start with generous limits**: Increase constraints gradually
3. **Monitor during execution**: Switch to Monitor tab
4. **Export history**: File → Export History
5. **Check logs**: History tab for detailed info

## 🐛 Common Issues

### Sandbox not found
```bash
make all
```

### Permission denied
```bash
chmod +x sandbox_v2
```

### GUI won't start
```bash
pip install --upgrade PySide6
```

### Process not monitored
- Process completed too quickly
- Check History tab instead

## 📁 Project Structure

```
ZenCube/
├── sandbox_v2.c          # Enhanced C sandbox
├── main.py               # GUI entry point
├── ui/                   # GUI components
├── utils/                # Python utilities
└── resources/            # App resources
```

## 🔗 Resources

- `README.md`: Full documentation
- `UI_GUIDE.md`: Detailed GUI guide
- `project_summery.txt`: Project overview

## ⌨️ Keyboard Shortcuts

- `F5`: Refresh monitoring
- `Ctrl+Q`: Quit application

---

**ZenCube** - Lightweight Linux Sandbox 🧊
