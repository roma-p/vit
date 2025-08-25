package db

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"testing"
	"time"

	"vit/internal/testutils"
)

func TestJSONManager_LocalLockingMechanism(t *testing.T) {
	tempDir := t.TempDir()
	filename := filepath.Join(tempDir, "lock_test.json")
	
	t.Run("BasicLockAcquisition", func(t *testing.T) {
		manager := NewJSONManager(filename, nil)
		defer manager.Close()
		
		lockfile := filename + ".lock"
		
		// Acquire lock
		err := manager.acquireLocalLock(lockfile)
		testutils.AssertNoError(t, err)
		
		// Verify lock file exists
		testutils.AssertExists(t, lockfile)
		
		// Try to acquire again - should fail
		err = manager.acquireLocalLock(lockfile)
		testutils.AssertError(t, err)
		
		// Clean up
		os.Remove(lockfile)
	})
	
	t.Run("LockContentValidation", func(t *testing.T) {
		manager := NewJSONManager(filename, nil)
		defer manager.Close()
		
		lockfile := filename + ".lock"
		
		err := manager.acquireLocalLock(lockfile)
		if err != nil {
			t.Fatalf("Failed to acquire lock: %v", err)
		}
		defer os.Remove(lockfile)
		
		// Read lock file content
		content, err := os.ReadFile(lockfile)
		if err != nil {
			t.Fatalf("Failed to read lock file: %v", err)
		}
		
		contentStr := string(content)
		testutils.AssertTrue(t, len(contentStr) > 0)
		// Basic checks for lock file content format
		// Note: We could add more specific assertions here if needed
	})
	
	t.Run("OrphanedLockCleanup", func(t *testing.T) {
		manager := NewJSONManager(filename, nil)
		manager.timeout = 100 * time.Millisecond // Short timeout for testing
		defer manager.Close()
		
		lockfile := filename + ".lock"
		
		// Create an old lock file
		err := os.WriteFile(lockfile, []byte("old lock"), 0666)
		if err != nil {
			t.Fatalf("Failed to create old lock file: %v", err)
		}
		
		// Make it appear old
		oldTime := time.Now().Add(-200 * time.Millisecond)
		err = os.Chtimes(lockfile, oldTime, oldTime)
		if err != nil {
			t.Fatalf("Failed to set old time: %v", err)
		}
		
		// Try to clean orphaned lock
		manager.cleanOrphanedLocalLock(lockfile)
		
		// Verify lock was removed
		if _, err := os.Stat(lockfile); !os.IsNotExist(err) {
			t.Error("Orphaned lock file should be removed")
		}
	})
	
	t.Run("RecentLockNotCleaned", func(t *testing.T) {
		manager := NewJSONManager(filename, nil)
		manager.timeout = 1 * time.Second
		defer manager.Close()
		
		lockfile := filename + ".lock"
		
		// Create a recent lock file
		err := os.WriteFile(lockfile, []byte("recent lock"), 0666)
		if err != nil {
			t.Fatalf("Failed to create recent lock file: %v", err)
		}
		defer os.Remove(lockfile)
		
		// Try to clean - should not be removed
		manager.cleanOrphanedLocalLock(lockfile)
		
		// Verify lock still exists
		if _, err := os.Stat(lockfile); os.IsNotExist(err) {
			t.Error("Recent lock file should not be removed")
		}
	})
}

