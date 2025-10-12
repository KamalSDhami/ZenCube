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
#include <getopt.h>

/**
 * ZenCube Sandbox Runner - Phase 2
 * 
 * Enhanced sandbox with resource limits (CPU, Memory, Time)
 * and JSON output for UI integration.
 * 
 * Author: ZenCube Development Team
 * Date: October 2025
 */

/* Configuration structure */
typedef struct {
    int cpu_limit_seconds;      /* CPU time limit in seconds (0 = no limit) */
    int memory_limit_mb;         /* Memory limit in MB (0 = no limit) */
    int timeout_seconds;         /* Wall clock timeout in seconds (0 = no limit) */
    int json_output;             /* Output in JSON format */
    char **command_argv;         /* Command and arguments to execute */
} sandbox_config_t;

/* Result structure */
typedef struct {
    pid_t pid;
    int exit_code;
    int terminated_by_signal;
    int signal_number;
    double execution_time;
    int cpu_limit_exceeded;
    int memory_limit_exceeded;
    int timeout_exceeded;
} sandbox_result_t;

/* Function prototypes */
void print_usage(const char *program_name);
void log_message(const char *format, ...);
void log_json_result(sandbox_result_t *result, sandbox_config_t *config);
void apply_resource_limits(sandbox_config_t *config);
int parse_arguments(int argc, char *argv[], sandbox_config_t *config);
double timespec_diff(struct timespec *start, struct timespec *end);
int run_sandbox(sandbox_config_t *config, sandbox_result_t *result);

/**
 * Print usage information
 */
void print_usage(const char *program_name) {
    printf("Usage: %s [OPTIONS] <command> [arguments...]\n", program_name);
    printf("\nZenCube Sandbox - Execute commands with resource limits\n");
    printf("\nOptions:\n");
    printf("  --cpu <seconds>      CPU time limit in seconds (default: unlimited)\n");
    printf("  --mem <MB>           Memory limit in MB (default: unlimited)\n");
    printf("  --timeout <seconds>  Wall clock timeout in seconds (default: unlimited)\n");
    printf("  --json               Output results in JSON format\n");
    printf("  -h, --help           Show this help message\n");
    printf("\nExamples:\n");
    printf("  %s --cpu 5 --mem 256 /bin/ls -l\n", program_name);
    printf("  %s --timeout 10 /usr/bin/sleep 15\n", program_name);
    printf("  %s --json --cpu 2 /bin/echo \"Hello\"\n", program_name);
}

/**
 * Log a formatted message with timestamp
 */
void log_message(const char *format, ...) {
    va_list args;
    time_t raw_time;
    struct tm *time_info;
    char time_buffer[80];
    
    time(&raw_time);
    time_info = localtime(&raw_time);
    strftime(time_buffer, sizeof(time_buffer), "%H:%M:%S", time_info);
    
    printf("[ZenCube %s] ", time_buffer);
    
    va_start(args, format);
    vprintf(format, args);
    va_end(args);
    
    printf("\n");
    fflush(stdout);
}

/**
 * Output results in JSON format
 */
void log_json_result(sandbox_result_t *result, sandbox_config_t *config) {
    printf("{\n");
    printf("  \"pid\": %d,\n", result->pid);
    printf("  \"exit_code\": %d,\n", result->exit_code);
    printf("  \"execution_time\": %.3f,\n", result->execution_time);
    printf("  \"terminated_by_signal\": %s,\n", result->terminated_by_signal ? "true" : "false");
    
    if (result->terminated_by_signal) {
        printf("  \"signal_number\": %d,\n", result->signal_number);
        printf("  \"signal_name\": \"%s\",\n", strsignal(result->signal_number));
    }
    
    printf("  \"limits\": {\n");
    printf("    \"cpu_seconds\": %d,\n", config->cpu_limit_seconds);
    printf("    \"memory_mb\": %d,\n", config->memory_limit_mb);
    printf("    \"timeout_seconds\": %d\n", config->timeout_seconds);
    printf("  },\n");
    
    printf("  \"limit_exceeded\": {\n");
    printf("    \"cpu\": %s,\n", result->cpu_limit_exceeded ? "true" : "false");
    printf("    \"memory\": %s,\n", result->memory_limit_exceeded ? "true" : "false");
    printf("    \"timeout\": %s\n", result->timeout_exceeded ? "true" : "false");
    printf("  },\n");
    
    printf("  \"success\": %s\n", (result->exit_code == 0 && !result->terminated_by_signal) ? "true" : "false");
    printf("}\n");
    fflush(stdout);
}

