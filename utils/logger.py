"""
Execution Logger
Logs sandbox execution history and events
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class ExecutionLog:
    """Represents a single execution log entry"""
    timestamp: str
    command: str
    arguments: List[str]
    pid: int
    exit_code: int
    execution_time: float
    cpu_limit: int
    memory_limit: int
    timeout: int
    success: bool
    terminated_by_signal: bool
    signal_name: Optional[str] = None
    cpu_limit_exceeded: bool = False
    memory_limit_exceeded: bool = False
    timeout_exceeded: bool = False
    output: str = ""
    error: str = ""


class ExecutionLogger:
    """Manages execution history and logging"""
    
    def __init__(self, log_file: str = "execution_history.json", max_entries: int = 1000):
        """
        Initialize execution logger
        
        Args:
            log_file: Path to log file
            max_entries: Maximum number of entries to keep in memory
        """
        self.log_file = log_file
        self.max_entries = max_entries
        self.history: List[ExecutionLog] = []
        
        # Load existing history
        self._load_history()
    
    def log_execution(self, 
                     command: str,
                     arguments: List[str],
                     result: 'SandboxResult',
                     cpu_limit: int = 0,
                     memory_limit: int = 0,
                     timeout: int = 0):
        """
        Log an execution
        
        Args:
            command: Command that was executed
            arguments: Command arguments
            result: SandboxResult object
            cpu_limit: CPU limit used
            memory_limit: Memory limit used
            timeout: Timeout used
        """
        log_entry = ExecutionLog(
            timestamp=datetime.now().isoformat(),
            command=command,
            arguments=arguments,
            pid=result.pid,
            exit_code=result.exit_code,
            execution_time=result.execution_time,
            cpu_limit=cpu_limit,
            memory_limit=memory_limit,
            timeout=timeout,
            success=result.success,
            terminated_by_signal=result.terminated_by_signal,
            signal_name=result.signal_name,
            cpu_limit_exceeded=result.cpu_limit_exceeded,
            memory_limit_exceeded=result.memory_limit_exceeded,
            timeout_exceeded=result.timeout_exceeded,
            output=result.output[:500],  # Limit output length
            error=result.error[:500]
        )
        
        self.history.append(log_entry)
        
        # Limit history size
        if len(self.history) > self.max_entries:
            self.history.pop(0)
        
        # Save to file
        self._save_history()
    
    def get_history(self, limit: Optional[int] = None) -> List[ExecutionLog]:
        """
        Get execution history
        
        Args:
            limit: Maximum number of entries to return (None = all)
            
        Returns:
            List of ExecutionLog entries
        """
        if limit:
            return self.history[-limit:]
        return self.history
    
    def get_statistics(self) -> Dict:
        """
        Get execution statistics
        
        Returns:
            Dictionary with statistics
        """
        if not self.history:
            return {
                "total_executions": 0,
                "successful": 0,
                "failed": 0,
                "avg_execution_time": 0.0,
                "cpu_limit_exceeded": 0,
                "memory_limit_exceeded": 0,
                "timeout_exceeded": 0
            }
        
        successful = sum(1 for log in self.history if log.success)
        failed = len(self.history) - successful
        avg_time = sum(log.execution_time for log in self.history) / len(self.history)
        
        return {
            "total_executions": len(self.history),
            "successful": successful,
            "failed": failed,
            "avg_execution_time": avg_time,
            "cpu_limit_exceeded": sum(1 for log in self.history if log.cpu_limit_exceeded),
            "memory_limit_exceeded": sum(1 for log in self.history if log.memory_limit_exceeded),
            "timeout_exceeded": sum(1 for log in self.history if log.timeout_exceeded)
        }
    
    def clear_history(self):
        """Clear all execution history"""
        self.history = []
        self._save_history()
    
    def export_history(self, filename: str) -> bool:
        """
        Export history to a file
        
        Args:
            filename: Output filename
            
        Returns:
            True if export successful
        """
        try:
            with open(filename, 'w') as f:
                json.dump([asdict(log) for log in self.history], f, indent=2)
            return True
        except Exception:
            return False
    
    def _load_history(self):
        """Load history from file"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.history = [ExecutionLog(**entry) for entry in data]
            except Exception:
                self.history = []
    
    def _save_history(self):
        """Save history to file"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump([asdict(log) for log in self.history], f, indent=2)
        except Exception:
            pass
