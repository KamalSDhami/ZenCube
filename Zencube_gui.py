#!/usr/bin/env python3
"""
ZenCube GUI - Graphical User Interface for ZenCube Sandbox
Author: Kamal Singh Dhami
Date: October 12, 2025
Description: Modern GUI for executing commands in ZenCube sandbox with resource limits
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import os
import sys
from pathlib import Path

class ZenCubeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ZenCube Sandbox - GUI Controller")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        
        # Set color scheme
        self.bg_color = "#2b2b2b"
        self.fg_color = "#ffffff"
        self.accent_color = "#4a9eff"
        self.button_color = "#3d3d3d"
        
        # Configure root background
        self.root.configure(bg=self.bg_color)
        
        # Variables for resource limits
        self.cpu_enabled = tk.BooleanVar(value=False)
        self.cpu_limit = tk.StringVar(value="5")
        
        self.mem_enabled = tk.BooleanVar(value=False)
        self.mem_limit = tk.StringVar(value="256")
        
        self.procs_enabled = tk.BooleanVar(value=False)
        self.procs_limit = tk.StringVar(value="10")
        
        self.fsize_enabled = tk.BooleanVar(value=False)
        self.fsize_limit = tk.StringVar(value="100")
        
        # WSL option (auto-detect Windows)
        import platform
        is_windows = platform.system() == "Windows"
        self.use_wsl = tk.BooleanVar(value=is_windows)
        
        # Command and file path
        self.command_path = tk.StringVar(value="")
        self.command_args = tk.StringVar(value="")
        
        # Detect sandbox path
        self.sandbox_path = self.detect_sandbox_path()
        
        # Create UI
        self.create_widgets()
        
        # Center window
        self.center_window()
    
    def detect_sandbox_path(self):
        """Detect the sandbox binary path"""
        # Get the directory where the GUI script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        possible_paths = [
            "./sandbox",                                      # Current directory
            os.path.join(script_dir, "sandbox"),             # Same dir as script
            "./zencube/sandbox",                             # Subdirectory
            "../sandbox",                                     # Parent directory
            os.path.join(script_dir, "..", "sandbox"),       # Parent of script dir
            "/usr/local/bin/sandbox",                        # System install
            os.path.expanduser("~/zencube/sandbox")          # User home
        ]
        
        for path in possible_paths:
            full_path = os.path.abspath(path)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                # Check if file is executable (Linux/Unix)
                import platform
                if platform.system() != "Windows":
                    if os.access(full_path, os.X_OK):
                        return path
                else:
                    return path
        
        # If not found, return default and show warning
        return "./sandbox"  # Default fallback
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # ===== HEADER =====
        self.create_header(main_frame)
        
        # ===== FILE SELECTION SECTION =====
        self.create_file_section(main_frame)
        
        # ===== RESOURCE LIMITS SECTION =====
        self.create_limits_section(main_frame)
        
        # ===== OUTPUT TERMINAL SECTION =====
        self.create_output_section(main_frame)
        
        # ===== CONTROL BUTTONS =====
        self.create_control_buttons(main_frame)
        
        # ===== STATUS BAR =====
        self.create_status_bar()
    
    def create_header(self, parent):
        """Create header with title and logo"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="🧊 ZenCube Sandbox Controller",
            font=("Helvetica", 20, "bold")
        )
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Subtitle
        subtitle_label = ttk.Label(
            header_frame,
            text="Execute commands safely with resource limits",
            font=("Helvetica", 10)
        )
        subtitle_label.grid(row=1, column=0, sticky=tk.W)
    
    def create_file_section(self, parent):
        """Create file selection section"""
        file_frame = ttk.LabelFrame(parent, text="Command Selection", padding="10")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # Command/File path
        ttk.Label(file_frame, text="Command/File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        command_entry = ttk.Entry(file_frame, textvariable=self.command_path, width=50)
        command_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        browse_btn = ttk.Button(
            file_frame,
            text="Browse...",
            command=self.browse_file,
            width=12
        )
        browse_btn.grid(row=0, column=2, padx=5)
        
        # Command arguments
        ttk.Label(file_frame, text="Arguments:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        
        args_entry = ttk.Entry(file_frame, textvariable=self.command_args, width=50)
        args_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=(10, 0))
        
        # Quick commands
        ttk.Label(file_frame, text="Quick Commands:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        
        quick_frame = ttk.Frame(file_frame)
        quick_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        quick_commands = [
            ("/bin/ls", "-la"),
            ("/bin/echo", "Hello ZenCube!"),
            ("/usr/bin/whoami", ""),
            ("./tests/infinite_loop", ""),
            ("./tests/memory_hog", ""),
        ]
        
        for i, (cmd, args) in enumerate(quick_commands):
            btn = ttk.Button(
                quick_frame,
                text=cmd.split('/')[-1],
                command=lambda c=cmd, a=args: self.set_quick_command(c, a),
                width=12
            )
            btn.grid(row=0, column=i, padx=2)
    
    def create_limits_section(self, parent):
        """Create resource limits section"""
        limits_frame = ttk.LabelFrame(parent, text="Resource Limits", padding="10")
        limits_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Create a grid layout for limits
        limits_frame.columnconfigure(1, weight=1)
        limits_frame.columnconfigure(3, weight=1)
        
        # CPU Limit
        cpu_check = ttk.Checkbutton(
            limits_frame,
            text="CPU Time (seconds)",
            variable=self.cpu_enabled,
            command=self.update_limit_states
        )
        cpu_check.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.cpu_entry = ttk.Entry(limits_frame, textvariable=self.cpu_limit, width=10, state='disabled')
        self.cpu_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(limits_frame, text="(Default: 5s)").grid(row=0, column=2, sticky=tk.W, padx=5)
        
        # Memory Limit
        mem_check = ttk.Checkbutton(
            limits_frame,
            text="Memory (MB)",
            variable=self.mem_enabled,
            command=self.update_limit_states
        )
        mem_check.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.mem_entry = ttk.Entry(limits_frame, textvariable=self.mem_limit, width=10, state='disabled')
        self.mem_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(limits_frame, text="(Default: 256 MB)").grid(row=1, column=2, sticky=tk.W, padx=5)
        
        # Process Limit
        procs_check = ttk.Checkbutton(
            limits_frame,
            text="Max Processes",
            variable=self.procs_enabled,
            command=self.update_limit_states
        )
        procs_check.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.procs_entry = ttk.Entry(limits_frame, textvariable=self.procs_limit, width=10, state='disabled')
        self.procs_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(limits_frame, text="(Default: 10)").grid(row=2, column=2, sticky=tk.W, padx=5)
        
        # File Size Limit
        fsize_check = ttk.Checkbutton(
            limits_frame,
            text="File Size (MB)",
            variable=self.fsize_enabled,
            command=self.update_limit_states
        )
        fsize_check.grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.fsize_entry = ttk.Entry(limits_frame, textvariable=self.fsize_limit, width=10, state='disabled')
        self.fsize_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(limits_frame, text="(Default: 100 MB)").grid(row=3, column=2, sticky=tk.W, padx=5)
        
        # Preset buttons
        preset_frame = ttk.Frame(limits_frame)
        preset_frame.grid(row=4, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(preset_frame, text="Presets:").grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(preset_frame, text="No Limits", command=self.preset_none, width=12).grid(row=0, column=1, padx=2)
        ttk.Button(preset_frame, text="Light", command=self.preset_light, width=12).grid(row=0, column=2, padx=2)
        ttk.Button(preset_frame, text="Medium", command=self.preset_medium, width=12).grid(row=0, column=3, padx=2)
        ttk.Button(preset_frame, text="Strict", command=self.preset_strict, width=12).grid(row=0, column=4, padx=2)
        
        # WSL option
        wsl_frame = ttk.Frame(limits_frame)
        wsl_frame.grid(row=5, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))
        
        wsl_check = ttk.Checkbutton(
            wsl_frame,
            text="Use WSL (Windows Subsystem for Linux)",
            variable=self.use_wsl,
            command=self.update_wsl_status
        )
        wsl_check.grid(row=0, column=0, sticky=tk.W)
        
        import platform
        if platform.system() == "Windows":
            ttk.Label(wsl_frame, text="(Auto-detected: Windows)", foreground="green").grid(row=0, column=1, padx=(10, 0))
        else:
            ttk.Label(wsl_frame, text="(Auto-detected: Linux/Unix)", foreground="blue").grid(row=0, column=1, padx=(10, 0))
    
    def create_output_section(self, parent):
        """Create output terminal section"""
        output_frame = ttk.LabelFrame(parent, text="Output Terminal", padding="10")
        output_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        # Create scrolled text widget
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=("Courier", 10),
            bg="#1e1e1e",
            fg="#00ff00",
            insertbackground="#00ff00"
        )
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add tags for colored output
        self.output_text.tag_configure("error", foreground="#ff4444")
        self.output_text.tag_configure("success", foreground="#44ff44")
        self.output_text.tag_configure("warning", foreground="#ffaa00")
        self.output_text.tag_configure("info", foreground="#4a9eff")
        
        # Initial message
        self.log_output("🧊 ZenCube Sandbox Terminal\n", "info")
        self.log_output("=" * 80 + "\n", "info")
        self.log_output("Ready to execute commands. Select a file and configure limits.\n\n", "success")
        
        # Check if sandbox exists
        self.validate_sandbox_exists()
    
    def validate_sandbox_exists(self):
        """Check if sandbox binary exists and warn if not"""
        if not os.path.exists(self.sandbox_path):
            self.log_output("⚠️ WARNING: Sandbox binary not found!\n", "warning")
            self.log_output(f"   Looking for: {self.sandbox_path}\n", "warning")
            self.log_output(f"   Current directory: {os.getcwd()}\n", "info")
            self.log_output("\n💡 To fix this:\n", "info")
            self.log_output("   1. Make sure you're in the correct directory\n", "info")
            self.log_output("   2. Build the sandbox: cd zencube && make\n", "info")
            self.log_output("   3. Or run GUI from zencube directory: cd zencube && python Zencube_gui.py\n\n", "info")
        else:
            # Check if executable on Linux
            import platform
            if platform.system() != "Windows":
                if not os.access(self.sandbox_path, os.X_OK):
                    self.log_output("⚠️ WARNING: Sandbox found but not executable!\n", "warning")
                    self.log_output(f"   Run: chmod +x {self.sandbox_path}\n\n", "info")
                else:
                    self.log_output(f"✅ Sandbox found: {self.sandbox_path}\n", "success")
            else:
                self.log_output(f"✅ Sandbox found: {self.sandbox_path}\n", "success")
    
    def create_control_buttons(self, parent):
        """Create control buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Execute button (large and prominent)
        self.execute_btn = ttk.Button(
            button_frame,
            text="▶ Execute Command",
            command=self.execute_command,
            width=20
        )
        self.execute_btn.grid(row=0, column=0, padx=5)
        
        # Stop button
        self.stop_btn = ttk.Button(
            button_frame,
            text="⏹ Stop",
            command=self.stop_execution,
            state='disabled',
            width=15
        )
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        # Clear output button
        ttk.Button(
            button_frame,
            text="🗑 Clear Output",
            command=self.clear_output,
            width=15
        ).grid(row=0, column=2, padx=5)
        
        # Help button
        ttk.Button(
            button_frame,
            text="❓ Help",
            command=self.show_help,
            width=15
        ).grid(row=0, column=3, padx=5)
        
        # Settings button
        ttk.Button(
            button_frame,
            text="⚙️ Settings",
            command=self.show_settings,
            width=15
        ).grid(row=0, column=4, padx=5)
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        import platform
        os_name = platform.system()
        wsl_status = "WSL Mode" if self.use_wsl.get() else "Native Mode"
        
        self.status_bar = ttk.Label(
            self.root,
            text=f"Ready | OS: {os_name} | {wsl_status} | Sandbox: {self.sandbox_path}",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    def browse_file(self):
        """Open file browser dialog"""
        filename = filedialog.askopenfilename(
            title="Select Command/Executable",
            filetypes=[
                ("Executables", "*"),
                ("Shell Scripts", "*.sh"),
                ("Python Scripts", "*.py"),
                ("All Files", "*.*")
            ]
        )
        
        if filename:
            # Warn if user selected a source file instead of executable
            if filename.endswith('.c') or filename.endswith('.cpp'):
                self.log_output(f"⚠️ Warning: You selected a source file ({filename})\n", "warning")
                self.log_output(f"💡 Tip: Select the compiled executable (without .c extension)\n", "info")
                
                # Try to suggest the executable name
                executable = filename.rsplit('.', 1)[0]
                self.log_output(f"💡 Try selecting: {executable}\n", "info")
            
            self.command_path.set(filename)
            self.log_output(f"📁 Selected file: {filename}\n", "info")
            
            # Show WSL path conversion
            wsl_path = self.convert_to_wsl_path(filename)
            if wsl_path != filename:
                self.log_output(f"🔄 WSL path: {wsl_path}\n", "info")
    
    def set_quick_command(self, command, args):
        """Set a quick command"""
        self.command_path.set(command)
        self.command_args.set(args)
        self.log_output(f"⚡ Quick command set: {command} {args}\n", "info")
    
    def update_limit_states(self):
        """Enable/disable entry fields based on checkboxes"""
        self.cpu_entry.config(state='normal' if self.cpu_enabled.get() else 'disabled')
        self.mem_entry.config(state='normal' if self.mem_enabled.get() else 'disabled')
        self.procs_entry.config(state='normal' if self.procs_enabled.get() else 'disabled')
        self.fsize_entry.config(state='normal' if self.fsize_enabled.get() else 'disabled')
    
    def update_wsl_status(self):
        """Update status when WSL checkbox changes"""
        if self.use_wsl.get():
            self.log_output("🔄 WSL mode enabled - Commands will run via WSL\n", "info")
        else:
            self.log_output("🐧 Native mode enabled - Commands will run directly\n", "info")
    
    def preset_none(self):
        """Disable all limits"""
        self.cpu_enabled.set(False)
        self.mem_enabled.set(False)
        self.procs_enabled.set(False)
        self.fsize_enabled.set(False)
        self.update_limit_states()
        self.log_output("📋 Preset applied: No Limits\n", "info")
    
    def preset_light(self):
        """Apply light limits"""
        self.cpu_enabled.set(True)
        self.cpu_limit.set("30")
        self.mem_enabled.set(True)
        self.mem_limit.set("1024")
        self.procs_enabled.set(False)
        self.fsize_enabled.set(False)
        self.update_limit_states()
        self.log_output("📋 Preset applied: Light (CPU: 30s, Memory: 1GB)\n", "info")
    
    def preset_medium(self):
        """Apply medium limits"""
        self.cpu_enabled.set(True)
        self.cpu_limit.set("10")
        self.mem_enabled.set(True)
        self.mem_limit.set("512")
        self.procs_enabled.set(True)
        self.procs_limit.set("10")
        self.fsize_enabled.set(False)
        self.update_limit_states()
        self.log_output("📋 Preset applied: Medium (CPU: 10s, Memory: 512MB, Procs: 10)\n", "info")
    
    def preset_strict(self):
        """Apply strict limits"""
        self.cpu_enabled.set(True)
        self.cpu_limit.set("5")
        self.mem_enabled.set(True)
        self.mem_limit.set("256")
        self.procs_enabled.set(True)
        self.procs_limit.set("5")
        self.fsize_enabled.set(True)
        self.fsize_limit.set("50")
        self.update_limit_states()
        self.log_output("📋 Preset applied: Strict (All limits enabled)\n", "info")
    
    def log_output(self, message, tag=None):
        """Add message to output terminal"""
        self.output_text.insert(tk.END, message, tag)
        self.output_text.see(tk.END)
        self.output_text.update()
    
    def clear_output(self):
        """Clear output terminal"""
        self.output_text.delete(1.0, tk.END)
        self.log_output("🧊 ZenCube Sandbox Terminal\n", "info")
        self.log_output("=" * 80 + "\n", "info")
        self.log_output("Output cleared.\n\n", "success")
    
    def convert_to_wsl_path(self, windows_path):
        """Convert Windows path to WSL path format"""
        # If WSL is not enabled, return path as-is
        if not self.use_wsl.get():
            return windows_path
        
        # If it's already a relative path or starts with /, return as-is
        if not ':' in windows_path:
            return windows_path
        
        # Convert Windows path to WSL format
        # C:/Users/... -> /mnt/c/Users/...
        path = windows_path.replace('\\', '/')
        
        # Check if it's an absolute Windows path (e.g., C:/ or C:\)
        if len(path) > 1 and path[1] == ':':
            drive = path[0].lower()
            rest = path[2:]  # Everything after "C:"
            wsl_path = f"/mnt/{drive}{rest}"
            return wsl_path
        
        return path
    
    def build_command(self):
        """Build the sandbox command with all options"""
        command = self.command_path.get().strip()
        args = self.command_args.get().strip()
        
        if not command:
            raise ValueError("No command specified")
        
        # Convert Windows path to WSL path if needed
        wsl_command = self.convert_to_wsl_path(command)
        
        # Build command - with or without WSL prefix
        if self.use_wsl.get():
            cmd_parts = ["wsl", self.sandbox_path]
        else:
            cmd_parts = [self.sandbox_path]
        
        # Add resource limits
        if self.cpu_enabled.get():
            cpu_val = self.cpu_limit.get().strip()
            if cpu_val:
                cmd_parts.append(f"--cpu={cpu_val}")
        
        if self.mem_enabled.get():
            mem_val = self.mem_limit.get().strip()
            if mem_val:
                cmd_parts.append(f"--mem={mem_val}")
        
        if self.procs_enabled.get():
            procs_val = self.procs_limit.get().strip()
            if procs_val:
                cmd_parts.append(f"--procs={procs_val}")
        
        if self.fsize_enabled.get():
            fsize_val = self.fsize_limit.get().strip()
            if fsize_val:
                cmd_parts.append(f"--fsize={fsize_val}")
        
        # Add command and arguments (use WSL path if WSL enabled)
        cmd_parts.append(wsl_command)
        if args:
            cmd_parts.extend(args.split())
        
        return cmd_parts
    
    def execute_command(self):
        """Execute the sandbox command in a separate thread"""
        try:
            # Validate command before execution
            command = self.command_path.get().strip()
            if not command:
                raise ValueError("No command specified. Please enter a command or use Browse.")
            
            # Check if user accidentally selected a source file
            if command.endswith('.c') or command.endswith('.cpp'):
                error_msg = (
                    "⚠️ Cannot execute source file!\n\n"
                    f"You selected: {command}\n\n"
                    "Please select the compiled executable (without .c extension).\n"
                    f"Try: {command.rsplit('.', 1)[0]}"
                )
                messagebox.showerror("Invalid File Type", error_msg)
                self.log_output(f"❌ Error: Cannot execute source file: {command}\n", "error")
                self.log_output(f"💡 Select the executable: {command.rsplit('.', 1)[0]}\n", "info")
                return
            
            cmd_parts = self.build_command()
            
            # Log command
            self.log_output("\n" + "=" * 80 + "\n", "info")
            self.log_output(f"🚀 Executing: {' '.join(cmd_parts)}\n", "info")
            self.log_output("=" * 80 + "\n", "info")
            
            # Update UI state
            self.execute_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.status_bar.config(text="Running...")
            
            # Execute in thread
            thread = threading.Thread(target=self.run_command, args=(cmd_parts,), daemon=True)
            thread.start()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            self.log_output(f"❌ Error: {e}\n", "error")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute command: {e}")
            self.log_output(f"❌ Unexpected error: {e}\n", "error")
    
    def run_command(self, cmd_parts):
        """Run command in subprocess"""
        try:
            self.process = subprocess.Popen(
                cmd_parts,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output line by line
            for line in self.process.stdout:
                self.root.after(0, self.log_output, line)
            
            # Wait for process to complete
            self.process.wait()
            exit_code = self.process.returncode
            
            # Log completion
            if exit_code == 0:
                self.root.after(0, self.log_output, f"\n✅ Command completed successfully (exit code: {exit_code})\n", "success")
            else:
                self.root.after(0, self.log_output, f"\n⚠️ Command exited with code: {exit_code}\n", "warning")
            
        except Exception as e:
            self.root.after(0, self.log_output, f"\n❌ Execution error: {e}\n", "error")
        
        finally:
            # Reset UI state
            self.root.after(0, self.execute_btn.config, {'state': 'normal'})
            self.root.after(0, self.stop_btn.config, {'state': 'disabled'})
            self.root.after(0, self.status_bar.config, {'text': 'Ready'})
            self.process = None
    
    def stop_execution(self):
        """Stop the currently running command"""
        if hasattr(self, 'process') and self.process:
            self.process.terminate()
            self.log_output("\n🛑 Execution stopped by user\n", "warning")
            self.status_bar.config(text="Stopped")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
ZenCube Sandbox GUI - Help

USAGE:
1. Select a command/file using the Browse button or Quick Commands
2. (Optional) Add command-line arguments
3. Enable resource limits as needed:
   - CPU Time: Limit execution time in seconds
   - Memory: Limit memory usage in megabytes
   - Max Processes: Prevent fork bombs
   - File Size: Limit file writes in megabytes
4. Toggle WSL option (Windows users should keep this enabled)
5. Click "Execute Command" to run
6. View output in the terminal area

PRESETS:
- No Limits: Run without any restrictions
- Light: Generous limits for development
- Medium: Balanced limits for testing
- Strict: Tight limits for untrusted code

WSL OPTION:
- Enabled: Commands run through WSL (for Windows users)
- Disabled: Commands run directly (for Linux/Unix users)
- Auto-detected based on your operating system

TIPS:
- Use test programs in ./tests/ to verify limits
- Check output terminal for detailed execution logs
- Use Stop button to terminate long-running processes
- Linux users should uncheck WSL for native execution

For more information, see README.md
        """
        
        messagebox.showinfo("ZenCube Help", help_text)
    
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("ZenCube Settings")
        settings_window.geometry("600x300")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Center the dialog
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() // 2) - (300)
        y = (settings_window.winfo_screenheight() // 2) - (150)
        settings_window.geometry(f'600x300+{x}+{y}')
        
        # Main frame
        main_frame = ttk.Frame(settings_window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        ttk.Label(
            main_frame,
            text="⚙️ ZenCube Settings",
            font=("Helvetica", 14, "bold")
        ).grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Sandbox Path Setting
        ttk.Label(main_frame, text="Sandbox Binary Path:").grid(row=1, column=0, sticky=tk.W, pady=10)
        
        sandbox_var = tk.StringVar(value=self.sandbox_path)
        sandbox_entry = ttk.Entry(main_frame, textvariable=sandbox_var, width=40)
        sandbox_entry.grid(row=1, column=1, padx=10, pady=10)
        
        def browse_sandbox():
            filename = filedialog.askopenfilename(
                title="Select Sandbox Binary",
                filetypes=[("Executable", "*"), ("All Files", "*.*")]
            )
            if filename:
                sandbox_var.set(filename)
        
        ttk.Button(
            main_frame,
            text="Browse...",
            command=browse_sandbox
        ).grid(row=1, column=2, pady=10)
        
        # Current Status
        ttk.Label(main_frame, text="Current Status:").grid(row=2, column=0, sticky=tk.W, pady=10)
        
        status_text = tk.Text(main_frame, height=4, width=50, wrap=tk.WORD)
        status_text.grid(row=2, column=1, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        current_path = os.path.abspath(self.sandbox_path)
        exists = os.path.exists(current_path)
        executable = os.access(current_path, os.X_OK) if exists else False
        
        status_text.insert("1.0", f"Path: {current_path}\n")
        status_text.insert("end", f"Exists: {'✅ Yes' if exists else '❌ No'}\n")
        status_text.insert("end", f"Executable: {'✅ Yes' if executable else '❌ No'}\n")
        status_text.insert("end", f"Working Dir: {os.getcwd()}")
        status_text.config(state='disabled')
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(20, 0))
        
        def apply_settings():
            new_path = sandbox_var.get().strip()
            if new_path:
                self.sandbox_path = new_path
                self.log_output(f"\n⚙️ Sandbox path updated to: {new_path}\n", "info")
                self.validate_sandbox_exists()
                # Update status bar
                import platform
                os_name = platform.system()
                wsl_status = "WSL Mode" if self.use_wsl.get() else "Native Mode"
                self.status_bar.config(text=f"Ready | OS: {os_name} | {wsl_status} | Sandbox: {self.sandbox_path}")
                settings_window.destroy()
        
        def reset_to_default():
            self.sandbox_path = self.detect_sandbox_path()
            sandbox_var.set(self.sandbox_path)
            self.log_output(f"\n🔄 Sandbox path reset to: {self.sandbox_path}\n", "info")
        
        ttk.Button(button_frame, text="Apply", command=apply_settings, width=15).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Reset to Default", command=reset_to_default, width=15).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy, width=15).grid(row=0, column=2, padx=5)

def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Set style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Create app
    app = ZenCubeGUI(root)
    
    # Start main loop
    root.mainloop()

if __name__ == "__main__":
    main()
