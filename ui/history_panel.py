"""
History Panel
Panel for viewing execution history and logs
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QGroupBox, QHeaderView, QTextEdit, QSplitter
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class HistoryPanel(QWidget):
    """Panel for execution history"""
    
    def __init__(self, execution_logger):
        super().__init__()
        
        self.execution_logger = execution_logger
        self._setup_ui()
        self.refresh()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QHBoxLayout()
        
        self.total_label = QLabel("Total: 0")
        self.total_label.setStyleSheet("font-weight: bold;")
        stats_layout.addWidget(self.total_label)
        
        self.success_label = QLabel("Successful: 0")
        self.success_label.setStyleSheet("font-weight: bold; color: green;")
        stats_layout.addWidget(self.success_label)
        
        self.failed_label = QLabel("Failed: 0")
        self.failed_label.setStyleSheet("font-weight: bold; color: red;")
        stats_layout.addWidget(self.failed_label)
        
        self.avg_time_label = QLabel("Avg Time: 0.0s")
        self.avg_time_label.setStyleSheet("font-weight: bold;")
        stats_layout.addWidget(self.avg_time_label)
        
        stats_layout.addStretch()
        
        refresh_button = QPushButton("🔄 Refresh")
        refresh_button.clicked.connect(self.refresh)
        stats_layout.addWidget(refresh_button)
        
        clear_button = QPushButton("🗑 Clear History")
        clear_button.clicked.connect(self._clear_history)
        stats_layout.addWidget(clear_button)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Splitter for table and details
        splitter = QSplitter(Qt.Vertical)
        
        # History table
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        table_layout.addWidget(QLabel("<b>Execution History</b>"))
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels([
            "Time", "Command", "PID", "Exit Code", "Duration (s)",
            "CPU Limit", "Memory Limit", "Status"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.history_table)
        
        splitter.addWidget(table_widget)
        
        # Details panel
        details_group = QGroupBox("Execution Details")
        details_layout = QVBoxLayout()
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(200)
        details_layout.addWidget(self.details_text)
        
        details_group.setLayout(details_layout)
        splitter.addWidget(details_group)
        
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
    
    def refresh(self):
        """Refresh history display"""
        # Update statistics
        stats = self.execution_logger.get_statistics()
        self.total_label.setText(f"Total: {stats['total_executions']}")
        self.success_label.setText(f"Successful: {stats['successful']}")
        self.failed_label.setText(f"Failed: {stats['failed']}")
        self.avg_time_label.setText(f"Avg Time: {stats['avg_execution_time']:.3f}s")
        
        # Update history table
        history = self.execution_logger.get_history(limit=100)
        history.reverse()  # Show most recent first
        
        self.history_table.setRowCount(len(history))
        
        for row, log in enumerate(history):
            # Parse timestamp
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(log.timestamp)
                time_str = dt.strftime("%H:%M:%S")
            except:
                time_str = log.timestamp[:8]
            
            self.history_table.setItem(row, 0, QTableWidgetItem(time_str))
            
            # Command
            command_str = f"{log.command} {' '.join(log.arguments)}"[:50]
            self.history_table.setItem(row, 1, QTableWidgetItem(command_str))
            
            # PID
            self.history_table.setItem(row, 2, QTableWidgetItem(str(log.pid)))
            
            # Exit code
            exit_item = QTableWidgetItem(str(log.exit_code))
            if log.exit_code == 0:
                exit_item.setForeground(QColor("green"))
            else:
                exit_item.setForeground(QColor("red"))
            self.history_table.setItem(row, 3, exit_item)
            
            # Duration
            self.history_table.setItem(row, 4, QTableWidgetItem(f"{log.execution_time:.3f}"))
            
            # Limits
            cpu_str = f"{log.cpu_limit}s" if log.cpu_limit > 0 else "∞"
            mem_str = f"{log.memory_limit}MB" if log.memory_limit > 0 else "∞"
            self.history_table.setItem(row, 5, QTableWidgetItem(cpu_str))
            self.history_table.setItem(row, 6, QTableWidgetItem(mem_str))
            
            # Status
            status = "✓ Success" if log.success else "✗ Failed"
            if log.terminated_by_signal:
                status = f"⚠ Signal {log.signal_name}"
            if log.cpu_limit_exceeded:
                status = "⚠ CPU Limit"
            if log.memory_limit_exceeded:
                status = "⚠ Memory Limit"
            if log.timeout_exceeded:
                status = "⚠ Timeout"
            
            status_item = QTableWidgetItem(status)
            if log.success:
                status_item.setForeground(QColor("green"))
            else:
                status_item.setForeground(QColor("red"))
            self.history_table.setItem(row, 7, status_item)
    
    def _on_selection_changed(self):
        """Handle selection change in table"""
        selected_rows = self.history_table.selectedItems()
        
        if not selected_rows:
            self.details_text.clear()
            return
        
        row = selected_rows[0].row()
        history = self.execution_logger.get_history(limit=100)
        history.reverse()
        
        if row >= len(history):
            return
        
        log = history[row]
        
        # Build details text
        details = []
        details.append(f"<b>Timestamp:</b> {log.timestamp}")
        details.append(f"<b>Command:</b> {log.command} {' '.join(log.arguments)}")
        details.append(f"<b>PID:</b> {log.pid}")
        details.append(f"<b>Exit Code:</b> {log.exit_code}")
        details.append(f"<b>Execution Time:</b> {log.execution_time:.3f}s")
        details.append("")
        details.append(f"<b>Resource Limits:</b>")
        details.append(f"  • CPU: {log.cpu_limit}s" if log.cpu_limit > 0 else "  • CPU: Unlimited")
        details.append(f"  • Memory: {log.memory_limit}MB" if log.memory_limit > 0 else "  • Memory: Unlimited")
        details.append(f"  • Timeout: {log.timeout}s" if log.timeout > 0 else "  • Timeout: Unlimited")
        details.append("")
        
        if log.terminated_by_signal:
            details.append(f"<b>Signal:</b> {log.signal_name}")
        
        if log.cpu_limit_exceeded:
            details.append("<b>⚠ CPU limit exceeded</b>")
        if log.memory_limit_exceeded:
            details.append("<b>⚠ Memory limit exceeded</b>")
        if log.timeout_exceeded:
            details.append("<b>⚠ Timeout exceeded</b>")
        
        if log.output:
            details.append("")
            details.append(f"<b>Output:</b>")
            details.append(f"<pre>{log.output}</pre>")
        
        if log.error:
            details.append("")
            details.append(f"<b>Error:</b>")
            details.append(f"<pre>{log.error}</pre>")
        
        self.details_text.setHtml("<br>".join(details))
    
    def _clear_history(self):
        """Clear execution history"""
        from PySide6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear all execution history?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.execution_logger.clear_history()
            self.refresh()
