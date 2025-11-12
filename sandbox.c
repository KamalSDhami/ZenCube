#define _GNU_SOURCE
#define _POSIX_C_SOURCE 199309L

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <errno.h>
#include <string.h>
#include <time.h>
#include <stdarg.h>
#include <signal.h>
#include <limits.h>
#include <stddef.h>
#ifdef __linux__
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#endif

typedef struct {
    int cpu_seconds;
    long memory_mb;
    int max_processes;   
    long max_file_mb;    
} ResourceLimits;


void print_usage(const char *program_name);
void log_message(const char *format, ...);
void log_command(int argc, char *argv[], int start_index);
double timespec_diff(struct timespec *start, struct timespec *end);
int parse_arguments(int argc, char *argv[], ResourceLimits *limits, int *cmd_start_index,
                    int *jail_enabled, int *disable_network,
                    char *jail_path, size_t jail_path_size);
int apply_resource_limits(const ResourceLimits *limits);
void log_resource_limits(const ResourceLimits *limits);
int setup_chroot_jail(const char *jail_path);
int apply_network_seccomp(void);

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
    printf("  --jail=<path>        Request chroot jail at <path> (requires root)\n");
    printf("  --no-net             Disable network syscalls (seccomp)\n");
    printf("  --help               Display this help message\n");
    printf("\nExamples:\n");
    printf("  %s /bin/ls -l /\n", program_name);
    printf("  %s --cpu=5 /bin/sleep 10\n", program_name);
    printf("  %s --mem=256 --cpu=10 ./memory_test\n", program_name);
    printf("  %s --procs=5 --fsize=100 ./app\n", program_name);
    printf("  %s --jail=/opt/dev_jail --cpu=2 /bin/pwd\n", program_name);
    printf("\nResource Limit Signals:\n");
    printf("  SIGXCPU - CPU time limit exceeded\n");
    printf("  SIGKILL - Memory limit exceeded (kernel kill)\n");
}

void log_message(const char *format, ...) {
    va_list args;
    time_t raw_time;
    struct tm *time_info;
    char time_buffer[80];
    

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

void log_command(int argc, char *argv[], int start_index) {
    printf("[Sandbox] Starting command:");
    for (int i = start_index; i < argc; i++) {
        printf(" %s", argv[i]);
    }
    printf("\n");
    fflush(stdout);
}

double timespec_diff(struct timespec *start, struct timespec *end) {
    return (end->tv_sec - start->tv_sec) + (end->tv_nsec - start->tv_nsec) / 1000000000.0;
}

int parse_arguments(int argc, char *argv[], ResourceLimits *limits, int *cmd_start_index,
                    int *jail_enabled, int *disable_network,
                    char *jail_path, size_t jail_path_size) {
    int i = 1;
    

    limits->cpu_seconds = 0;
    limits->memory_mb = 0;
    limits->max_processes = 0;
    limits->max_file_mb = 0;
    if (jail_enabled != NULL) {
        *jail_enabled = 0;
    }
    if (disable_network != NULL) {
        *disable_network = 0;
    }
    if (jail_path != NULL && jail_path_size > 0) {
        jail_path[0] = '\0';
    }
    

    while (i < argc && argv[i][0] == '-') {
        if (strcmp(argv[i], "--") == 0) {
            i++;
            break;
        }
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
        } else if (strncmp(argv[i], "--jail=", 7) == 0) {
            const char *path_arg = argv[i] + 7;
            size_t path_len = strlen(path_arg);
            if (path_len == 0) {
                fprintf(stderr, "Error: --jail requires a non-empty path\n");
                return -1;
            }
            if (jail_path == NULL || jail_path_size == 0 || jail_enabled == NULL) {
                fprintf(stderr, "Error: Jail support is not properly configured\n");
                return -1;
            }
            if (path_len >= jail_path_size) {
                fprintf(stderr, "Error: Jail path is too long\n");
                return -1;
            }
            strncpy(jail_path, path_arg, jail_path_size - 1);
            jail_path[jail_path_size - 1] = '\0';
            *jail_enabled = 1;
        } else if (strcmp(argv[i], "--no-net") == 0) {
            if (disable_network == NULL) {
                fprintf(stderr, "Error: Network flag unsupported in this build\n");
                return -1;
            }
            *disable_network = 1;
        } else {
            fprintf(stderr, "Error: Unknown option: %s\n", argv[i]);
            return -1;
        }
        i++;
    }
    
    *cmd_start_index = i;
    return 0;
}

