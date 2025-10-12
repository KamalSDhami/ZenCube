#define _GNU_SOURCE
#define _POSIX_C_SOURCE 199309L

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <sys/resource.h>
#include <errno.h>
#include <string.h>
#include <time.h>
#include <stdarg.h>
#include <signal.h>
#include <limits.h>

/**
 * ZenCube Sandbox Runner - Phase 2
 * 
 * A sandbox implementation with resource limits to prevent runaway processes.
 * Supports CPU time, memory, process count, and file size restrictions.
 * 
 * Features:
 * - CPU time limits (RLIMIT_CPU)
 * - Memory limits (RLIMIT_AS)
 * - Process count limits (RLIMIT_NPROC)
 * - File size limits (RLIMIT_FSIZE)
 * 
 * Author: Systems Programming Team
 * Date: October 2025
 */

/* Structure to hold resource limit configuration */
typedef struct {
    int cpu_seconds;      /* CPU time limit in seconds (0 = unlimited) */
    long memory_mb;       /* Memory limit in MB (0 = unlimited) */
    int max_processes;    /* Maximum number of processes (0 = unlimited) */
    long max_file_mb;     /* Maximum file size in MB (0 = unlimited) */
} ResourceLimits;

/* Function prototypes */
void print_usage(const char *program_name);
void log_message(const char *format, ...);
void log_command(int argc, char *argv[], int start_index);
double timespec_diff(struct timespec *start, struct timespec *end);
int parse_arguments(int argc, char *argv[], ResourceLimits *limits, int *cmd_start_index);
int apply_resource_limits(const ResourceLimits *limits);
void log_resource_limits(const ResourceLimits *limits);

/**
 * Print usage information for the sandbox program
 */
void print_usage(const char *program_name) {
    printf("Usage: %s [OPTIONS] <command> [arguments...]\n", program_name);
    printf("\nDescription:\n");
    printf("  Execute a command in a sandbox with resource limits.\n");
    printf("  The command will run as a child process with enforced constraints.\n");
    printf("\nOptions:\n");
    printf("  --cpu=<seconds>      Limit CPU time (default: unlimited)\n");
    printf("  --mem=<MB>           Limit memory in megabytes (default: unlimited)\n");
    printf("  --procs=<count>      Limit number of processes (default: unlimited)\n");
    printf("  --fsize=<MB>         Limit file size in megabytes (default: unlimited)\n");
    printf("  --help               Display this help message\n");
    printf("\nExamples:\n");
    printf("  %s /bin/ls -l /\n", program_name);
    printf("  %s --cpu=5 /bin/sleep 10\n", program_name);
    printf("  %s --mem=256 --cpu=10 ./memory_test\n", program_name);
    printf("  %s --procs=5 --fsize=100 ./app\n", program_name);
    printf("\nResource Limit Signals:\n");
    printf("  SIGXCPU - CPU time limit exceeded\n");
    printf("  SIGKILL - Memory limit exceeded (kernel kill)\n");
}

/**
 * Log a formatted message with timestamp and sandbox prefix
 */
void log_message(const char *format, ...) {
    va_list args;
    time_t raw_time;
    struct tm *time_info;
    char time_buffer[80];
    
    /* Get current time for logging */
    time(&raw_time);
    time_info = localtime(&raw_time);
    strftime(time_buffer, sizeof(time_buffer), "%H:%M:%S", time_info);
    
    printf("[Sandbox %s] ", time_buffer);
    
    va_start(args, format);
    vprintf(format, args);
    va_end(args);
    
    printf("\n");
    fflush(stdout);
}

/**
 * Log the command being executed with all its arguments
 */
void log_command(int argc, char *argv[], int start_index) {
    printf("[Sandbox] Starting command:");
    for (int i = start_index; i < argc; i++) {
        printf(" %s", argv[i]);
    }
    printf("\n");
    fflush(stdout);
}

/**
 * Calculate the difference between two timespec structures in seconds
 */
double timespec_diff(struct timespec *start, struct timespec *end) {
    return (end->tv_sec - start->tv_sec) + (end->tv_nsec - start->tv_nsec) / 1000000000.0;
}

/**
 * Parse command-line arguments and extract resource limits
 * Returns 0 on success, -1 on error
 */