func TestJSONManager_ConcurrentLocking(t *testing.T) {
	tempDir := t.TempDir()
	filename := filepath.Join(tempDir, "concurrent_lock_test.json")
	
	t.Run("SerializedAccess", func(t *testing.T) {
		const numGoroutines = 10
		const operationsPerGoroutine = 5
		
		manager := NewJSONManager(filename, nil)
		defer manager.Close()
		
		var wg sync.WaitGroup
		var mu sync.Mutex
		accessOrder := make([]int, 0)
		errors := make(chan error, numGoroutines*operationsPerGoroutine)
		
		for i := 0; i < numGoroutines; i++ {
			wg.Add(1)
			go func(goroutineID int) {
				defer wg.Done()
				
				for j := 0; j < operationsPerGoroutine; j++ {
					ctx := context.Background()
					testData := TestData{
						ID:    goroutineID*1000 + j,
						Name:  fmt.Sprintf("goroutine_%d_op_%d", goroutineID, j),
						Value: goroutineID*100 + j,
					}
					
					err := manager.WriteJSON(ctx, testData)
					if err != nil {
						errors <- err
						return
					}
					
					// Record access order
					mu.Lock()
					accessOrder = append(accessOrder, goroutineID*1000+j)
					mu.Unlock()
					
					// Small delay to increase chance of contention
					time.Sleep(1 * time.Millisecond)
				}
			}(i)
		}
		
		wg.Wait()
		close(errors)
		
		// Check for errors
		for err := range errors {
			t.Errorf("Concurrent operation failed: %v", err)
		}
		
		// Verify all operations completed
		expectedOps := numGoroutines * operationsPerGoroutine
		if len(accessOrder) != expectedOps {
			t.Errorf("Expected %d operations, got %d", expectedOps, len(accessOrder))
		}
		
		// Verify final file exists and is readable
		var finalData TestData
		err := manager.ReadJSON(context.Background(), &finalData)
		if err != nil {
			t.Fatalf("Failed to read final data: %v", err)
		}
	})
	
	t.Run("ReadWriteConcurrency", func(t *testing.T) {
		manager := NewJSONManager(filename, nil)
		defer manager.Close()
		
		ctx := context.Background()
		
		// Write initial data
		initialData := TestData{ID: 0, Name: "initial", Value: 0}
		err := manager.WriteJSON(ctx, initialData)
		if err != nil {
			t.Fatalf("Failed to write initial data: %v", err)
		}
		
		const numReaders = 5
		const numWriters = 3
		const duration = 100 * time.Millisecond
		
		var wg sync.WaitGroup
		errors := make(chan error, numReaders+numWriters)
		
		// Start readers
		for i := 0; i < numReaders; i++ {
			wg.Add(1)
			go func(readerID int) {
				defer wg.Done()
				
				start := time.Now()
				for time.Since(start) < duration {
					var data TestData
					err := manager.ReadJSON(ctx, &data)
					if err != nil {
						errors <- fmt.Errorf("reader %d: %v", readerID, err)
						return
					}
					time.Sleep(5 * time.Millisecond)
				}
			}(i)
		}
		
		// Start writers
		for i := 0; i < numWriters; i++ {
			wg.Add(1)
			go func(writerID int) {
				defer wg.Done()
				
				start := time.Now()
				opCount := 0
				for time.Since(start) < duration {
					testData := TestData{
						ID:    writerID*1000 + opCount,
						Name:  fmt.Sprintf("writer_%d_op_%d", writerID, opCount),
						Value: writerID*100 + opCount,
					}
					
					err := manager.WriteJSON(ctx, testData)
					if err != nil {
						errors <- fmt.Errorf("writer %d: %v", writerID, err)
						return
					}
					
					opCount++
					time.Sleep(10 * time.Millisecond)
				}
			}(i)
		}
		
		wg.Wait()
		close(errors)
		
		// Check for errors
		for err := range errors {
			t.Errorf("Concurrent read/write error: %v", err)
		}
	})
}

func TestJSONManager_LockTimeout(t *testing.T) {
	tempDir := t.TempDir()
	filename := filepath.Join(tempDir, "timeout_test.json")
	
	t.Run("TimeoutWithHeldLock", func(t *testing.T) {
		manager := NewJSONManager(filename, nil)
		manager.timeout = 50 * time.Millisecond
		manager.retryDelay = 10 * time.Millisecond
		defer manager.Close()
		
		lockfile := filename + ".lock"
		
		// Create and hold a lock
		err := os.WriteFile(lockfile, []byte("held lock"), 0666)
		if err != nil {
			t.Fatalf("Failed to create held lock: %v", err)
		}
		defer os.Remove(lockfile)
		
		// Try to write - should timeout
		ctx := context.Background()
		testData := TestData{ID: 1, Name: "test", Value: 42}
		
		start := time.Now()
		err = manager.WriteJSON(ctx, testData)
		elapsed := time.Since(start)
		
		if err == nil {
			t.Error("Expected timeout error")
		}
		
		// Should timeout after approximately the configured timeout
		if elapsed < manager.timeout {
			t.Errorf("Timeout too short: %v < %v", elapsed, manager.timeout)
		}
		
		// But not too much longer (allow some overhead)
		maxTimeout := manager.timeout + 50*time.Millisecond
		if elapsed > maxTimeout {
			t.Errorf("Timeout too long: %v > %v", elapsed, maxTimeout)
		}
	})
	
	t.Run("ContextTimeout", func(t *testing.T) {
		manager := NewJSONManager(filename, nil)
		defer manager.Close()
		
		// Create context with very short timeout
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Millisecond)
		defer cancel()
		
		// Hold a lock to force timeout
		lockfile := filename + ".lock"
		err := os.WriteFile(lockfile, []byte("context test lock"), 0666)
		if err != nil {
			t.Fatalf("Failed to create lock: %v", err)
		}
		defer os.Remove(lockfile)
		
		testData := TestData{ID: 1, Name: "test", Value: 42}
		
		start := time.Now()
		err = manager.WriteJSON(ctx, testData)
		elapsed := time.Since(start)
		
		if err == nil {
			t.Error("Expected context timeout error")
		}
		
		// Should respect context timeout
		if elapsed > 50*time.Millisecond {
			t.Errorf("Context timeout not respected: %v", elapsed)
		}
	})
}

