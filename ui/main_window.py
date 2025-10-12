"""
ZenCube Main Window
Main application window with tabbed interface
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QStatusBar, QMenuBar, QMenu, QMessageBox, QLabel
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon
import sys
import os

from .execution_panel import ExecutionPanel
from .monitoring_panel import MonitoringPanel
from .history_panel import HistoryPanel
from utils.sandbox_wrapper import SandboxRunner
from utils.process_monitor import ProcessMonitor
from utils.logger import ExecutionLogger


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize utilities
        sandbox_path = self._find_sandbox_executable()
        
        try:
            self.sandbox_runner = SandboxRunner(sandbox_path)
        except FileNotFoundError:
            QMessageBox.warning(
                self,
                "Sandbox Not Found",
                f"Could not find sandbox executable at: {sandbox_path}\n\n"
                "Please compile the sandbox first:\n"
                "make all"
            )
            self.sandbox_runner = None
        
        self.process_monitor = ProcessMonitor()
        self.execution_logger = ExecutionLogger()
        
        # Setup UI
        self.setWindowTitle("ZenCube - Sandbox Manager")
        self.setMinimumSize(1000, 700)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create panels
        self.execution_panel = ExecutionPanel(
            self.sandbox_runner,
            self.execution_logger
        )
        self.monitoring_panel = MonitoringPanel(self.process_monitor)
        self.history_panel = HistoryPanel(self.execution_logger)
        
        # Add tabs
        self.tab_widget.addTab(self.execution_panel, "🚀 Execute")
        self.tab_widget.addTab(self.monitoring_panel, "📊 Monitor")
        self.tab_widget.addTab(self.history_panel, "📜 History")
        
        # Connect signals
        self.execution_panel.execution_started.connect(self._on_execution_started)
        self.execution_panel.execution_finished.connect(self._on_execution_finished)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # System metrics in status bar
        self.system_metrics_label = QLabel()
        self.status_bar.addPermanentWidget(self.system_metrics_label)
        
        # Timer for updating system metrics
        self.metrics_timer = QTimer()
        self.metrics_timer.timeout.connect(self._update_system_metrics)
        self.metrics_timer.start(2000)  # Update every 2 seconds
        
        # Initial update
        self._update_system_metrics()
    
    def _create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        export_action = QAction("Export History...", self)
        export_action.triggered.connect(self._export_history)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        refresh_action = QAction("Refresh Monitoring", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_monitoring)
        view_menu.addAction(refresh_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("About ZenCube", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _find_sandbox_executable(self) -> str:
        """Find the sandbox executable"""
        # Try common locations
        possible_paths = [
            "./sandbox_v2",
            "../sandbox_v2",
            "/usr/local/bin/sandbox_v2",
            os.path.join(os.path.dirname(__file__), "..", "sandbox_v2")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Default to ./sandbox_v2
        return "./sandbox_v2"
    
    def _on_execution_started(self, pid: int):
        """Handle execution started"""
        self.status_label.setText(f"Executing... (PID: {pid})")
        self.process_monitor.start_monitoring(pid)
        self.monitoring_panel.refresh()
    
    def _on_execution_finished(self, success: bool):
        """Handle execution finished"""
        if success:
            self.status_label.setText("Execution completed successfully")
        else:
            self.status_label.setText("Execution failed")
        
        # Refresh history
        self.history_panel.refresh()
    
    def _update_system_metrics(self):
        """Update system metrics in status bar"""
        metrics = self.process_monitor.get_system_metrics()
        self.system_metrics_label.setText(
            f"CPU: {metrics['cpu_percent']:.1f}% | "
            f"Memory: {metrics['memory_used_mb']:.0f}/{metrics['memory_total_mb']:.0f} MB "
            f"({metrics['memory_percent']:.1f}%) | "
            f"Processes: {metrics['process_count']}"
        )
    
    def _refresh_monitoring(self):
        """Refresh monitoring panel"""
        self.monitoring_panel.refresh()
        self.status_label.setText("Monitoring refreshed")
    
    def _export_history(self):
        """Export execution history"""
        from PySide6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export History",
            "execution_history_export.json",
            "JSON Files (*.json)"
        )
        
        if filename:
            if self.execution_logger.export_history(filename):
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"History exported to:\n{filename}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Export Failed",
                    "Failed to export history"
                )
    
    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About ZenCube",
            "<h2>ZenCube Sandbox Manager</h2>"
            "<p>Version 2.0</p>"
            "<p>A lightweight Linux sandbox and process isolation framework.</p>"
            "<p>Execute commands with resource limits and monitor system processes.</p>"
            "<hr>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Process isolation with resource limits</li>"
            "<li>Real-time process monitoring</li>"
            "<li>Execution history and logging</li>"
            "</ul>"
        )
