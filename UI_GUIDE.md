# ZenCube UI User Guide

## 🎯 Getting Started

### Launching the Application

```bash
python3 main.py
```

The application will open with a modern, tabbed interface showing three main panels:
1. **Execute** - Run sandboxed commands
2. **Monitor** - View system and process metrics
3. **History** - Browse execution logs

---

## 📋 Execute Panel

### Running a Command

1. **Enter Command**: Type or select a command in the command field
   - Example: `/bin/ls -la /tmp`
   - Use absolute paths for executables

2. **Set Resource Limits** (Optional):
   - **CPU Limit**: Maximum CPU time in seconds (0 = unlimited)
   - **Memory Limit**: Maximum memory in MB (0 = unlimited)
   - **Timeout**: Wall clock timeout in seconds (0 = unlimited)

3. **Click Execute**: Press the green "▶ Execute" button

4. **View Output**: Results appear in the output text area below

### Quick Commands

Use the preset buttons for common operations:
- **ls -l**: List directory contents
- **whoami**: Show current user
- **date**: Display current date/time
- **uname**: System information
- **sleep 5**: Test timing (5 second delay)

### Understanding Results

**Success Indicators:**
- ✓ Green "Execution Successful" message
- Exit code 0
- Execution time displayed

**Failure Indicators:**
- ✗ Red "Execution Failed" message
- Non-zero exit code
- Signal termination

**Resource Limit Warnings:**
- ⚠ CPU limit exceeded (SIGXCPU)
- ⚠ Memory limit exceeded
- ⚠ Timeout exceeded

---

## 📊 Monitor Panel

### System Metrics

Top bar shows real-time system information:
- **CPU**: Overall CPU usage percentage
- **Memory**: Used/Total memory with percentage
- **Processes**: Total number of running processes

### Monitored Processes

Shows processes started from the sandbox with detailed metrics:
- **PID**: Process ID
- **Name**: Process name
- **Status**: Current state (running, sleeping, zombie)
- **CPU %**: CPU usage percentage
- **Memory (MB)**: Memory consumption
- **Threads**: Number of threads
- **Created**: Start time

### Top Processes

Lists the top 20 processes by memory usage system-wide:
- Helps identify resource-intensive processes
- Updates automatically every 3 seconds
- Includes PID, name, user, status, and memory

### Refresh

- **Auto-refresh**: Updates every 3 seconds automatically
- **Manual Refresh**: Click "🔄 Refresh" button
- **Keyboard Shortcut**: F5

---

## 📜 History Panel

### Statistics Overview

Shows aggregate execution data:
- **Total**: Total number of executions
- **Successful**: Count of successful runs (green)
- **Failed**: Count of failed runs (red)
- **Avg Time**: Average execution time

### Execution History Table

Displays up to 100 most recent executions:
- **Time**: Execution timestamp (HH:MM:SS)
- **Command**: Command and arguments (truncated if long)
- **PID**: Process ID
- **Exit Code**: Process exit status (0 = success)
- **Duration**: Execution time in seconds
- **CPU Limit**: Applied CPU limit
- **Memory Limit**: Applied memory limit
- **Status**: Execution outcome with indicators

**Status Icons:**
- ✓ Success: Normal completion
- ✗ Failed: Error or non-zero exit
- ⚠ Signal: Terminated by signal
- ⚠ CPU Limit: CPU limit exceeded
- ⚠ Memory Limit: Memory limit exceeded
- ⚠ Timeout: Timeout exceeded

### Execution Details

Click any row in the history table to view detailed information:
- Full command with arguments
- Complete execution metrics
- Resource limits applied
- Output and error messages (if captured)
- Signal information (if terminated)

### Managing History

**Refresh History:**
```
Click "🔄 Refresh" button
```

**Clear History:**
```
Click "🗑 Clear History" button
Confirm deletion when prompted
```

**Export History:**
```
File menu → Export History...
Choose location and filename
History saved as JSON file
```

