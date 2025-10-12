"""
ZenCube Sandbox Wrapper
Provides Python interface to the C sandbox executable
"""

import subprocess
import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SandboxResult:
    """Represents the result of a sandbox execution"""
    pid: int
    exit_code: int
    execution_time: float
    terminated_by_signal: bool
    signal_number: Optional[int] = None
    signal_name: Optional[str] = None
    cpu_limit_exceeded: bool = False
    memory_limit_exceeded: bool = False
    timeout_exceeded: bool = False
    success: bool = False
    output: str = ""
    error: str = ""


class SandboxRunner:
    """Interface to run commands in the ZenCube sandbox"""
    
    def __init__(self, sandbox_path: str = "./sandbox_v2"):
        """
        Initialize sandbox runner
        
        Args:
            sandbox_path: Path to the sandbox executable
        """
        self.sandbox_path = sandbox_path
        
        # Verify sandbox exists
        if not os.path.exists(sandbox_path):
            raise FileNotFoundError(f"Sandbox executable not found: {sandbox_path}")
    
    def run(self, 
            command: List[str],
            cpu_limit: int = 0,
            memory_limit: int = 0,
            timeout: int = 0,
            capture_output: bool = True) -> SandboxResult:
        """
        Execute a command in the sandbox
        
        Args:
            command: List of command and arguments to execute
            cpu_limit: CPU time limit in seconds (0 = unlimited)
            memory_limit: Memory limit in MB (0 = unlimited)
            timeout: Wall clock timeout in seconds (0 = unlimited)
            capture_output: Whether to capture stdout/stderr
            
        Returns:
            SandboxResult object with execution details
        """
        # Build sandbox command
        sandbox_cmd = [self.sandbox_path]
        
        if cpu_limit > 0:
            sandbox_cmd.extend(["--cpu", str(cpu_limit)])
        
        if memory_limit > 0:
            sandbox_cmd.extend(["--mem", str(memory_limit)])
        
        if timeout > 0:
            sandbox_cmd.extend(["--timeout", str(timeout)])
        
        # Add JSON flag for structured output
        sandbox_cmd.append("--json")
        
        # Add the actual command
        sandbox_cmd.extend(command)
        
        # Execute the sandbox
        try:
            process = subprocess.Popen(
                sandbox_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            # Parse JSON output from sandbox
            result_data = self._parse_json_output(stdout)
            
            # Create result object
            result = SandboxResult(
                pid=result_data.get("pid", 0),
                exit_code=result_data.get("exit_code", -1),
                execution_time=result_data.get("execution_time", 0.0),
                terminated_by_signal=result_data.get("terminated_by_signal", False),
                signal_number=result_data.get("signal_number"),
                signal_name=result_data.get("signal_name"),
                cpu_limit_exceeded=result_data.get("limit_exceeded", {}).get("cpu", False),
                memory_limit_exceeded=result_data.get("limit_exceeded", {}).get("memory", False),
                timeout_exceeded=result_data.get("limit_exceeded", {}).get("timeout", False),
                success=result_data.get("success", False),
                output=stdout if capture_output else "",
                error=stderr if capture_output else ""
            )
            
            return result
            
        except Exception as e:
            # Return error result
            return SandboxResult(
                pid=0,
                exit_code=-1,
                execution_time=0.0,
                terminated_by_signal=False,
                success=False,
                error=str(e)
            )
    
    def _parse_json_output(self, output: str) -> Dict:
        """
        Parse JSON output from sandbox
        
        Args:
            output: Raw output from sandbox
            
        Returns:
            Dictionary with parsed data
        """
        try:
            # Find JSON object in output
            json_start = output.find("{")
            json_end = output.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = output[json_start:json_end]
                return json.loads(json_str)
            else:
                return {}
        except json.JSONDecodeError:
            return {}
    
    def validate_command(self, command: List[str]) -> tuple[bool, str]:
        """
        Validate that a command can be executed
        
        Args:
            command: Command to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not command or len(command) == 0:
            return False, "Command cannot be empty"
        
        # Check if command exists (basic validation)
        cmd_path = command[0]
        
        # If it's an absolute path, check if it exists
        if os.path.isabs(cmd_path):
            if not os.path.exists(cmd_path):
                return False, f"Command not found: {cmd_path}"
            if not os.access(cmd_path, os.X_OK):
                return False, f"Command is not executable: {cmd_path}"
        
        return True, ""