int apply_resource_limits(const ResourceLimits *limits) {
    struct rlimit rlim;
    

    if (limits->cpu_seconds > 0) {
        rlim.rlim_cur = limits->cpu_seconds;
        rlim.rlim_max = limits->cpu_seconds;
        if (setrlimit(RLIMIT_CPU, &rlim) != 0) {
            fprintf(stderr, "[Sandbox] Error: Failed to set CPU limit: %s\n", strerror(errno));
            return -1;
        }
        log_message("CPU limit set to %d seconds", limits->cpu_seconds);
    }
    

    if (limits->memory_mb > 0) {
        rlim.rlim_cur = (rlim_t)limits->memory_mb * 1024 * 1024;
        rlim.rlim_max = (rlim_t)limits->memory_mb * 1024 * 1024;
        if (setrlimit(RLIMIT_AS, &rlim) != 0) {
            fprintf(stderr, "[Sandbox] Error: Failed to set memory limit: %s\n", strerror(errno));
            return -1;
        }
        log_message("Memory limit set to %ld MB", limits->memory_mb);
    }
    

    if (limits->max_processes > 0) {
        rlim.rlim_cur = limits->max_processes;
        rlim.rlim_max = limits->max_processes;
        if (setrlimit(RLIMIT_NPROC, &rlim) != 0) {
            fprintf(stderr, "[Sandbox] Error: Failed to set process limit: %s\n", strerror(errno));
            return -1;
        }
        log_message("Process limit set to %d", limits->max_processes);
    }
    

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

int setup_chroot_jail(const char *jail_path) {
    if (chdir(jail_path) != 0) {
        fprintf(stderr, "[Sandbox] Child Error: Failed to change directory to '%s': %s\n",
                jail_path, strerror(errno));
        return -1;
    }
    if (chroot(".") != 0) {
        fprintf(stderr, "[Sandbox] Child Error: Failed to chroot to '%s': %s\n",
                jail_path, strerror(errno));
        return -1;
    }
    if (chdir("/") != 0) {
        fprintf(stderr, "[Sandbox] Child Error: Failed to change to new root '/': %s\n",
                strerror(errno));
        return -1;
    }
    log_message("Chroot jail activated at %s", jail_path);
    return 0;
}

int apply_network_seccomp(void) {
#ifdef __linux__
#ifndef SECCOMP_RET_ERRNO
#define SECCOMP_RET_ERRNO 0x00050000U
#endif
#define ZC_DENY_SYSCALL(name) \
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_##name, 0, 1), \
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & 0xFFF))

    static const struct sock_filter filter_program[] = {
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),
        ZC_DENY_SYSCALL(socket),
        ZC_DENY_SYSCALL(connect),
        ZC_DENY_SYSCALL(sendto),
        ZC_DENY_SYSCALL(sendmsg),
        ZC_DENY_SYSCALL(recvfrom),
        ZC_DENY_SYSCALL(recvmsg),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    };

    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter_program) / sizeof(filter_program[0])),
        .filter = (struct sock_filter *)filter_program,
    };

    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
        return -1;
    }

    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog) != 0) {
        return -1;
    }

#undef ZC_DENY_SYSCALL
    return 0;
#else
    errno = ENOSYS;
    return -1;
#endif
}

