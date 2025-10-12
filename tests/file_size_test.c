/**
 * File Size Test Program
 * 
 * This program writes large amounts of data to test file size limits.
 * Should receive SIGXFSZ when file size limit is exceeded.
 * 
 * Usage with sandbox:
 *   ./sandbox --fsize=50 ./tests/file_size_test
 * 
 * Expected: Process terminated by SIGXFSZ when file exceeds limit
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define CHUNK_SIZE_MB 10

int main(void) {
    FILE *fp;
    size_t chunk_size = CHUNK_SIZE_MB * 1024 * 1024;  /* 10 MB chunks */
    char *buffer;
    size_t total_written = 0;
    int chunk_count = 0;
    
    printf("Starting file size test...\n");
    printf("Will write data in %d MB chunks to test_output.dat\n", CHUNK_SIZE_MB);
    fflush(stdout);
    
    /* Allocate buffer */
    buffer = (char *)malloc(chunk_size);
    if (buffer == NULL) {
        fprintf(stderr, "Failed to allocate buffer\n");
        return 1;
    }
    
    /* Fill buffer with test data */
    memset(buffer, 'A', chunk_size);
    
    /* Open file for writing */
    fp = fopen("test_output.dat", "wb");
    if (fp == NULL) {
        fprintf(stderr, "Failed to open test_output.dat for writing\n");
        free(buffer);
        return 1;
    }
    
    /* Keep writing until we hit the limit or fail */
    while (1) {
        size_t written = fwrite(buffer, 1, chunk_size, fp);
        
        if (written < chunk_size) {
            printf("Write failed after %zu MB\n", total_written / (1024 * 1024));
            if (ferror(fp)) {
                printf("File error occurred (expected with file size limit)\n");
            }
            break;
        }
        
        chunk_count++;
        total_written += written;
        
        printf("Wrote chunk #%d (Total: %zu MB)\n", 
               chunk_count, total_written / (1024 * 1024));
        fflush(stdout);
        
        /* Force flush to disk */
        fflush(fp);
    }
    
    fclose(fp);
    free(buffer);
    
    printf("Test completed. Total written: %zu MB\n", total_written / (1024 * 1024));
    
    /* Clean up test file */
    remove("test_output.dat");
    
    return 0;
}
