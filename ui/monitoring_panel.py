"""
Monitoring Panel
Panel for monitoring running processes
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QGroupBox, QHeaderView
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor


class MonitoringPanel(QWidget):
    """Panel for monitoring processes"""
    
    def __init__(self, process_monitor):
        super().__init__()
        
        self.process_monitor = process_monitor
        self._setup_ui()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(3000)  # Refresh every 3 seconds
        
        # Initial load
        self.refresh()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # System metrics
        metrics_group = QGroupBox("System Metrics")
        metrics_layout = QHBoxLayout()
        
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        metrics_layout.addWidget(self.cpu_label)
        
        self.memory_label = QLabel("Memory: 0 MB")
        self.memory_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        metrics_layout.addWidget(self.memory_label)
        
        self.process_count_label = QLabel("Processes: 0")
        self.process_count_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        metrics_layout.addWidget(self.process_count_label)
        
        metrics_layout.addStretch()
        
        refresh_button = QPushButton("🔄 Refresh")
        refresh_button.clicked.connect(self.refresh)
        metrics_layout.addWidget(refresh_button)
        
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)
        
        # Monitored processes
        monitored_group = QGroupBox("Monitored Processes (from Sandbox)")
        monitored_layout = QVBoxLayout()
        
        self.monitored_table = QTableWidget()
        self.monitored_table.setColumnCount(7)
        self.monitored_table.setHorizontalHeaderLabels([
            "PID", "Name", "Status", "CPU %", "Memory (MB)", "Threads", "Created"
        ])
        self.monitored_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.monitored_table.setAlternatingRowColors(True)
        monitored_layout.addWidget(self.monitored_table)
        
        monitored_group.setLayout(monitored_layout)
        layout.addWidget(monitored_group, stretch=1)
        
        # All processes (top 20 by memory)
        all_processes_group = QGroupBox("Top Processes (by Memory)")
        all_layout = QVBoxLayout()
        
        self.all_processes_table = QTableWidget()
        self.all_processes_table.setColumnCount(5)
        self.all_processes_table.setHorizontalHeaderLabels([
            "PID", "Name", "User", "Status", "Memory"
        ])
        self.all_processes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.all_processes_table.setAlternatingRowColors(True)
        all_layout.addWidget(self.all_processes_table)
        
        all_processes_group.setLayout(all_layout)
        layout.addWidget(all_processes_group, stretch=1)
    
    def refresh(self):
        """Refresh process information"""
        # Update system metrics
        metrics = self.process_monitor.get_system_metrics()
        self.cpu_label.setText(f"CPU: {metrics['cpu_percent']:.1f}%")
        self.memory_label.setText(
            f"Memory: {metrics['memory_used_mb']:.0f} / {metrics['memory_total_mb']:.0f} MB "
            f"({metrics['memory_percent']:.1f}%)"
        )
        self.process_count_label.setText(f"Processes: {metrics['process_count']}")
        
        # Update monitored processes
        self._update_monitored_processes()
        
        # Update all processes
        self._update_all_processes()
    
    def _update_monitored_processes(self):
        """Update monitored processes table"""
        monitored = self.process_monitor.monitored_processes
        
        self.monitored_table.setRowCount(len(monitored))
        
        for row, (pid, info) in enumerate(monitored.items()):
            # Update metrics for this process
            self.process_monitor.update_metrics(pid)
            
            self.monitored_table.setItem(row, 0, QTableWidgetItem(str(info.pid)))
            self.monitored_table.setItem(row, 1, QTableWidgetItem(info.name))
            
            status_item = QTableWidgetItem(info.status)
            if info.status == "running":
                status_item.setForeground(QColor("green"))
            elif info.status == "sleeping":
                status_item.setForeground(QColor("blue"))
            elif info.status == "zombie":
                status_item.setForeground(QColor("red"))
            self.monitored_table.setItem(row, 2, status_item)
            
            self.monitored_table.setItem(row, 3, QTableWidgetItem(f"{info.cpu_percent:.1f}"))
            self.monitored_table.setItem(row, 4, QTableWidgetItem(f"{info.memory_mb:.1f}"))
            self.monitored_table.setItem(row, 5, QTableWidgetItem(str(info.threads)))
            self.monitored_table.setItem(row, 6, QTableWidgetItem(
                info.create_time.strftime("%H:%M:%S")
            ))
    
    def _update_all_processes(self):
        """Update all processes table"""
        try:
            import psutil
            
            # Get all processes sorted by memory
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'memory_info']):
                try:
                    info = proc.info
                    memory_mb = info['memory_info'].rss / (1024 * 1024)
                    processes.append((
                        info['pid'],
                        info['name'],
                        info.get('username', 'N/A'),
                        info['status'],
                        memory_mb
                    ))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by memory and take top 20
            processes.sort(key=lambda x: x[4], reverse=True)
            processes = processes[:20]
            
            self.all_processes_table.setRowCount(len(processes))
            
            for row, (pid, name, user, status, memory) in enumerate(processes):
                self.all_processes_table.setItem(row, 0, QTableWidgetItem(str(pid)))
                self.all_processes_table.setItem(row, 1, QTableWidgetItem(name))
                self.all_processes_table.setItem(row, 2, QTableWidgetItem(user))
                self.all_processes_table.setItem(row, 3, QTableWidgetItem(status))
                self.all_processes_table.setItem(row, 4, QTableWidgetItem(f"{memory:.1f} MB"))
        
        except Exception:
            pass
