/**
 * Memory Hog Test Program
 * 
 * This program allocates increasing amounts of memory to test memory limits.
 * Should be killed when memory limit is exceeded.
 * 
 * Usage with sandbox:
 *   ./sandbox --mem=100 ./tests/memory_hog
 * 
 * Expected: Process killed when trying to allocate more than limit
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define CHUNK_SIZE_MB 10

int main(void) {
    size_t chunk_size = CHUNK_SIZE_MB * 1024 * 1024;  /* 10 MB chunks */
    size_t total_allocated = 0;
    int chunk_count = 0;
    char *ptr;
    
    printf("Starting memory allocation test...\n");
    printf("Will allocate memory in %d MB chunks\n", CHUNK_SIZE_MB);
    fflush(stdout);
    
    /* Keep allocating memory until we fail or are killed */
    while (1) {
        ptr = (char *)malloc(chunk_size);
        
        if (ptr == NULL) {
            printf("malloc() failed after allocating %zu MB\n", total_allocated / (1024 * 1024));
            printf("This is expected when memory limit is enforced\n");
            break;
        }
        
        /* Actually touch the memory to ensure it's allocated */
        memset(ptr, 0, chunk_size);
        
        chunk_count++;
        total_allocated += chunk_size;
        
        printf("Allocated chunk #%d (Total: %zu MB)\n", 
               chunk_count, total_allocated / (1024 * 1024));
        fflush(stdout);
        
        /* Small delay to make output readable */
        usleep(100000);  /* 0.1 seconds */
    }
    
    printf("Test completed. Total allocated: %zu MB\n", total_allocated / (1024 * 1024));
    return 0;
}