/**
 * Apply resource limits to the current process
 */
void apply_resource_limits(sandbox_config_t *config) {
    struct rlimit limit;
    
    /* Set CPU time limit */
    if (config->cpu_limit_seconds > 0) {
        limit.rlim_cur = config->cpu_limit_seconds;
        limit.rlim_max = config->cpu_limit_seconds;
        
        if (setrlimit(RLIMIT_CPU, &limit) == -1) {
            fprintf(stderr, "[ZenCube] Warning: Failed to set CPU limit: %s\n", strerror(errno));
        } else {
            log_message("CPU limit set to %d seconds", config->cpu_limit_seconds);
        }
    }
    
    /* Set memory limit */
    if (config->memory_limit_mb > 0) {
        limit.rlim_cur = (rlim_t)config->memory_limit_mb * 1024 * 1024;
        limit.rlim_max = (rlim_t)config->memory_limit_mb * 1024 * 1024;
        
        if (setrlimit(RLIMIT_AS, &limit) == -1) {
            fprintf(stderr, "[ZenCube] Warning: Failed to set memory limit: %s\n", strerror(errno));
        } else {
            log_message("Memory limit set to %d MB", config->memory_limit_mb);
        }
    }
}

/**
 * Parse command line arguments
 */
int parse_arguments(int argc, char *argv[], sandbox_config_t *config) {
    int opt;
    int option_index = 0;
    
    /* Initialize config with defaults */
    config->cpu_limit_seconds = 0;
    config->memory_limit_mb = 0;
    config->timeout_seconds = 0;
    config->json_output = 0;
    config->command_argv = NULL;
    
    static struct option long_options[] = {
        {"cpu",     required_argument, 0, 'c'},
        {"mem",     required_argument, 0, 'm'},
        {"timeout", required_argument, 0, 't'},
        {"json",    no_argument,       0, 'j'},
        {"help",    no_argument,       0, 'h'},
        {0, 0, 0, 0}
    };
    
    /* Parse options */
    while ((opt = getopt_long(argc, argv, "c:m:t:jh", long_options, &option_index)) != -1) {
        switch (opt) {
            case 'c':
                config->cpu_limit_seconds = atoi(optarg);
                if (config->cpu_limit_seconds < 0) {
                    fprintf(stderr, "Error: CPU limit must be non-negative\n");
                    return -1;
                }
                break;
            
            case 'm':
                config->memory_limit_mb = atoi(optarg);
                if (config->memory_limit_mb < 0) {
                    fprintf(stderr, "Error: Memory limit must be non-negative\n");
                    return -1;
                }
                break;
            
            case 't':
                config->timeout_seconds = atoi(optarg);
                if (config->timeout_seconds < 0) {
                    fprintf(stderr, "Error: Timeout must be non-negative\n");
                    return -1;
                }
                break;
            
            case 'j':
                config->json_output = 1;
                break;
            
            case 'h':
                print_usage(argv[0]);
                exit(EXIT_SUCCESS);
            
            default:
                print_usage(argv[0]);
                return -1;
        }
    }
    
    /* Check if command is provided */
    if (optind >= argc) {
        fprintf(stderr, "Error: No command specified\n\n");
        print_usage(argv[0]);
        return -1;
    }
    
    /* Store command and arguments */
    config->command_argv = &argv[optind];
    
    return 0;
}

/**
 * Calculate time difference in seconds
 */
double timespec_diff(struct timespec *start, struct timespec *end) {
    return (end->tv_sec - start->tv_sec) + (end->tv_nsec - start->tv_nsec) / 1000000000.0;
}

/**
 * Run the sandboxed command
 */
