"""
Execution Panel
Panel for executing commands in the sandbox
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QTextEdit, QSpinBox, QSlider,
    QCheckBox, QFormLayout, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QThread, pyqtSignal
from PySide6.QtGui import QFont


class ExecutionWorker(QThread):
    """Worker thread for executing sandbox commands"""
    
    finished = pyqtSignal(object)  # SandboxResult
    started = pyqtSignal(int)  # PID
    
    def __init__(self, sandbox_runner, command, cpu_limit, memory_limit, timeout):
        super().__init__()
        self.sandbox_runner = sandbox_runner
        self.command = command
        self.cpu_limit = cpu_limit
        self.memory_limit = memory_limit
        self.timeout = timeout
    
    def run(self):
        """Execute the command"""
        result = self.sandbox_runner.run(
            command=self.command,
            cpu_limit=self.cpu_limit,
            memory_limit=self.memory_limit,
            timeout=self.timeout
        )
        
        if result.pid > 0:
            self.started.emit(result.pid)
        
        self.finished.emit(result)


class ExecutionPanel(QWidget):
    """Panel for executing sandbox commands"""
    
    execution_started = Signal(int)  # PID
    execution_finished = Signal(bool)  # Success
    
    def __init__(self, sandbox_runner, execution_logger):
        super().__init__()
        
        self.sandbox_runner = sandbox_runner
        self.execution_logger = execution_logger
        self.execution_worker = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Command input section
        command_group = QGroupBox("Command")
        command_layout = QFormLayout()
        
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("e.g., /bin/ls -la /tmp")
        command_layout.addRow("Command:", self.command_input)
        
        command_group.setLayout(command_layout)
        layout.addWidget(command_group)
        
        # Resource limits section
        limits_group = QGroupBox("Resource Limits")
        limits_layout = QFormLayout()
        
        # CPU limit
        cpu_layout = QHBoxLayout()
        self.cpu_limit_spin = QSpinBox()
        self.cpu_limit_spin.setRange(0, 3600)
        self.cpu_limit_spin.setValue(0)
        self.cpu_limit_spin.setSuffix(" seconds")
        self.cpu_limit_spin.setSpecialValueText("Unlimited")
        cpu_layout.addWidget(self.cpu_limit_spin)
        limits_layout.addRow("CPU Limit:", cpu_layout)
        
        # Memory limit
        memory_layout = QHBoxLayout()
        self.memory_limit_spin = QSpinBox()
        self.memory_limit_spin.setRange(0, 8192)
        self.memory_limit_spin.setValue(0)
        self.memory_limit_spin.setSuffix(" MB")
        self.memory_limit_spin.setSpecialValueText("Unlimited")
        memory_layout.addWidget(self.memory_limit_spin)
        limits_layout.addRow("Memory Limit:", memory_layout)
        
        # Timeout
        timeout_layout = QHBoxLayout()
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(0, 3600)
        self.timeout_spin.setValue(0)
        self.timeout_spin.setSuffix(" seconds")
        self.timeout_spin.setSpecialValueText("Unlimited")
        timeout_layout.addWidget(self.timeout_spin)
        limits_layout.addRow("Timeout:", timeout_layout)
        
        limits_group.setLayout(limits_layout)
        layout.addWidget(limits_group)
        
        # Execute button
        button_layout = QHBoxLayout()
        self.execute_button = QPushButton("▶ Execute")
        self.execute_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.execute_button.clicked.connect(self._execute_command)
        button_layout.addWidget(self.execute_button)
        
        self.stop_button = QPushButton("⏹ Stop")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.stop_button.clicked.connect(self._stop_execution)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Output section
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout()
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Courier", 9))
        output_layout.addWidget(self.output_text)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group, stretch=1)
        
        # Result section
        result_layout = QHBoxLayout()
        self.result_label = QLabel("")
        self.result_label.setStyleSheet("font-weight: bold; padding: 5px;")
        result_layout.addWidget(self.result_label)
        result_layout.addStretch()
        layout.addLayout(result_layout)
        
        # Preset commands
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Quick Commands:"))
        
        presets = [
            ("ls -l", "/bin/ls -l /tmp"),
            ("whoami", "/usr/bin/whoami"),
            ("date", "/bin/date"),
            ("uname", "/bin/uname -a"),
            ("sleep 5", "/bin/sleep 5")
        ]
        
        for label, command in presets:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, c=command: self.command_input.setText(c))
            preset_layout.addWidget(btn)
        
        preset_layout.addStretch()
        layout.addLayout(preset_layout)
    
    def _execute_command(self):
        """Execute the command"""
        if not self.sandbox_runner:
            self.output_text.append("❌ Sandbox executable not found!")
            return
        
        command_str = self.command_input.text().strip()
        if not command_str:
            self.output_text.append("❌ Please enter a command")
            return
        
        # Parse command
        command = command_str.split()
        
        # Validate command
        is_valid, error_msg = self.sandbox_runner.validate_command(command)
        if not is_valid:
            self.output_text.append(f"❌ {error_msg}")
            return
        
        # Clear previous output
        self.output_text.clear()
        self.result_label.setText("")
        
        # Get limits
        cpu_limit = self.cpu_limit_spin.value()
        memory_limit = self.memory_limit_spin.value()
        timeout = self.timeout_spin.value()
        
        # Show execution info
        self.output_text.append(f"🚀 Executing: {command_str}")
        self.output_text.append(f"   CPU Limit: {cpu_limit}s" if cpu_limit > 0 else "   CPU Limit: Unlimited")
        self.output_text.append(f"   Memory Limit: {memory_limit}MB" if memory_limit > 0 else "   Memory Limit: Unlimited")
        self.output_text.append(f"   Timeout: {timeout}s" if timeout > 0 else "   Timeout: Unlimited")
        self.output_text.append("-" * 50)
        
        # Disable controls
        self.execute_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        
        # Start execution in worker thread
        self.execution_worker = ExecutionWorker(
            self.sandbox_runner,
            command,
            cpu_limit,
            memory_limit,
            timeout
        )
        self.execution_worker.started.connect(self._on_execution_started)
        self.execution_worker.finished.connect(self._on_execution_finished)
        self.execution_worker.start()
    
    def _stop_execution(self):
        """Stop execution"""
        if self.execution_worker:
            self.execution_worker.terminate()
            self.output_text.append("\n⏹ Execution stopped by user")
            self._reset_ui()
    
    def _on_execution_started(self, pid: int):
        """Handle execution started"""
        self.output_text.append(f"✓ Process started (PID: {pid})")
        self.execution_started.emit(pid)
    
    def _on_execution_finished(self, result):
        """Handle execution finished"""
        # Log execution
        command_str = self.command_input.text()
        command = command_str.split()
        
        self.execution_logger.log_execution(
            command=command[0] if command else "",
            arguments=command[1:] if len(command) > 1 else [],
            result=result,
            cpu_limit=self.cpu_limit_spin.value(),
            memory_limit=self.memory_limit_spin.value(),
            timeout=self.timeout_spin.value()
        )
        
        # Display results
        self.output_text.append("-" * 50)
        self.output_text.append(f"Exit Code: {result.exit_code}")
        self.output_text.append(f"Execution Time: {result.execution_time:.3f}s")
        
        if result.terminated_by_signal:
            self.output_text.append(f"⚠ Terminated by signal: {result.signal_name}")
        
        if result.cpu_limit_exceeded:
            self.output_text.append("⚠ CPU limit exceeded")
        if result.memory_limit_exceeded:
            self.output_text.append("⚠ Memory limit exceeded")
        if result.timeout_exceeded:
            self.output_text.append("⚠ Timeout exceeded")
        
        # Show success/failure
        if result.success:
            self.result_label.setText("✓ Execution Successful")
            self.result_label.setStyleSheet(
                "font-weight: bold; padding: 5px; color: green;"
            )
        else:
            self.result_label.setText("✗ Execution Failed")
            self.result_label.setStyleSheet(
                "font-weight: bold; padding: 5px; color: red;"
            )
        
        self.execution_finished.emit(result.success)
        self._reset_ui()
    
    def _reset_ui(self):
        """Reset UI after execution"""
        self.execute_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