int parse_arguments(int argc, char *argv[], ResourceLimits *limits, int *cmd_start_index) {
    int i = 1;
    
    /* Initialize limits to unlimited (0) */
    limits->cpu_seconds = 0;
    limits->memory_mb = 0;
    limits->max_processes = 0;
    limits->max_file_mb = 0;
    
    /* Parse options */
    while (i < argc && argv[i][0] == '-') {
        if (strcmp(argv[i], "--help") == 0) {
            print_usage(argv[0]);
            exit(EXIT_SUCCESS);
        } else if (strncmp(argv[i], "--cpu=", 6) == 0) {
            limits->cpu_seconds = atoi(argv[i] + 6);
            if (limits->cpu_seconds < 0) {
                fprintf(stderr, "Error: Invalid CPU limit: %s\n", argv[i] + 6);
                return -1;
            }
        } else if (strncmp(argv[i], "--mem=", 6) == 0) {
            limits->memory_mb = atol(argv[i] + 6);
            if (limits->memory_mb < 0) {
                fprintf(stderr, "Error: Invalid memory limit: %s\n", argv[i] + 6);
                return -1;
            }
        } else if (strncmp(argv[i], "--procs=", 8) == 0) {
            limits->max_processes = atoi(argv[i] + 8);
            if (limits->max_processes < 0) {
                fprintf(stderr, "Error: Invalid process limit: %s\n", argv[i] + 8);
                return -1;
            }
        } else if (strncmp(argv[i], "--fsize=", 8) == 0) {
            limits->max_file_mb = atol(argv[i] + 8);
            if (limits->max_file_mb < 0) {
                fprintf(stderr, "Error: Invalid file size limit: %s\n", argv[i] + 8);
                return -1;
            }
        } else {
            fprintf(stderr, "Error: Unknown option: %s\n", argv[i]);
            return -1;
        }
        i++;
    }
    
    *cmd_start_index = i;
    return 0;
}

/**
 * Apply resource limits to the current process
 * Returns 0 on success, -1 on error
 */
int apply_resource_limits(const ResourceLimits *limits) {
    struct rlimit rlim;
    
    /* Apply CPU time limit */
    if (limits->cpu_seconds > 0) {
        rlim.rlim_cur = limits->cpu_seconds;
        rlim.rlim_max = limits->cpu_seconds;
        if (setrlimit(RLIMIT_CPU, &rlim) != 0) {
            fprintf(stderr, "[Sandbox] Error: Failed to set CPU limit: %s\n", strerror(errno));
            return -1;
        }
        log_message("CPU limit set to %d seconds", limits->cpu_seconds);
    }
    
    /* Apply memory limit (address space) */
    if (limits->memory_mb > 0) {
        rlim.rlim_cur = (rlim_t)limits->memory_mb * 1024 * 1024;
        rlim.rlim_max = (rlim_t)limits->memory_mb * 1024 * 1024;
        if (setrlimit(RLIMIT_AS, &rlim) != 0) {
            fprintf(stderr, "[Sandbox] Error: Failed to set memory limit: %s\n", strerror(errno));
            return -1;
        }
        log_message("Memory limit set to %ld MB", limits->memory_mb);
    }
    
    /* Apply process count limit */
    if (limits->max_processes > 0) {
        rlim.rlim_cur = limits->max_processes;
        rlim.rlim_max = limits->max_processes;
        if (setrlimit(RLIMIT_NPROC, &rlim) != 0) {
            fprintf(stderr, "[Sandbox] Error: Failed to set process limit: %s\n", strerror(errno));
            return -1;
        }
        log_message("Process limit set to %d", limits->max_processes);
    }
    
    /* Apply file size limit */
    if (limits->max_file_mb > 0) {
        rlim.rlim_cur = (rlim_t)limits->max_file_mb * 1024 * 1024;
        rlim.rlim_max = (rlim_t)limits->max_file_mb * 1024 * 1024;
        if (setrlimit(RLIMIT_FSIZE, &rlim) != 0) {
            fprintf(stderr, "[Sandbox] Error: Failed to set file size limit: %s\n", strerror(errno));
            return -1;
        }
        log_message("File size limit set to %ld MB", limits->max_file_mb);
    }
    
    return 0;
}

/**
 * Log the active resource limits
 */
void log_resource_limits(const ResourceLimits *limits) {
    if (limits->cpu_seconds > 0 || limits->memory_mb > 0 || 
        limits->max_processes > 0 || limits->max_file_mb > 0) {
        printf("[Sandbox] Active resource limits:\n");
        if (limits->cpu_seconds > 0) {
            printf("  CPU Time: %d seconds\n", limits->cpu_seconds);
        }
        if (limits->memory_mb > 0) {
            printf("  Memory: %ld MB\n", limits->memory_mb);
        }
        if (limits->max_processes > 0) {
            printf("  Processes: %d\n", limits->max_processes);
        }
        if (limits->max_file_mb > 0) {
            printf("  File Size: %ld MB\n", limits->max_file_mb);
        }
    } else {
        printf("[Sandbox] No resource limits applied (unlimited)\n");
    }
}

/**
 * Main sandbox runner function
 */
