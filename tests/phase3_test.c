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

#define TEST_DURATION_SEC 12
#define ALLOCATION_MB 15

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
    
    printf("Generating varied CPU and memory patterns for visualization...\n");
    printf("Watch the GUI graphs show different activity phases!\n\n");
    
    printf("  [1] Phase 1: Low CPU baseline (2 sec)...\n");
    time_t start = time(NULL);
    double dummy = 0.0;
    
    // Phase 1: Low CPU - baseline (2 seconds)
    while (time(NULL) - start < 2) {
        for (int i = 0; i < 1000; i++) {
            dummy += (double)i * 0.001;
        }
        usleep(50000); // Sleep 50ms to keep CPU low
    }
    
    printf("  [2] Phase 2: CPU spike - intensive computation (2 sec)...\n");
    start = time(NULL);
    // Phase 2: High CPU spike (2 seconds)
    while (time(NULL) - start < 2) {
        for (int i = 0; i < 1000000; i++) {
            dummy += (double)i * 1.234567;
            dummy = dummy * 0.9999;
        }
    }
    
    printf("  [3] Phase 3: Memory allocation ramp (3 sec)...\n");
    start = time(NULL);
    char *buffers[3];
    int phase = 0;
    
    // Phase 3: Progressive memory allocation (3 seconds)
    while (time(NULL) - start < 3) {
        int elapsed = (int)(time(NULL) - start);
        
        // Allocate more memory each second
        if (elapsed != phase && elapsed < 3) {
            phase = elapsed;
            size_t alloc_size = (phase + 1) * 5 * 1024 * 1024; // 5MB, 10MB, 15MB
            printf("      📈 Allocating %zu MB (total: %d MB)...\n", 
                   alloc_size / (1024 * 1024), 
                   (phase + 1) * 5);
            
            buffers[phase] = (char*)malloc(alloc_size);
            if (buffers[phase] != NULL) {
                // Write to memory to ensure it's counted
                for (size_t i = 0; i < alloc_size; i += 4096) {
                    buffers[phase][i] = (char)(i & 0xFF);
                }
            }
        }
        
        // Medium CPU activity
        for (int i = 0; i < 100000; i++) {
            dummy += (double)i * 0.5;
        }
        usleep(10000); // Small sleep
    }
    
    printf("  [4] Phase 4: CPU burst pattern (3 sec)...\n");
    start = time(NULL);
    // Phase 4: Alternating CPU bursts (3 seconds)
    while (time(NULL) - start < 3) {
        // High CPU burst
        for (int i = 0; i < 500000; i++) {
            dummy += (double)i * 2.5;
        }
        
        // Low CPU pause
        usleep(100000); // Sleep 100ms
        
        // Access memory to keep it active
        for (int p = 0; p < 3; p++) {
            if (buffers[p] != NULL) {
                for (size_t i = 0; i < 1024 * 1024; i += 8192) {
                    dummy += buffers[p][i];
                }
            }
        }
    }
    
    printf("  [5] Phase 5: Gradual ramp down (2 sec)...\n");
    start = time(NULL);
    // Phase 5: Gradual CPU decrease (2 seconds)
    int intensity = 1000000;
    while (time(NULL) - start < 2) {
        for (int i = 0; i < intensity; i++) {
            dummy += (double)i * 0.1;
        }
        intensity = intensity * 0.8; // Reduce intensity
        usleep(20000); // 20ms sleep
    }
    
    printf("\n  [6] Cleaning up...\n");
    // Free all allocated memory
    for (int i = 0; i < 3; i++) {
        if (buffers[i] != NULL) {
            free(buffers[i]);
        }
    }
    
    printf("\n✅ Monitoring test completed\n");
    printf("   Duration: 12 seconds (5 distinct phases)\n");
    printf("   Check the GUI for:\n");
    printf("     - CPU graph: Shows low baseline → spike → medium → bursts → ramp down\n");
    printf("     - Memory graph: Shows progressive allocation (5MB → 10MB → 15MB)\n");
    printf("     - Sample view: Live updates with varying CPU%% and RSS\n");
    printf("     - Summary: Peak values from each phase\n");
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
    printf("  2. Set command: ./tests/phase3_test (or full path)\n");
    printf("  3. (Optional) Enable File Jail with path: sandbox_jail\n");
    printf("  4. (Optional) Enable 'Disable Network Access'\n");
    printf("  5. Click 'Execute Command'\n");
    printf("  6. Watch the monitoring graphs for 12 seconds!\n");
    printf("\n");
    printf("EXPECTED RESULTS:\n");
    printf("  ✅ File Jail: All file access attempts blocked\n");
    printf("  ✅ Network: All socket operations blocked\n");
    printf("  ✅ Monitoring: Graphs show varied CPU and memory patterns\n");
    printf("     - Phase 1: Low CPU baseline\n");
    printf("     - Phase 2: High CPU spike\n");
    printf("     - Phase 3: Progressive memory allocation (5→15 MB)\n");
    printf("     - Phase 4: CPU burst pattern\n");
    printf("     - Phase 5: Gradual ramp down\n");
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
    printf("  📊 Monitoring Dashboard: Should show varied graph patterns\n");
    printf("     - CPU: Low baseline → spike → medium → bursts → ramp down\n");
    printf("     - Memory: Progressive increase from 5MB to 15MB\n");
    printf("     - ~12 samples collected over 12 seconds\n");
    printf("  🗂️  File Jail Panel: Check status for violations\n");
    printf("  📡 Network Panel: Check status for blocking attempts\n");
    printf("\n");
    printf("Exit code: 0 (success)\n");
    printf("\n");
    
    return 0;
}
