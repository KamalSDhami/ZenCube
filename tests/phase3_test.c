/*
 * Phase 3 Integration Test Program
 * 
 * This program tests all Phase 3 features in the GUI:
 * 1. File Jail - Attempts file access outside jail
 * 2. Network Restrictions - Attempts network socket operations
 * 3. Monitoring & Metrics - Generates CPU and memory activity
 * 
 * Compile: gcc -o phase3_test phase3_test.c
 * Run in GUI: ./tests/phase3_test
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <errno.h>
#include <time.h>

#define TEST_DURATION_SEC 5
#define ALLOCATION_MB 10

void print_separator(const char *title) {
    printf("\n");
    printf("═══════════════════════════════════════════════════════\n");
    printf("  %s\n", title);
    printf("═══════════════════════════════════════════════════════\n");
}

void test_file_jail() {
    print_separator("TEST 1: File Jail (Filesystem Restrictions)");
    
    printf("Attempting to read files outside jail...\n\n");
    
    const char *test_files[] = {
        "/etc/passwd",           // System file
        "/home/secret.txt",      // User home file
        "../../../etc/hosts",    // Path traversal attempt
        NULL
    };
    
    for (int i = 0; test_files[i] != NULL; i++) {
        printf("  [%d] Trying to open: %s\n", i + 1, test_files[i]);
        
        int fd = open(test_files[i], O_RDONLY);
        if (fd >= 0) {
            printf("      ❌ VIOLATION: File opened successfully!\n");
            close(fd);
        } else {
            printf("      ✅ BLOCKED: %s\n", strerror(errno));
        }
    }
    
    printf("\n✅ File jail test completed\n");
}

void test_network_restrictions() {
    print_separator("TEST 2: Network Restrictions");
    
    printf("Attempting network socket operations...\n\n");
    
    // Test 1: Create TCP socket
    printf("  [1] Creating TCP socket...\n");
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock >= 0) {
        printf("      ❌ VIOLATION: Socket created (fd=%d)\n", sock);
        
        // Test 2: Attempt connection
        printf("  [2] Attempting to connect to 8.8.8.8:53...\n");
        struct sockaddr_in addr;
        memset(&addr, 0, sizeof(addr));
        addr.sin_family = AF_INET;
        addr.sin_port = htons(53);
        inet_pton(AF_INET, "8.8.8.8", &addr.sin_addr);
        
        int ret = connect(sock, (struct sockaddr*)&addr, sizeof(addr));
        if (ret == 0) {
            printf("      ❌ VIOLATION: Connection succeeded!\n");
        } else {
            printf("      ✅ BLOCKED: %s\n", strerror(errno));
        }
        
        close(sock);
    } else {
        printf("      ✅ BLOCKED: %s\n", strerror(errno));
    }
    
    // Test 3: Create UDP socket
    printf("  [3] Creating UDP socket...\n");
    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock >= 0) {
        printf("      ❌ VIOLATION: UDP socket created (fd=%d)\n", sock);
        close(sock);
    } else {
        printf("      ✅ BLOCKED: %s\n", strerror(errno));
    }
    
    printf("\n✅ Network restriction test completed\n");
}

void test_monitoring_metrics() {
    print_separator("TEST 3: Monitoring & Metrics (Resource Usage)");
    
    printf("Generating CPU and memory activity for %d seconds...\n", TEST_DURATION_SEC);
    printf("Watch the GUI graphs populate in real-time!\n\n");
    
    // Allocate memory
    size_t alloc_size = ALLOCATION_MB * 1024 * 1024;
    printf("  [1] Allocating %d MB of memory...\n", ALLOCATION_MB);
    char *buffer = (char*)malloc(alloc_size);
    if (buffer == NULL) {
        printf("      ❌ Memory allocation failed\n");
        return;
    }
    
    // Fill memory to ensure it's actually used
    printf("  [2] Writing to allocated memory...\n");
    for (size_t i = 0; i < alloc_size; i += 4096) {
        buffer[i] = (char)(i & 0xFF);
    }
    
    printf("  [3] Generating CPU load...\n");
    time_t start = time(NULL);
    unsigned long long counter = 0;
    double dummy = 0.0;
    
    while (time(NULL) - start < TEST_DURATION_SEC) {
        // CPU-intensive computation
        for (int i = 0; i < 100000; i++) {
            dummy += (double)i * 1.234567;
            counter++;
        }
        
        // Read from memory to keep it active
        for (size_t i = 0; i < alloc_size; i += 8192) {
            dummy += buffer[i];
        }
        
        // Progress indicator
        if (counter % 1000000 == 0) {
            int elapsed = (int)(time(NULL) - start);
            printf("      ⏱️  Elapsed: %d/%d seconds (iterations: %llu)\n", 
                   elapsed, TEST_DURATION_SEC, counter);
        }
    }
    
    printf("\n  [4] Cleaning up...\n");
    free(buffer);
    
    printf("\n✅ Monitoring test completed\n");
    printf("   Total iterations: %llu\n", counter);
    printf("   Check the GUI for:\n");
    printf("     - CPU graph showing usage spikes\n");
    printf("     - Memory graph showing %d+ MB allocation\n", ALLOCATION_MB);
    printf("     - Sample view with live updates\n");
    printf("     - Summary with peak CPU%% and memory\n");
}

void print_usage() {
    print_separator("Phase 3 Integration Test Suite");
    printf("\n");
    printf("This program validates all Phase 3 features:\n");
    printf("  1. File Jail - Filesystem access restrictions\n");
    printf("  2. Network Restrictions - Socket operation blocking\n");
    printf("  3. Monitoring & Metrics - Resource usage tracking\n");
    printf("\n");
    printf("HOW TO USE IN GUI:\n");
    printf("  1. Enable 'Enable monitoring for executions' checkbox\n");
    printf("  2. Set command: ./tests/phase3_test\n");
    printf("  3. (Optional) Enable File Jail with path: sandbox_jail\n");
    printf("  4. (Optional) Enable 'Disable Network Access'\n");
    printf("  5. Click 'Execute Command'\n");
    printf("  6. Watch the monitoring graphs populate!\n");
    printf("\n");
    printf("EXPECTED RESULTS:\n");
    printf("  ✅ File Jail: All file access attempts blocked\n");
    printf("  ✅ Network: All socket operations blocked\n");
    printf("  ✅ Monitoring: Graphs show CPU and memory usage\n");
    printf("  ✅ Log files created in monitor/logs/\n");
    printf("\n");
}

int main(int argc, char *argv[]) {
    print_usage();
    
    // Run all tests
    test_file_jail();
    sleep(1);
    
    test_network_restrictions();
    sleep(1);
    
    test_monitoring_metrics();
    
    print_separator("PHASE 3 TEST SUITE COMPLETE");
    printf("\n");
    printf("Check the GUI panels for results:\n");
    printf("  📊 Monitoring Dashboard: Should show graphs and samples\n");
    printf("  🗂️  File Jail Panel: Check status for violations\n");
    printf("  📡 Network Panel: Check status for blocking attempts\n");
    printf("\n");
    printf("Exit code: 0 (success)\n");
    printf("\n");
    
    return 0;
}