int main(int argc, char *argv[]) {
    pid_t child_pid;
    int status;
    struct timespec start_time, end_time;
    double execution_time;
    ResourceLimits limits;
    int cmd_start_index;
    int jail_enabled = 0;
    int disable_network = 0;
    char jail_path[PATH_MAX];
    

    if (parse_arguments(argc, argv, &limits, &cmd_start_index,
                        &jail_enabled, &disable_network,
                        jail_path, sizeof(jail_path)) != 0) {
        fprintf(stderr, "\n");
        print_usage(argv[0]);
        return EXIT_FAILURE;
    }
    

    if (cmd_start_index >= argc) {
        fprintf(stderr, "Error: No command specified\n\n");
        print_usage(argv[0]);
        return EXIT_FAILURE;
    }
    

    log_resource_limits(&limits);
    if (disable_network) {
        log_message("Network restriction requested (--no-net)");
    }
    if (jail_enabled) {
        char resolved_path[PATH_MAX];
        struct stat jail_stat;
        if (realpath(jail_path, resolved_path) == NULL) {
            fprintf(stderr, "[Sandbox] Error: Unable to resolve jail path '%s': %s\n",
                    jail_path, strerror(errno));
            return EXIT_FAILURE;
        }
        strncpy(jail_path, resolved_path, sizeof(jail_path) - 1);
        jail_path[sizeof(jail_path) - 1] = '\0';
        if (stat(jail_path, &jail_stat) != 0) {
            fprintf(stderr, "[Sandbox] Error: Cannot stat jail path '%s': %s\n",
                    jail_path, strerror(errno));
            return EXIT_FAILURE;
        }
        if (!S_ISDIR(jail_stat.st_mode)) {
            fprintf(stderr, "[Sandbox] Error: Jail path '%s' is not a directory\n", jail_path);
            return EXIT_FAILURE;
        }
        if (access(jail_path, X_OK) != 0) {
            fprintf(stderr, "[Sandbox] Error: Jail path '%s' is not accessible: %s\n",
                    jail_path, strerror(errno));
            return EXIT_FAILURE;
        }
        log_message("Jail requested at %s", jail_path);
    }
    

    log_command(argc, argv, cmd_start_index);
    

    if (clock_gettime(CLOCK_MONOTONIC, &start_time) == -1) {
        log_message("Warning: Failed to get start time: %s", strerror(errno));
    }
    

    child_pid = fork();
    
    if (child_pid == -1) {

        fprintf(stderr, "[Sandbox] Error: Failed to create child process: %s\n", 
                strerror(errno));
        return EXIT_FAILURE;
    }
    
    if (child_pid == 0) {
        
        log_message("Child process created (PID: %d)", getpid());
        
        
        if (apply_resource_limits(&limits) != 0) {
            fprintf(stderr, "[Sandbox] Child Error: Failed to apply resource limits\n");
            exit(EXIT_FAILURE);
        }
        
        
        
        if (disable_network) {
            if (apply_network_seccomp() == 0) {
                log_message("Seccomp network filter installed");
            } else {
                int saved_errno = errno;
                log_message("Warning: Unable to install network filter (errno=%d: %s)",
                            saved_errno, strerror(saved_errno));
                log_message("Proceeding without kernel-level network restriction."
                            " Use monitor/net_wrapper.py in dev-safe mode.");
            }
        }

        if (execvp(argv[cmd_start_index], &argv[cmd_start_index]) == -1) {
        
            fprintf(stderr, "[Sandbox] Child Error: Failed to execute '%s': %s\n", 
                    argv[cmd_start_index], strerror(errno));
            exit(EXIT_FAILURE);
        }
        
        
        exit(EXIT_FAILURE);
    } else {
        
        log_message("Child PID: %d", child_pid);
        
        
        pid_t wait_result = waitpid(child_pid, &status, 0);
        
        
        if (clock_gettime(CLOCK_MONOTONIC, &end_time) == -1) {
            log_message("Warning: Failed to get end time: %s", strerror(errno));
            execution_time = -1.0;  
        } else {
            execution_time = timespec_diff(&start_time, &end_time);
        }
        
        if (wait_result == -1) {
            fprintf(stderr, "[Sandbox] Error: waitpid() failed: %s\n", strerror(errno));
            return EXIT_FAILURE;
        }
        
        
        if (WIFEXITED(status)) {
            
            int exit_code = WEXITSTATUS(status);
            log_message("Process exited normally with status %d", exit_code);
            
            if (execution_time >= 0) {
                log_message("Execution time: %.3f seconds", execution_time);
            }
            
            
            return exit_code;
        } else if (WIFSIGNALED(status)) {
            
            int signal_num = WTERMSIG(status);
            log_message("Process terminated by signal %d (%s)", 
                       signal_num, strsignal(signal_num));
            
            
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
            
            
            if (WCOREDUMP(status)) {
                log_message("Core dump was created");
            }
            
            return EXIT_FAILURE;
        } else if (WIFSTOPPED(status)) {
            
            int stop_signal = WSTOPSIG(status);
            log_message("Process stopped by signal %d", stop_signal);
            return EXIT_FAILURE;
        } else {
            
            log_message("Process ended with unknown status: %d", status);
            return EXIT_FAILURE;
        }
    }
    
    return EXIT_SUCCESS;
}