int run_sandbox(sandbox_config_t *config, sandbox_result_t *result) {
    pid_t child_pid;
    int status;
    struct timespec start_time, end_time;
    
    /* Initialize result structure */
    result->pid = 0;
    result->exit_code = -1;
    result->terminated_by_signal = 0;
    result->signal_number = 0;
    result->execution_time = 0.0;
    result->cpu_limit_exceeded = 0;
    result->memory_limit_exceeded = 0;
    result->timeout_exceeded = 0;
    
    /* Record start time */
    if (clock_gettime(CLOCK_MONOTONIC, &start_time) == -1) {
        if (!config->json_output) {
            log_message("Warning: Failed to get start time: %s", strerror(errno));
        }
    }
    
    /* Log command execution */
    if (!config->json_output) {
        printf("[ZenCube] Executing:");
        for (int i = 0; config->command_argv[i] != NULL; i++) {
            printf(" %s", config->command_argv[i]);
        }
        printf("\n");
    }
    
    /* Create child process */
    child_pid = fork();
    
    if (child_pid == -1) {
        fprintf(stderr, "[ZenCube] Error: Failed to fork: %s\n", strerror(errno));
        return -1;
    }
    
    if (child_pid == 0) {
        /* Child process - apply resource limits and execute command */
        apply_resource_limits(config);
        
        /* Execute command */
        execvp(config->command_argv[0], config->command_argv);
        
        /* If we reach here, execvp failed */
        fprintf(stderr, "[ZenCube] Error: Failed to execute '%s': %s\n", 
                config->command_argv[0], strerror(errno));
        exit(EXIT_FAILURE);
    }
    
    /* Parent process */
    result->pid = child_pid;
    
    if (!config->json_output) {
        log_message("Process started with PID: %d", child_pid);
    }
    
    /* Wait for child with timeout if specified */
    if (config->timeout_seconds > 0) {
        int timeout_count = 0;
        int wait_result;
        
        while (timeout_count < config->timeout_seconds) {
            wait_result = waitpid(child_pid, &status, WNOHANG);
            
            if (wait_result > 0) {
                /* Child has exited */
                break;
            } else if (wait_result == -1) {
                fprintf(stderr, "[ZenCube] Error: waitpid failed: %s\n", strerror(errno));
                return -1;
            }
            
            sleep(1);
            timeout_count++;
        }
        
        /* Check if timeout occurred */
        if (timeout_count >= config->timeout_seconds && wait_result == 0) {
            result->timeout_exceeded = 1;
            kill(child_pid, SIGKILL);
            waitpid(child_pid, &status, 0);
            
            if (!config->json_output) {
                log_message("Process killed due to timeout (%d seconds)", config->timeout_seconds);
            }
        }
    } else {
        /* No timeout - just wait */
        if (waitpid(child_pid, &status, 0) == -1) {
            fprintf(stderr, "[ZenCube] Error: waitpid failed: %s\n", strerror(errno));
            return -1;
        }
    }
    
    /* Record end time */
    if (clock_gettime(CLOCK_MONOTONIC, &end_time) == -1) {
        if (!config->json_output) {
            log_message("Warning: Failed to get end time: %s", strerror(errno));
        }
    } else {
        result->execution_time = timespec_diff(&start_time, &end_time);
    }
    
    /* Analyze exit status */
    if (WIFEXITED(status)) {
        result->exit_code = WEXITSTATUS(status);
        
        if (!config->json_output) {
            log_message("Process exited with code: %d", result->exit_code);
            log_message("Execution time: %.3f seconds", result->execution_time);
        }
    } else if (WIFSIGNALED(status)) {
        result->terminated_by_signal = 1;
        result->signal_number = WTERMSIG(status);
        
        /* Check if it was killed due to resource limits */
        if (result->signal_number == SIGXCPU) {
            result->cpu_limit_exceeded = 1;
        } else if (result->signal_number == SIGKILL && result->timeout_exceeded) {
            /* Already marked as timeout */
        }
        
        if (!config->json_output) {
            log_message("Process terminated by signal %d (%s)", 
                       result->signal_number, strsignal(result->signal_number));
            log_message("Execution time: %.3f seconds", result->execution_time);
        }
    }
    
    return 0;
}

/**
 * Main function
 */
int main(int argc, char *argv[]) {
    sandbox_config_t config;
    sandbox_result_t result;
    
    /* Parse command line arguments */
    if (parse_arguments(argc, argv, &config) != 0) {
        return EXIT_FAILURE;
    }
    
    /* Run the sandbox */
    if (run_sandbox(&config, &result) != 0) {
        return EXIT_FAILURE;
    }
    
    /* Output results */
    if (config.json_output) {
        log_json_result(&result, &config);
    }
    
    /* Return appropriate exit code */
    if (result.terminated_by_signal || result.exit_code != 0) {
        return EXIT_FAILURE;
    }
    
    return EXIT_SUCCESS;
}
