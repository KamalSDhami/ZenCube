"""
Process Monitor
Real-time process monitoring utilities using psutil
"""

import psutil
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ProcessMetrics:
    """Represents process metrics at a point in time"""
    timestamp: datetime
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    threads: int
    status: str


@dataclass
class ProcessInfo:
    """Complete process information"""
    pid: int
    name: str
    cmdline: List[str]
    create_time: datetime
    status: str
    username: str
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    memory_percent: float = 0.0
    threads: int = 0
    metrics_history: List[ProcessMetrics] = field(default_factory=list)


class ProcessMonitor:
    """Monitor running processes and collect metrics"""
    
    def __init__(self, max_history: int = 100):
        """
        Initialize process monitor
        
        Args:
            max_history: Maximum number of metric samples to keep per process
        """
        self.max_history = max_history
        self.monitored_processes: Dict[int, ProcessInfo] = {}
    
    def get_process_info(self, pid: int) -> Optional[ProcessInfo]:
        """
        Get detailed information about a process
        
        Args:
            pid: Process ID
            
        Returns:
            ProcessInfo object or None if process doesn't exist
        """
        try:
            proc = psutil.Process(pid)
            
            info = ProcessInfo(
                pid=pid,
                name=proc.name(),
                cmdline=proc.cmdline(),
                create_time=datetime.fromtimestamp(proc.create_time()),
                status=proc.status(),
                username=proc.username(),
                cpu_percent=proc.cpu_percent(interval=0.1),
                memory_mb=proc.memory_info().rss / (1024 * 1024),
                memory_percent=proc.memory_percent(),
                threads=proc.num_threads()
            )
            
            return info
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    
    def start_monitoring(self, pid: int) -> bool:
        """
        Start monitoring a process
        
        Args:
            pid: Process ID to monitor
            
        Returns:
            True if monitoring started successfully
        """
        info = self.get_process_info(pid)
        
        if info:
            self.monitored_processes[pid] = info
            return True
        
        return False
    
    def stop_monitoring(self, pid: int):
        """
        Stop monitoring a process
        
        Args:
            pid: Process ID to stop monitoring
        """
        if pid in self.monitored_processes:
            del self.monitored_processes[pid]
    
    def update_metrics(self, pid: int) -> bool:
        """
        Update metrics for a monitored process
        
        Args:
            pid: Process ID
            
        Returns:
            True if update successful
        """
        if pid not in self.monitored_processes:
            return False
        
        try:
            proc = psutil.Process(pid)
            info = self.monitored_processes[pid]
            
            # Update current values
            info.cpu_percent = proc.cpu_percent(interval=0.1)
            info.memory_mb = proc.memory_info().rss / (1024 * 1024)
            info.memory_percent = proc.memory_percent()
            info.threads = proc.num_threads()
            info.status = proc.status()
            
            # Add to history
            metrics = ProcessMetrics(
                timestamp=datetime.now(),
                cpu_percent=info.cpu_percent,
                memory_mb=info.memory_mb,
                memory_percent=info.memory_percent,
                threads=info.threads,
                status=info.status
            )
            
            info.metrics_history.append(metrics)
            
            # Limit history size
            if len(info.metrics_history) > self.max_history:
                info.metrics_history.pop(0)
            
            return True
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Process no longer exists
            return False
    
    def get_system_metrics(self) -> Dict:
        """
        Get overall system metrics
        
        Returns:
            Dictionary with system CPU, memory, and process counts
        """
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "cpu_count": psutil.cpu_count(),
            "memory_total_mb": psutil.virtual_memory().total / (1024 * 1024),
            "memory_used_mb": psutil.virtual_memory().used / (1024 * 1024),
            "memory_percent": psutil.virtual_memory().percent,
            "process_count": len(psutil.pids())
        }
    
    def get_all_processes(self) -> List[ProcessInfo]:
        """
        Get list of all running processes
        
        Returns:
            List of ProcessInfo objects
        """
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status']):
            try:
                info = ProcessInfo(
                    pid=proc.info['pid'],
                    name=proc.info['name'],
                    cmdline=[],
                    create_time=datetime.now(),
                    status=proc.info['status'],
                    username=proc.info.get('username', 'N/A')
                )
                processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return processes