---

## 💡 Usage Tips

### Best Practices

1. **Start Simple**: Test with basic commands first
2. **Use Absolute Paths**: Always use full paths like `/bin/ls`
3. **Set Conservative Limits**: Start with generous limits
4. **Monitor Resource Usage**: Check the Monitor tab during execution
5. **Review History**: Learn from past executions

### Common Use Cases

**Testing CPU-Intensive Programs:**
```
Command: /usr/bin/stress --cpu 2 --timeout 10
CPU Limit: 5 seconds
Expected: Killed by CPU limit
```

**Testing Memory Usage:**
```
Command: /usr/bin/python3 -c "x = 'a' * 100000000"
Memory Limit: 50 MB
Expected: Killed by memory limit
```

**Testing Long-Running Tasks:**
```
Command: /bin/sleep 30
Timeout: 5 seconds
Expected: Killed by timeout
```

**Safe Script Execution:**
```
Command: /bin/bash /path/to/script.sh
CPU Limit: 60 seconds
Memory Limit: 512 MB
Timeout: 120 seconds
```

### Keyboard Shortcuts

- **F5**: Refresh monitoring panel
- **Ctrl+Q**: Quit application

---

## 🔍 Troubleshooting

### "Sandbox executable not found"

**Problem**: GUI can't find the compiled sandbox

**Solution**:
```bash
cd /path/to/ZenCube
make all
python3 main.py
```

### Command Not Found

**Problem**: Command returns "command not found" error

**Solution**:
- Use absolute path: `/bin/ls` instead of `ls`
- Verify command exists: `which ls`
- Check executable permissions

### Permission Denied

**Problem**: Cannot execute command

**Solution**:
- Ensure sandbox has execute permission: `chmod +x sandbox_v2`
- Verify target command is executable
- May need elevated privileges for some operations

### Process Not Appearing in Monitor

**Problem**: Executed process doesn't show in monitoring

**Solution**:
- Process may have completed too quickly
- Check History panel for execution details
- Increase refresh rate or use longer-running commands

### GUI Freezing

**Problem**: Interface becomes unresponsive

**Solution**:
- Long-running commands execute in background threads
- Click "⏹ Stop" button to terminate execution
- Restart application if necessary

---

## 🎨 UI Features

### Color Coding

- **Green**: Success, normal operation
- **Red**: Failure, errors
- **Orange/Yellow**: Warnings, limits exceeded
- **Blue**: Informational messages

### Real-time Updates

- System metrics update every 2 seconds
- Process monitoring updates every 3 seconds
- Execution output updates in real-time

### Status Bar

Bottom status bar shows:
- Left: Current operation status
- Right: System metrics (CPU, Memory, Process count)

---

## 📊 Understanding Metrics

### CPU Percentage

- **Per-Process**: CPU time / wall time × 100
- **System-Wide**: Average across all cores
- Values > 100% possible on multi-core systems

### Memory Usage

- **RSS (Resident Set Size)**: Physical memory used
- **Virtual Memory**: Total address space
- Displayed in MB for readability

### Process Status

- **running**: Actively executing
- **sleeping**: Waiting for I/O
- **stopped**: Suspended
- **zombie**: Terminated but not reaped

---

## 🚀 Advanced Usage

### Batch Testing

1. Set consistent resource limits
2. Run multiple test commands
3. Compare results in History panel
4. Export history for analysis

### Performance Benchmarking

1. Run same command with different limits
2. Monitor execution time trends
3. Identify optimal resource allocation
4. Use exported data for reporting

### Educational Demonstrations

1. Show resource limit enforcement
2. Demonstrate process isolation
3. Visualize system resource usage
4. Track execution patterns

---

## 📝 Notes

- All executions are logged automatically
- History persists between sessions
- JSON export compatible with analysis tools
- Monitoring requires no special permissions
- Resource limits enforced by kernel

---

For technical details, see the main README.md file.
