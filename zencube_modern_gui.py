"""
ZenCube Modern GUI - PySide6 Implementation
Date: October 13, 2025
Description: Modern, responsive GUI with React-inspired design using PySide6
"""

import os
import subprocess
import threading
import platform
import shlex
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QCheckBox, QSlider,
    QFileDialog, QFrame, QScrollArea, QSpinBox, QComboBox, QMessageBox,
    QGraphicsDropShadowEffect, QGroupBox, QGridLayout, QSplitter, QSizePolicy,
    QLayout
)
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, Signal, QThread,
    QObject, Property, QRect, QPoint
)
from PySide6.QtGui import (
    QFont, QColor, QPalette, QIcon, QLinearGradient, QPainter, QBrush,
    QPen, QPixmap, QTextCursor
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from gui.file_jail_panel import attach_file_jail_panel
from gui.monitor_panel import attach_monitor_panel
from gui.network_panel import attach_network_panel


class FlowLayout(QLayout):
    """Flow layout that wraps widgets responsively"""
    
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing if spacing >= 0 else 10)
        self.item_list = []
    
    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)
    
    def addItem(self, item):
        self.item_list.append(item)
    
    def count(self):
        return len(self.item_list)
    
    def itemAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None
    
    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None
    
    def expandingDirections(self):
        return Qt.Orientations(0)
    
    def hasHeightForWidth(self):
        return True
    
    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), True)
    
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)
    
    def sizeHint(self):
        return self.minimumSize()
    
    def minimumSize(self):
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        margin = self.contentsMargins().left()
        size += QSize(2 * margin, 2 * margin)
        return size
    
    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        
        for item in self.item_list:
            widget = item.widget()
            space_x = spacing
            space_y = spacing
            
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0
            
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        
        return y + line_height - rect.y()


class ModernButton(QPushButton):
    """Modern styled button with hover effects"""
    
    def __init__(self, text, primary=False, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self.setMinimumHeight(35)
        self.setCursor(Qt.PointingHandCursor)
        self._setup_style()
    
    def _setup_style(self):
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #667eea, stop:1 #764ba2);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 10px 20px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #764ba2, stop:1 #667eea);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #5a3a7f, stop:1 #4a5fc1);
                }
                QPushButton:disabled {
                    background: #cccccc;
                    color: #666666;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: #f0f4f8;
                    color: #2d3748;
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 600;
                    padding: 10px 20px;
                }
                QPushButton:hover {
                    background: #e2e8f0;
                    border-color: #cbd5e0;
                }
                QPushButton:pressed {
                    background: #cbd5e0;
                }
            """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)


class ModernCard(QFrame):
    """Modern card widget with shadow"""
    
    def __init__(self, title=None, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(8)
        
        # Add title if provided
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2d3748;
                    background: transparent;
                    border: none;
                }
            """)
            self.main_layout.addWidget(title_label)


class ModernInput(QLineEdit):
    """Modern styled input field"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(36)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #f7fafc;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                color: #2d3748;
            }
            QLineEdit:focus {
                border-color: #667eea;
                background-color: white;
            }
            QLineEdit:hover {
                border-color: #cbd5e0;
            }
        """)


class ModernCheckbox(QCheckBox):
    """Modern styled checkbox"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #2d3748;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 24px;
                height: 24px;
                border-radius: 6px;
                border: 2px solid #cbd5e0;
                background: white;
            }
            QCheckBox::indicator:hover {
                border-color: #667eea;
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-color: #667eea;
            }
        """)


class ModernSpinBox(QSpinBox):
    """Modern styled spin box"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(36)
        self.setStyleSheet("""
            QSpinBox {
                background-color: #f7fafc;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 14px;
                color: #2d3748;
            }
            QSpinBox:focus {
                border-color: #667eea;
                background-color: white;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 30px;
                border-radius: 4px;
                background: #e2e8f0;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #cbd5e0;
            }
            QSpinBox::up-arrow {
                width: 12px;
                height: 12px;
            }
            QSpinBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)


