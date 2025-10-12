/**
 * Fork Bomb Test Program
 * 
 * This program attempts to create many child processes to test
 * process count limits (RLIMIT_NPROC).
 * 
 * WARNING: Without proper limits, this can freeze your system!
 * Always run with --procs limit in the sandbox.
 * 
 * Usage with sandbox:
 *   ./sandbox --procs=10 ./tests/fork_bomb
 * 
 * Expected: fork() should fail once process limit is reached
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <errno.h>
#include <string.h>

int main(void) {
    int fork_count = 0;
    pid_t pid;
    
    printf("Starting controlled fork test...\n");
    printf("⚠️  This tests process limits - DO NOT run without limits!\n");
    fflush(stdout);
    
    /* Attempt to fork multiple times */
    while (1) {
        pid = fork();
        
        if (pid < 0) {
            /* Fork failed - this is expected when limit is reached */
            printf("fork() failed after %d successful forks: %s\n", 
                   fork_count, strerror(errno));
            printf("This is expected behavior when process limit is enforced.\n");
            fflush(stdout);
            break;
        } else if (pid == 0) {
            /* Child process - just sleep and exit */
            sleep(2);
            exit(0);
        } else {
            /* Parent process */
            fork_count++;
            printf("Successfully created child process #%d (PID: %d)\n", fork_count, pid);
            fflush(stdout);
            
            /* Small delay to make output readable */
            usleep(100000);  /* 0.1 seconds */
        }
    }
    
    /* Wait for all children to complete */
    printf("Waiting for child processes to complete...\n");
    while (wait(NULL) > 0);
    
    printf("Fork test completed. Created %d child processes.\n", fork_count);
    return 0;
}