int main(int argc, char *argv[]) {
    pid_t child_pid;
    int status;
    struct timespec start_time, end_time;
    double execution_time;
    ResourceLimits limits;
    int cmd_start_index;
    
    /* Parse command line arguments and resource limits */
    if (parse_arguments(argc, argv, &limits, &cmd_start_index) != 0) {
        fprintf(stderr, "\n");
        print_usage(argv[0]);
        return EXIT_FAILURE;
    }
    
    /* Check if command is specified */
    if (cmd_start_index >= argc) {
        fprintf(stderr, "Error: No command specified\n\n");
        print_usage(argv[0]);
        return EXIT_FAILURE;
    }
    
    /* Log resource limits */
    log_resource_limits(&limits);
    
    /* Log the command we're about to execute */
    log_command(argc, argv, cmd_start_index);
    
    /* Record start time for timing measurement */
    if (clock_gettime(CLOCK_MONOTONIC, &start_time) == -1) {
        log_message("Warning: Failed to get start time: %s", strerror(errno));
    }
    
    /* Create child process using fork() */
    child_pid = fork();
    
    if (child_pid == -1) {
        /* Fork failed */
        fprintf(stderr, "[Sandbox] Error: Failed to create child process: %s\n", 
                strerror(errno));
        return EXIT_FAILURE;
    }
    
    if (child_pid == 0) {
        /* This is the child process */
        log_message("Child process created (PID: %d)", getpid());
        
        /* Apply resource limits in child process */
        if (apply_resource_limits(&limits) != 0) {
            fprintf(stderr, "[Sandbox] Child Error: Failed to apply resource limits\n");
            exit(EXIT_FAILURE);
        }
        
        /* Replace process image with target command using execvp() */
        /* execvp() automatically searches PATH for the executable */
        if (execvp(argv[cmd_start_index], &argv[cmd_start_index]) == -1) {
            /* execvp() failed - this only executes if exec fails */
            fprintf(stderr, "[Sandbox] Child Error: Failed to execute '%s': %s\n", 
                    argv[cmd_start_index], strerror(errno));
            exit(EXIT_FAILURE);
        }
        
        /* This line should never be reached if execvp() succeeds */
        exit(EXIT_FAILURE);
    } else {
        /* This is the parent process */
        log_message("Child PID: %d", child_pid);
        
        /* Wait for child process to complete */
        pid_t wait_result = waitpid(child_pid, &status, 0);
        
        /* Record end time */
        if (clock_gettime(CLOCK_MONOTONIC, &end_time) == -1) {
            log_message("Warning: Failed to get end time: %s", strerror(errno));
            execution_time = -1.0;  /* Indicate timing failed */
        } else {
            execution_time = timespec_diff(&start_time, &end_time);
        }
        
        if (wait_result == -1) {
            fprintf(stderr, "[Sandbox] Error: waitpid() failed: %s\n", strerror(errno));
            return EXIT_FAILURE;
        }
        
        /* Analyze and log child process exit status */
        if (WIFEXITED(status)) {
            /* Child exited normally */
            int exit_code = WEXITSTATUS(status);
            log_message("Process exited normally with status %d", exit_code);
            
            if (execution_time >= 0) {
                log_message("Execution time: %.3f seconds", execution_time);
            }
            
            /* Return the same exit code as the child process */
            return exit_code;
        } else if (WIFSIGNALED(status)) {
            /* Child was terminated by a signal */
            int signal_num = WTERMSIG(status);
            log_message("Process terminated by signal %d (%s)", 
                       signal_num, strsignal(signal_num));
            
            /* Provide specific information for resource limit signals */
            if (signal_num == SIGXCPU) {
                log_message("⚠️  RESOURCE LIMIT VIOLATED: CPU time limit exceeded");
                log_message("The process used more CPU time than allowed (%d seconds)", 
                           limits.cpu_seconds);
            } else if (signal_num == SIGKILL) {
                log_message("⚠️  Process was killed (possibly by memory limit)");
                if (limits.memory_mb > 0) {
                    log_message("Memory limit was set to %ld MB", limits.memory_mb);
                }
            } else if (signal_num == SIGXFSZ) {
                log_message("⚠️  RESOURCE LIMIT VIOLATED: File size limit exceeded");
                if (limits.max_file_mb > 0) {
                    log_message("File size limit was set to %ld MB", limits.max_file_mb);
                }
            }
            
            if (execution_time >= 0) {
                log_message("Execution time before termination: %.3f seconds", execution_time);
            }
            
            /* Check if core dump was created */
            if (WCOREDUMP(status)) {
                log_message("Core dump was created");
            }
            
            return EXIT_FAILURE;
        } else if (WIFSTOPPED(status)) {
            /* Child was stopped (shouldn't happen with our waitpid call) */
            int stop_signal = WSTOPSIG(status);
            log_message("Process stopped by signal %d", stop_signal);
            return EXIT_FAILURE;
        } else {
            /* Unknown status */
            log_message("Process ended with unknown status: %d", status);
            return EXIT_FAILURE;
        }
    }
    
    return EXIT_SUCCESS;
}