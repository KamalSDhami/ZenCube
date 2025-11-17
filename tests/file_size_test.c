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
 * 
 * WARNING: This test creates large files! Always run with --fsize limit.
 *          The test file is cleaned up automatically.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>

#define CHUNK_SIZE_MB 1  /* Reduced from 10 to 1 MB for faster testing */

/* Global file pointer for cleanup in signal handler */
FILE *g_fp = NULL;

/* Signal handler for cleanup */
void cleanup_handler(int sig) {
    if (g_fp) {
        fclose(g_fp);
        g_fp = NULL;
    }
    remove("test_output.dat");
    _exit(0);
}

int main(void) {
    FILE *fp;
    size_t chunk_size = CHUNK_SIZE_MB * 1024 * 1024;  /* 1 MB chunks */
    char *buffer;
    size_t total_written = 0;
    int chunk_count = 0;
    
    /* Register signal handlers for cleanup */
    signal(SIGXFSZ, cleanup_handler);
    signal(SIGINT, cleanup_handler);
    signal(SIGTERM, cleanup_handler);
    
    printf("Starting file size test...\n");
    printf("Will write data in %d MB chunks to test_output.dat\n", CHUNK_SIZE_MB);
    printf("WARNING: Test file will be removed automatically\n");
    fflush(stdout);
    
    /* Allocate buffer */
    buffer = (char *)malloc(chunk_size);
    if (buffer == NULL) {
        fprintf(stderr, "Failed to allocate buffer\n");
        return 1;
    }
    
    /* Fill buffer with test data */
    memset(buffer, 'A', chunk_size);
    
    /* Remove any existing test file first */
    remove("test_output.dat");
    
    /* Open file for writing */
    fp = fopen("test_output.dat", "wb");
    g_fp = fp;  /* Store globally for signal handler */
    
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