class CommandExecutor(QThread):
    """Thread for executing commands"""
    output_received = Signal(str)
    finished_signal = Signal(int)
    started_signal = Signal(int)
    
    def __init__(self, command_parts, env=None, cwd=None):
        super().__init__()
        self.command_parts = command_parts
        self.process = None
        self.env = env
        self.cwd = cwd
    
    def run(self):
        try:
            self.process = subprocess.Popen(
                self.command_parts,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=self.env,
                cwd=self.cwd,
            )
            if self.process.pid:
                self.started_signal.emit(self.process.pid)
            
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.output_received.emit(line)
            
            self.process.wait()
            self.finished_signal.emit(self.process.returncode)
            
        except Exception as e:
            self.output_received.emit(f"❌ Error: {str(e)}\n")
            self.finished_signal.emit(-1)
    
    def stop(self):
        if self.process:
            self.process.terminate()


class ZenCubeModernGUI(QMainWindow):
    """Modern ZenCube GUI with PySide6"""
    
    def __init__(self):
        super().__init__()
        self.executor = None
        self.use_wsl = platform.system() == "Windows"
        self.sandbox_path = self.detect_sandbox_path()
        self.terminal_visible = True  # Track terminal visibility
        self.network_panel = None
        self.monitor_panel = None
        self._last_raw_command: list[str] = []
        self._last_prepared_command: list[str] = []
        
        self.setWindowTitle("ZenCube Sandbox - Modern UI")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 750)
        
        # Setup UI
        self.setup_ui()
        self.apply_theme()
        
        # Center window
        self.center_window()
    
    def detect_sandbox_path(self):
        """Detect sandbox binary path"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        possible_paths = [
            "./sandbox",
            os.path.join(script_dir, "sandbox"),
            "./zencube/sandbox",
            "../sandbox",
            os.path.join(script_dir, "..", "sandbox"),
        ]
        
        for path in possible_paths:
            full_path = os.path.abspath(path)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                if platform.system() != "Windows":
                    if os.access(full_path, os.X_OK):
                        return path
                else:
                    return path
        
        return "./sandbox"
    
    def center_window(self):
        """Center window on screen"""
        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.frameGeometry()
        center_point = screen.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
    
    def setup_ui(self):
        """Setup the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header
        self.create_header(main_layout)
        
        # Content area with splitter
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(8)
        splitter.setChildrenCollapsible(False)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #cbd5e0, stop:0.5 #667eea, stop:1 #cbd5e0);
                border-radius: 4px;
                margin: 2px 0px;
            }
            QSplitter::handle:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:0.5 #764ba2, stop:1 #667eea);
            }
        """)
        
        # Top section (command and limits) with scroll area
        top_scroll = QScrollArea()
        top_scroll.setWidgetResizable(True)
        top_scroll.setFrameShape(QFrame.NoFrame)
        top_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #f7fafc;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e0;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0aec0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setSpacing(15)
        top_layout.setContentsMargins(0, 0, 10, 0)
        
        self.create_command_section(top_layout)
        self.create_limits_section(top_layout)
        self.create_file_jail_section(top_layout)
        self.create_network_section(top_layout)
        self.create_monitor_section(top_layout)
        top_layout.addStretch()
        
        top_scroll.setWidget(top_widget)
        splitter.addWidget(top_scroll)
        
        # Bottom section (output) - Store reference for toggling
        self.bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(self.bottom_widget)
        self.create_output_section(bottom_layout)
        splitter.addWidget(self.bottom_widget)
        
        # Store splitter reference
        self.splitter = splitter
        
        # Set splitter sizes (top section gets more space)
        splitter.setSizes([350, 250])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter, 1)
        
        # Control buttons (below splitter with fixed space)
        self.create_control_buttons(main_layout)
        
        # Status bar
        self.create_status_bar()
    
    def create_header(self, layout):
        """Create header section"""
        header_card = ModernCard()
        header_layout = QHBoxLayout()
        
        # Icon and title
        title_layout = QVBoxLayout()
        
        title = QLabel("🧊 ZenCube Sandbox")
        title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #1a202c;
                background: transparent;
                border: none;
            }
        """)
        
        subtitle = QLabel("Execute commands safely with resource limits")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #718096;
                background: transparent;
                border: none;
            }
        """)
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        title_layout.addStretch()
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Settings button
        settings_btn = ModernButton("⚙️ Settings")
        settings_btn.setMaximumWidth(120)
        settings_btn.clicked.connect(self.show_settings)
        header_layout.addWidget(settings_btn)
        
        header_card.main_layout.addLayout(header_layout)
        layout.addWidget(header_card)
    
    def create_command_section(self, layout):
        """Create command selection section"""
        card = ModernCard("Command Selection")
        
        # Command path
        cmd_layout = QHBoxLayout()
        cmd_label = QLabel("Command:")
        cmd_label.setMinimumWidth(80)
        cmd_label.setStyleSheet("font-weight: 600; color: #4a5568;")
        
        self.command_input = ModernInput("Enter command or browse...")
        
        browse_btn = ModernButton("📁 Browse")
        browse_btn.setMaximumWidth(120)
        browse_btn.clicked.connect(self.browse_file)
        
        cmd_layout.addWidget(cmd_label)
        cmd_layout.addWidget(self.command_input, 1)
        cmd_layout.addWidget(browse_btn)
        
        card.main_layout.addLayout(cmd_layout)
        
        # Arguments
        args_layout = QHBoxLayout()
        args_label = QLabel("Arguments:")
        args_label.setMinimumWidth(80)
        args_label.setStyleSheet("font-weight: 600; color: #4a5568;")
        
        self.args_input = ModernInput("Optional arguments...")
        
        args_layout.addWidget(args_label)
        args_layout.addWidget(self.args_input, 1)
        
        card.main_layout.addLayout(args_layout)
        
        # Quick commands
        quick_label = QLabel("Quick Commands:")
        quick_label.setStyleSheet("font-weight: 600; color: #4a5568; margin-top: 10px;")
        card.main_layout.addWidget(quick_label)
        
        # Use FlowLayout for responsive wrapping
        quick_layout = FlowLayout(spacing=10)
        
        quick_commands = [
            ("📋 ls", "/bin/ls", "-la"),
            ("💬 echo", "/bin/echo", "Hello ZenCube!"),
            ("👤 whoami", "/usr/bin/whoami", ""),
            ("⏱️ CPU Test", "./tests/infinite_loop", ""),
            ("💾 Memory Test", "./tests/memory_hog", ""),
        ]
        
        for label, cmd, args in quick_commands:
            btn = ModernButton(label)
            btn.clicked.connect(lambda checked, c=cmd, a=args: self.set_quick_command(c, a))
            quick_layout.addWidget(btn)
        
        card.main_layout.addLayout(quick_layout)
        
        layout.addWidget(card)
    
    def create_limits_section(self, layout):
        """Create resource limits section"""
        card = ModernCard("Resource Limits")
        
        # Create grid layout for limits (more compact)
        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setContentsMargins(0, 0, 0, 0)
        
        # CPU Limit
        self.cpu_check = ModernCheckbox("CPU Time (sec)")
        self.cpu_spin = ModernSpinBox()
        self.cpu_spin.setRange(1, 3600)
        self.cpu_spin.setValue(5)
        self.cpu_spin.setEnabled(False)
        self.cpu_check.toggled.connect(lambda checked: self.cpu_spin.setEnabled(checked))
        
        grid.addWidget(self.cpu_check, 0, 0)
        grid.addWidget(self.cpu_spin, 0, 1)
        
        # Memory Limit
        self.mem_check = ModernCheckbox("Memory (MB)")
        self.mem_spin = ModernSpinBox()
        self.mem_spin.setRange(1, 16384)
        self.mem_spin.setValue(256)
        self.mem_spin.setEnabled(False)
        self.mem_check.toggled.connect(lambda checked: self.mem_spin.setEnabled(checked))
        
        grid.addWidget(self.mem_check, 0, 2)
        grid.addWidget(self.mem_spin, 0, 3)
        
        # Process Limit
        self.procs_check = ModernCheckbox("Max Processes")
        self.procs_spin = ModernSpinBox()
        self.procs_spin.setRange(1, 1000)
        self.procs_spin.setValue(10)
        self.procs_spin.setEnabled(False)
        self.procs_check.toggled.connect(lambda checked: self.procs_spin.setEnabled(checked))
        
        grid.addWidget(self.procs_check, 1, 0)
        grid.addWidget(self.procs_spin, 1, 1)
        
        # File Size Limit
        self.fsize_check = ModernCheckbox("File Size (MB)")
        self.fsize_spin = ModernSpinBox()
        self.fsize_spin.setRange(1, 10240)
        self.fsize_spin.setValue(100)
        self.fsize_spin.setEnabled(False)
        self.fsize_check.toggled.connect(lambda checked: self.fsize_spin.setEnabled(checked))
        
        grid.addWidget(self.fsize_check, 1, 2)
        grid.addWidget(self.fsize_spin, 1, 3)
        
        card.main_layout.addLayout(grid)
        
        # Presets (more compact)
        preset_label = QLabel("Presets:")
        preset_label.setStyleSheet("font-weight: 600; color: #4a5568; margin-top: 5px;")
        card.main_layout.addWidget(preset_label)
        
        # Use FlowLayout for responsive preset buttons
        preset_layout = FlowLayout(spacing=6)
        
        presets = [
            ("🔓 No Limits", self.preset_none),
            ("🟢 Light", self.preset_light),
            ("🟡 Medium", self.preset_medium),
            ("🔴 Strict", self.preset_strict),
        ]
        
        for label, func in presets:
            btn = ModernButton(label)
            btn.clicked.connect(func)
            preset_layout.addWidget(btn)
        
        card.main_layout.addLayout(preset_layout)
        
        # WSL option
        self.wsl_check = ModernCheckbox("Use WSL (Windows Subsystem for Linux)")
        self.wsl_check.setChecked(self.use_wsl)
        self.wsl_check.toggled.connect(self.update_wsl_status)
        
        wsl_info = QLabel(f"Auto-detected: {platform.system()}")
        wsl_info.setStyleSheet("color: #718096; font-size: 12px; margin-left: 34px;")
        
        card.main_layout.addWidget(self.wsl_check)
        card.main_layout.addWidget(wsl_info)
        
        layout.addWidget(card)
    
    def create_file_jail_section(self, layout):
        """Create the File Jail panel container."""
        card = ModernCard("File Jail")
        card.main_layout.setSpacing(12)
        self.file_jail_panel = attach_file_jail_panel(self, card.main_layout)
        layout.addWidget(card)

    def create_network_section(self, layout):
        """Create the network restriction panel container."""
        card = ModernCard("Network Restrictions")
        card.main_layout.setSpacing(12)
        self.network_panel = attach_network_panel(self, card.main_layout)
        layout.addWidget(card)

    def create_monitor_section(self, layout):
        """Create the monitoring dashboard panel container."""
        card = ModernCard("Monitoring & Metrics")
        card.main_layout.setSpacing(12)
        self.monitor_panel = attach_monitor_panel(self, card.main_layout)
        layout.addWidget(card)

    def create_output_section(self, layout):
        """Create output terminal section"""
        card = ModernCard("Terminal Output")
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(150)
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a202c;
                color: #00ff00;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.5;
            }
        """)
        
        # Initial message
        self.log_output("🧊 ZenCube Sandbox Terminal\n", "info")
        self.log_output("=" * 80 + "\n", "info")
        self.log_output("Ready to execute commands.\n\n", "success")
        self.validate_sandbox()
        
        card.main_layout.addWidget(self.output_text, 1)
        layout.addWidget(card, 1)
    
    def create_control_buttons(self, layout):
        """Create control buttons"""
        button_layout = FlowLayout(spacing=15)
        
        # Execute button
        self.execute_btn = ModernButton("▶️ Execute Command", primary=True)
        self.execute_btn.setMinimumWidth(160)
        self.execute_btn.setMinimumHeight(42)
        self.execute_btn.clicked.connect(self.execute_command)
        
        # Stop button
        self.stop_btn = ModernButton("⏹️ Stop")
        self.stop_btn.setMinimumWidth(120)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_execution)
        
        # Clear button
        clear_btn = ModernButton("🗑️ Clear")
        clear_btn.setMinimumWidth(120)
        clear_btn.clicked.connect(self.clear_output)
        
        # Toggle Terminal button
        self.toggle_terminal_btn = ModernButton("👁️ Hide Terminal")
        self.toggle_terminal_btn.setMinimumWidth(140)
        self.toggle_terminal_btn.clicked.connect(self.toggle_terminal)
        
        # Help button
        help_btn = ModernButton("❓ Help")
        help_btn.setMinimumWidth(120)
        help_btn.clicked.connect(self.show_help)
        
        button_layout.addWidget(self.execute_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(self.toggle_terminal_btn)
        button_layout.addWidget(help_btn)
        
        layout.addLayout(button_layout)
    
    def create_status_bar(self):
        """Create status bar"""
        status = self.statusBar()
        status.setStyleSheet("""
            QStatusBar {
                background: #f7fafc;
                color: #4a5568;
                border-top: 1px solid #e2e8f0;
                padding: 5px;
            }
        """)
        
        os_name = platform.system()
        mode = "WSL Mode" if self.use_wsl else "Native Mode"
        status.showMessage(f"Ready | OS: {os_name} | {mode} | Sandbox: {self.sandbox_path}")
    
    def apply_theme(self):
        """Apply modern theme to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f7fafc, stop:1 #edf2f7);
            }
            QWidget {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
                    'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
            }
            QScrollBar:vertical {
                border: none;
                background: #e2e8f0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e0;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0aec0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
    
    def validate_sandbox(self):
        """Validate sandbox exists"""
        if not os.path.exists(self.sandbox_path):
            self.log_output("⚠️ WARNING: Sandbox binary not found!\n", "warning")
            self.log_output(f"Looking for: {self.sandbox_path}\n", "warning")
            self.log_output(f"Current directory: {os.getcwd()}\n\n", "info")
        else:
            if platform.system() != "Windows":
                if not os.access(self.sandbox_path, os.X_OK):
                    self.log_output("⚠️ Sandbox found but not executable!\n", "warning")
                    self.log_output(f"Run: chmod +x {self.sandbox_path}\n\n", "info")
                else:
                    self.log_output(f"✅ Sandbox found: {self.sandbox_path}\n\n", "success")
            else:
                self.log_output(f"✅ Sandbox found: {self.sandbox_path}\n\n", "success")
    
    def browse_file(self):
        """Browse for file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Command/Executable",
            "",
            "All Files (*)"
        )
        
        if file_path:
            if file_path.endswith('.c') or file_path.endswith('.cpp'):
                self.log_output(f"⚠️ Warning: Source file selected: {file_path}\n", "warning")
                self.log_output(f"💡 Select the executable without .c extension\n", "info")
            
            self.command_input.setText(file_path)
            self.log_output(f"📁 Selected: {file_path}\n", "info")
    
    def set_quick_command(self, command, args):
        """Set quick command"""
        self.command_input.setText(command)
        self.args_input.setText(args)
        self.log_output(f"⚡ Quick command set: {command} {args}\n", "info")
    
    def preset_none(self):
        """No limits preset"""
        self.cpu_check.setChecked(False)
        self.mem_check.setChecked(False)
        self.procs_check.setChecked(False)
        self.fsize_check.setChecked(False)
        self.log_output("📋 Preset: No Limits\n", "info")
    
    def preset_light(self):
        """Light limits preset"""
        self.cpu_check.setChecked(True)
        self.cpu_spin.setValue(30)
        self.mem_check.setChecked(True)
        self.mem_spin.setValue(1024)
        self.procs_check.setChecked(False)
        self.fsize_check.setChecked(False)
        self.log_output("📋 Preset: Light (CPU: 30s, Memory: 1GB)\n", "info")
    
    def preset_medium(self):
        """Medium limits preset"""
        self.cpu_check.setChecked(True)
        self.cpu_spin.setValue(10)
        self.mem_check.setChecked(True)
        self.mem_spin.setValue(512)
        self.procs_check.setChecked(True)
        self.procs_spin.setValue(10)
        self.fsize_check.setChecked(False)
        self.log_output("📋 Preset: Medium (CPU: 10s, Memory: 512MB, Procs: 10)\n", "info")
    
    def preset_strict(self):
        """Strict limits preset"""
        self.cpu_check.setChecked(True)
        self.cpu_spin.setValue(5)
        self.mem_check.setChecked(True)
        self.mem_spin.setValue(256)
        self.procs_check.setChecked(True)
        self.procs_spin.setValue(5)
        self.fsize_check.setChecked(True)
        self.fsize_spin.setValue(50)
        self.log_output("📋 Preset: Strict (All limits enabled)\n", "info")
    
    def update_wsl_status(self, checked):
        """Update WSL status"""
        self.use_wsl = checked
        mode = "WSL Mode" if checked else "Native Mode"
        self.log_output(f"🔄 {mode} enabled\n", "info")
        
        os_name = platform.system()
        self.statusBar().showMessage(f"Ready | OS: {os_name} | {mode} | Sandbox: {self.sandbox_path}")
    
    def _convert_command_for_platform(self, command: str) -> str:
        if self.use_wsl and ':' in command:
            path = command.replace('\\', '/')
            if len(path) > 1 and path[1] == ':':
                drive = path[0].lower()
                rest = path[2:]
                return f"/mnt/{drive}{rest}"
        return command

    def _collect_target_command_parts(self) -> list[str]:
        command = self.command_input.text().strip()
        if not command:
            raise ValueError("No command specified")
        command = self._convert_command_for_platform(command)
        args_text = self.args_input.text().strip()
        parts: list[str] = [command]
        if args_text:
            try:
                parts.extend(shlex.split(args_text))
            except ValueError as exc:
                raise ValueError(f"Invalid arguments: {exc}") from exc
        return parts

    def compute_target_commands(self) -> tuple[list[str], list[str]]:
        raw_parts = self._collect_target_command_parts()
        if self.network_panel:
            prepared_parts = self.network_panel.prepare_command(raw_parts)
        else:
            prepared_parts = list(raw_parts)
        self._last_raw_command = list(raw_parts)
        self._last_prepared_command = list(prepared_parts)
        return self._last_raw_command, self._last_prepared_command

    def get_effective_target_command(self) -> list[str]:
        _, prepared = self.compute_target_commands()
        return list(prepared)

    def _build_execution_env(self) -> dict[str, str]:
        env = os.environ.copy()
        root = str(PROJECT_ROOT)
        existing = env.get("PYTHONPATH", "")
        if existing:
            paths = existing.split(os.pathsep)
            if root not in paths:
                env["PYTHONPATH"] = os.pathsep.join([root, existing])
        else:
            env["PYTHONPATH"] = root
        if self.network_panel:
            self.network_panel.apply_env_overrides(env)
        return env

    def build_command(self):
        """Build command with limits"""
        raw_parts, prepared_parts = self.compute_target_commands()

        # Build command
        if self.use_wsl:
            cmd_parts = ["wsl", self.sandbox_path]
        else:
            cmd_parts = [self.sandbox_path]
        
        # Add limits
        if self.cpu_check.isChecked():
            cmd_parts.append(f"--cpu={self.cpu_spin.value()}")
        
        if self.mem_check.isChecked():
            cmd_parts.append(f"--mem={self.mem_spin.value()}")
        
        if self.procs_check.isChecked():
            cmd_parts.append(f"--procs={self.procs_spin.value()}")
        
        if self.fsize_check.isChecked():
            cmd_parts.append(f"--fsize={self.fsize_spin.value()}")

        if self.network_panel and self.network_panel.is_disabled():
            cmd_parts.append("--no-net")
            if self.network_panel.is_enforce_mode():
                if self.use_wsl:
                    sandbox_options = cmd_parts[2:].copy()
                else:
                    sandbox_options = cmd_parts[1:].copy()
                enforce_args = sandbox_options + raw_parts
                self.network_panel.show_enforce_command(self.sandbox_path, enforce_args)
            else:
                self.network_panel.reset_note()
        elif self.network_panel:
            self.network_panel.reset_note()
        
        cmd_parts.extend(prepared_parts)
        return cmd_parts
    
    def execute_command(self):
        """Execute command"""
        try:
            # Validate
            command = self.command_input.text().strip()
            if not command:
                QMessageBox.warning(self, "Error", "Please enter a command")
                return
            
            if command.endswith('.c') or command.endswith('.cpp'):
                QMessageBox.critical(
                    self,
                    "Invalid File",
                    f"Cannot execute source file!\n\n{command}\n\nSelect the compiled executable."
                )
                return
            
            # Build command and environment
            cmd_parts = self.build_command()
            env = self._build_execution_env()
            
            # Log
            self.log_output("\n" + "=" * 80 + "\n", "info")
            self.log_output(f"🚀 Executing: {' '.join(cmd_parts)}\n", "info")
            self.log_output("=" * 80 + "\n", "info")
            
            # Update UI
            self.execute_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.statusBar().showMessage("Running...")
            
            # Execute in thread
            self.executor = CommandExecutor(cmd_parts, env=env, cwd=str(PROJECT_ROOT))
            self.executor.output_received.connect(self.log_output)
            self.executor.started_signal.connect(self._on_process_started)
            self.executor.finished_signal.connect(self.on_command_finished)
            self.executor.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.log_output(f"❌ Error: {e}\n", "error")
    
    def _on_process_started(self, pid: int) -> None:
        """Attach monitoring once the subprocess PID is available."""
        if self.monitor_panel and self._last_raw_command:
            self.monitor_panel.attach_to_process(
                pid,
                list(self._last_raw_command),
                list(self._last_prepared_command),
            )
        
        # Attach network panel for status tracking
        if self.network_panel:
            self.network_panel.attach_to_execution(pid)

    def stop_execution(self):
        """Stop command execution"""
        if self.executor:
            self.executor.stop()
            self.log_output("\n🛑 Stopped by user\n", "warning")
            self.on_command_finished(-1)
    
    def on_command_finished(self, exit_code):
        """Handle command completion"""
        if self.monitor_panel:
            self.monitor_panel.handle_process_finished(exit_code)
        
        # Notify network panel that execution finished
        if self.network_panel:
            self.network_panel.handle_execution_finished()
        
        self.execute_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        if exit_code == 0:
            self.log_output(f"\n✅ Command completed (exit code: {exit_code})\n", "success")
        else:
            self.log_output(f"\n⚠️ Command exited with code: {exit_code}\n", "warning")
        
        os_name = platform.system()
        mode = "WSL Mode" if self.use_wsl else "Native Mode"
        self.statusBar().showMessage(f"Ready | OS: {os_name} | {mode} | Sandbox: {self.sandbox_path}")
    
    def toggle_terminal(self):
        """Toggle terminal visibility"""
        self.terminal_visible = not self.terminal_visible
        
        if self.terminal_visible:
            self.bottom_widget.show()
            self.toggle_terminal_btn.setText("👁️ Hide Terminal")
            # Restore splitter sizes
            self.splitter.setSizes([500, 400])
        else:
            self.bottom_widget.hide()
            self.toggle_terminal_btn.setText("👁️ Show Terminal")
            # Give all space to top widget
            sizes = self.splitter.sizes()
            total = sum(sizes)
            self.splitter.setSizes([total, 0])
        
        self.log_output(f"{'📺 Terminal shown' if self.terminal_visible else '🔇 Terminal hidden'}\n", "info")
    
    def log_output(self, message, msg_type=None):
        """Log output to terminal"""
        cursor = self.output_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Color based on type
        if msg_type == "error":
            color = "#ff4444"
        elif msg_type == "success":
            color = "#44ff44"
        elif msg_type == "warning":
            color = "#ffaa00"
        elif msg_type == "info":
            color = "#4a9eff"
        else:
            color = "#00ff00"
        
        # Convert newlines to HTML breaks and escape HTML characters
        html_message = message.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        cursor.insertHtml(f'<span style="color: {color};">{html_message}</span>')
        self.output_text.setTextCursor(cursor)
        self.output_text.ensureCursorVisible()

    def closeEvent(self, event):  # noqa: D401 - Qt event override
        if self.monitor_panel:
            self.monitor_panel.shutdown()
        super().closeEvent(event)
    
    def clear_output(self):
        """Clear output"""
        self.output_text.clear()
        self.log_output("🧊 ZenCube Sandbox Terminal\n", "info")
        self.log_output("=" * 80 + "\n", "info")
        self.log_output("Output cleared.\n\n", "success")
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Settings")
        dialog.setText(f"""
        Sandbox Path: {self.sandbox_path}
        Working Directory: {os.getcwd()}
        Platform: {platform.system()}
        
        Use the settings button to configure custom paths.
        """)
        dialog.exec()
    
    def show_help(self):
        """Show help"""
        help_text = """
        <h2>ZenCube Sandbox - Help</h2>
        
        <h3>Usage:</h3>
        <ol>
            <li>Select a command using Browse or Quick Commands</li>
            <li>Add optional arguments</li>
            <li>Enable resource limits as needed</li>
            <li>Click Execute Command</li>
        </ol>
        
        <h3>Presets:</h3>
        <ul>
            <li><b>No Limits:</b> Run without restrictions</li>
            <li><b>Light:</b> Generous limits for development</li>
            <li><b>Medium:</b> Balanced limits for testing</li>
            <li><b>Strict:</b> Tight limits for untrusted code</li>
        </ul>
        
        <h3>WSL Option:</h3>
        <p>Windows users should keep WSL enabled. Linux users should disable it.</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Help")
        msg.setTextFormat(Qt.RichText)
        msg.setText(help_text)
        msg.exec()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set app-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Create and show window
    window = ZenCubeModernGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