func TestJSONManager_LockRetryMechanism(t *testing.T) {
	tempDir := t.TempDir()
	filename := filepath.Join(tempDir, "retry_test.json")
	
	t.Run("SuccessfulRetryAfterLockRelease", func(t *testing.T) {
		manager := NewJSONManager(filename, nil)
		manager.retryDelay = 10 * time.Millisecond
		defer manager.Close()
		
		lockfile := filename + ".lock"
		
		// Create initial lock
		err := os.WriteFile(lockfile, []byte("initial lock"), 0666)
		if err != nil {
			t.Fatalf("Failed to create initial lock: %v", err)
		}
		
		// Start goroutine to remove lock after delay
		go func() {
			time.Sleep(30 * time.Millisecond)
			os.Remove(lockfile)
		}()
		
		// Try to write - should succeed after retry
		ctx := context.Background()
		testData := TestData{ID: 1, Name: "retry_test", Value: 42}
		
		start := time.Now()
		err = manager.WriteJSON(ctx, testData)
		elapsed := time.Since(start)
		
		if err != nil {
			t.Fatalf("Write should succeed after lock release: %v", err)
		}
		
		// Should take some time (at least the delay)
		if elapsed < 20*time.Millisecond {
			t.Errorf("Operation completed too quickly: %v", elapsed)
		}
		
		// Verify data was written
		var readData TestData
		err = manager.ReadJSON(ctx, &readData)
		if err != nil {
			t.Fatalf("Failed to read data: %v", err)
		}
		
		if readData.ID != testData.ID {
			t.Error("Data not written correctly after retry")
		}
	})
	
	t.Run("RetryAttemptCounting", func(t *testing.T) {
		manager := NewJSONManager(filename, nil)
		manager.timeout = 100 * time.Millisecond
		manager.retryDelay = 10 * time.Millisecond
		defer manager.Close()
		
		lockfile := filename + ".lock"
		
		// Hold lock throughout test
		err := os.WriteFile(lockfile, []byte("persistent lock"), 0666)
		if err != nil {
			t.Fatalf("Failed to create persistent lock: %v", err)
		}
		defer os.Remove(lockfile)
		
		ctx := context.Background()
		testData := TestData{ID: 1, Name: "count_test", Value: 42}
		
		start := time.Now()
		err = manager.WriteJSON(ctx, testData)
		elapsed := time.Since(start)
		
		if err == nil {
			t.Error("Expected timeout error")
		}
		
		// Calculate expected retry attempts
		expectedRetries := int(manager.timeout / manager.retryDelay)
		actualDuration := elapsed
		actualRetries := int(actualDuration / manager.retryDelay)
		
		// Should be within reasonable range
		if actualRetries < expectedRetries-2 || actualRetries > expectedRetries+2 {
			t.Errorf("Unexpected retry count: got ~%d, expected ~%d", actualRetries, expectedRetries)
		}
	})
}

func TestJSONManager_LockFilePermissions(t *testing.T) {
	tempDir := t.TempDir()
	filename := filepath.Join(tempDir, "perm_test.json")
	
	t.Run("LockFilePermissions", func(t *testing.T) {
		manager := NewJSONManager(filename, nil)
		defer manager.Close()
		
		lockfile := filename + ".lock"
		
		err := manager.acquireLocalLock(lockfile)
		if err != nil {
			t.Fatalf("Failed to acquire lock: %v", err)
		}
		defer os.Remove(lockfile)
		
		// Check lock file permissions (account for umask)
		info, err := os.Stat(lockfile)
		if err != nil {
			t.Fatalf("Failed to stat lock file: %v", err)
		}
		
		// Lock file should be readable by owner at minimum
		perms := info.Mode().Perm()
		if perms&0400 == 0 {
			t.Error("Lock file should be readable by owner")
		}
		
		// Should not be executable
		if perms&0111 != 0 {
			t.Error("Lock file should not be executable")
		}
	})
}

func TestJSONManager_EdgeCaseLocking(t *testing.T) {
	tempDir := t.TempDir()
	filename := filepath.Join(tempDir, "edge_test.json")
	
	t.Run("EmptyLockFile", func(t *testing.T) {
		manager := NewJSONManager(filename, nil)
		defer manager.Close()
		
		lockfile := filename + ".lock"
		
		// Create empty lock file
		file, err := os.Create(lockfile)
		if err != nil {
			t.Fatalf("Failed to create empty lock file: %v", err)
		}
		file.Close()
		defer os.Remove(lockfile)
		
		// Should not be able to acquire lock
		err = manager.acquireLocalLock(lockfile)
		if err == nil {
			t.Error("Should not acquire lock when file exists")
		}
	})
	
	t.Run("LockFileRemovedDuringOperation", func(t *testing.T) {
		manager := NewJSONManager(filename, nil)
		defer manager.Close()
		
		ctx := context.Background()
		
		// Start write operation
		var wg sync.WaitGroup
		var writeErr error
		
		wg.Add(1)
		go func() {
			defer wg.Done()
			testData := TestData{ID: 1, Name: "test", Value: 42}
			writeErr = manager.WriteJSON(ctx, testData)
		}()
		
		// Small delay to let write operation start
		time.Sleep(5 * time.Millisecond)
		
		// Remove lock file if it exists (simulating external interference)
		lockfile := filename + ".lock"
		os.Remove(lockfile) // Ignore error if doesn't exist
		
		wg.Wait()
		
		// Write should still succeed (it creates the lock)
		if writeErr != nil {
			t.Fatalf("Write should succeed even if lock is removed: %v", writeErr)
		}
	})
}

