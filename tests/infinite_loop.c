/**
 * Infinite Loop Test Program
 * 
 * This program runs an infinite loop to test CPU time limits.
 * Should be killed by SIGXCPU when CPU limit is exceeded.
 * 
 * Usage with sandbox:
 *   ./sandbox --cpu=5 ./tests/infinite_loop
 * 
 * Expected: Process terminated by SIGXCPU after ~5 seconds
 */

#include <stdio.h>
#include <unistd.h>

int main(void) {
    unsigned long long counter = 0;
    
    printf("Starting infinite loop (use Ctrl+C to stop manually)...\n");
    printf("This program is designed to test CPU time limits.\n");
    fflush(stdout);
    
    /* Infinite loop that consumes CPU time */
    while (1) {
        counter++;
        
        /* Print progress every billion iterations */
        if (counter % 1000000000 == 0) {
            printf("Still running... counter: %llu billion\n", counter / 1000000000);
            fflush(stdout);
        }
    }
    
    /* This should never be reached */
    return 0;
}
