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

type TestData struct {
	ID      int    `json:"id"`
	Name    string `json:"name"`
	Value   int    `json:"value"`
	Nested  struct {
		Field string `json:"field"`
	} `json:"nested"`
}

func TestJSONManager_LocalOperations(t *testing.T) {
	tempDir := t.TempDir()
	filename := filepath.Join(tempDir, "test.json")
	
	manager := NewJSONManager(filename, nil)
	defer manager.Close()
	
	ctx := context.Background()
	
	t.Run("WriteAndRead", func(t *testing.T) {
		testData := TestData{
			ID:   1,
			Name: "test",
			Value: 42,
		}
		testData.Nested.Field = "nested_value"
		
		// Write data
		err := manager.WriteJSON(ctx, testData)
		testutils.AssertNoError(t, err)
		
		// Read data back
		var readData TestData
		err = manager.ReadJSON(ctx, &readData)
		testutils.AssertNoError(t, err)
		
		// Verify data
		testutils.AssertEqual(t, testData.ID, readData.ID)
		testutils.AssertEqual(t, testData.Name, readData.Name)
		testutils.AssertEqual(t, testData.Value, readData.Value)
		testutils.AssertEqual(t, testData.Nested.Field, readData.Nested.Field)
	})
	
	t.Run("Exists", func(t *testing.T) {
		exists, err := manager.Exists()
		testutils.AssertNoError(t, err)
		testutils.AssertTrue(t, exists)
		
		// Test non-existent file
		nonExistentManager := NewJSONManager(filepath.Join(tempDir, "nonexistent.json"), nil)
		exists, err = nonExistentManager.Exists()
		testutils.AssertNoError(t, err)
		testutils.AssertFalse(t, exists)
	})
	
	t.Run("ReadNonExistentFile", func(t *testing.T) {
		nonExistentManager := NewJSONManager(filepath.Join(tempDir, "missing.json"), nil)
		var data TestData
		err := nonExistentManager.ReadJSON(ctx, &data)
		testutils.AssertError(t, err)
	})
}

func TestJSONManager_ConcurrentAccess(t *testing.T) {
	tempDir := t.TempDir()
	filename := filepath.Join(tempDir, "concurrent_test.json")
	
	manager := NewJSONManager(filename, nil)
	defer manager.Close()
	
	ctx := context.Background()
	
	t.Run("ConcurrentWrites", func(t *testing.T) {
		const numGoroutines = 10
		var wg sync.WaitGroup
		errors := make(chan error, numGoroutines)
		
		for i := 0; i < numGoroutines; i++ {
			wg.Add(1)
			go func(id int) {
				defer wg.Done()
				
				testData := TestData{
					ID:    id,
					Name:  fmt.Sprintf("test_%d", id),
					Value: id * 10,
				}
				
				err := manager.WriteJSON(ctx, testData)
				if err != nil {
					errors <- err
				}
			}(i)
		}
		
		wg.Wait()
		close(errors)
		
		// Check for errors
		for err := range errors {
			testutils.AssertNoError(t, err)
		}
		
		// Verify final state
		var finalData TestData
		err := manager.ReadJSON(ctx, &finalData)
		testutils.AssertNoError(t, err)
		
		// Should have data from one of the writes
		testutils.AssertTrue(t, finalData.ID >= 0 && finalData.ID < numGoroutines)
	})
	
	t.Run("ConcurrentReadsAndWrites", func(t *testing.T) {
		const numReaders = 5
		const numWriters = 3
		var wg sync.WaitGroup
		errors := make(chan error, numReaders+numWriters)
		
		// Start writers
		for i := 0; i < numWriters; i++ {
			wg.Add(1)
			go func(id int) {
				defer wg.Done()
				
				for j := 0; j < 5; j++ {
					testData := TestData{
						ID:    id*100 + j,
						Name:  fmt.Sprintf("writer_%d_iteration_%d", id, j),
						Value: (id*100 + j) * 10,
					}
					
					err := manager.WriteJSON(ctx, testData)
					if err != nil {
						errors <- err
						return
					}
					
					time.Sleep(10 * time.Millisecond)
				}
			}(i)
		}
		
		// Start readers
		for i := 0; i < numReaders; i++ {
			wg.Add(1)
			go func(id int) {
				defer wg.Done()
				
				for j := 0; j < 10; j++ {
					var data TestData
					err := manager.ReadJSON(ctx, &data)
					if err != nil && !os.IsNotExist(err) {
						errors <- err
						return
					}
					
					time.Sleep(5 * time.Millisecond)
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

func TestJSONManager_AtomicOperations(t *testing.T) {
	tempDir := t.TempDir()
	filename := filepath.Join(tempDir, "atomic_test.json")
	
	manager := NewJSONManager(filename, nil)
	defer manager.Close()
	
	ctx := context.Background()
	
	t.Run("WriteIsAtomic", func(t *testing.T) {
		// Write initial data
		initialData := TestData{ID: 1, Name: "initial", Value: 100}
		err := manager.WriteJSON(ctx, initialData)
		if err != nil {
			t.Fatalf("Failed to write initial data: %v", err)
		}
		
		// Verify temp file is cleaned up
		tempFile := filename + ".tmp"
		if _, err := os.Stat(tempFile); !os.IsNotExist(err) {
			t.Error("Temp file should not exist after write")
		}
		
		// Write new data
		newData := TestData{ID: 2, Name: "updated", Value: 200}
		err = manager.WriteJSON(ctx, newData)
		if err != nil {
			t.Fatalf("Failed to write new data: %v", err)
		}
		
		// Read and verify
		var readData TestData
		err = manager.ReadJSON(ctx, &readData)
		if err != nil {
			t.Fatalf("Failed to read data: %v", err)
		}
		
		if readData.ID != newData.ID || readData.Name != newData.Name || readData.Value != newData.Value {
			t.Error("Data was not atomically updated")
		}
	})
}


func TestJSONManager_OrphanedLockCleanup(t *testing.T) {
	tempDir := t.TempDir()
	filename := filepath.Join(tempDir, "orphan_test.json")
	
	manager := NewJSONManager(filename, nil)
	defer manager.Close()
	
	ctx := context.Background()
	
	t.Run("OrphanedLockIsRemoved", func(t *testing.T) {
		// Create an old lock file
		lockFile := filename + ".lock"
		file, err := os.Create(lockFile)
		if err != nil {
			t.Fatalf("Failed to create lock file: %v", err)
		}
		file.Close()
		
		// Make it look old
		oldTime := time.Now().Add(-20 * time.Second)
		err = os.Chtimes(lockFile, oldTime, oldTime)
		if err != nil {
			t.Fatalf("Failed to change lock file time: %v", err)
		}
		
		// Write should succeed (after cleaning orphaned lock)
		testData := TestData{ID: 1, Name: "test", Value: 42}
		err = manager.WriteJSON(ctx, testData)
		if err != nil {
			t.Fatalf("Write should succeed after cleaning orphaned lock: %v", err)
		}
		
		// Verify data was written
		var readData TestData
		err = manager.ReadJSON(ctx, &readData)
		if err != nil {
			t.Fatalf("Failed to read data: %v", err)
		}
		
		if readData.ID != testData.ID {
			t.Error("Data was not written correctly")
		}
	})
}


func TestSafeJSONManager_BackwardCompatibility(t *testing.T) {
	tempDir := t.TempDir()
	filename := filepath.Join(tempDir, "legacy_test.json")
	
	// Test legacy interface
	manager := NewSafeJSONManager(filename)
	defer manager.Close()
	
	ctx := context.Background()
	
	testData := TestData{ID: 1, Name: "legacy_test", Value: 100}
	
	err := manager.WriteJSON(ctx, testData)
	if err != nil {
		t.Fatalf("Legacy WriteJSON failed: %v", err)
	}
	
	var readData TestData
	err = manager.ReadJSON(ctx, &readData)
	if err != nil {
		t.Fatalf("Legacy ReadJSON failed: %v", err)
	}
	
	if readData.ID != testData.ID || readData.Name != testData.Name {
		t.Error("Legacy interface data mismatch")
	}
	
	// Test legacy Exists method
	if !manager.Exists() {
		t.Error("Legacy Exists should return true")
	}
}

func TestJSONManager_ContextCancellation(t *testing.T) {
	tempDir := t.TempDir()
	filename := filepath.Join(tempDir, "context_test.json")
	
	manager := NewJSONManager(filename, nil)
	defer manager.Close()
	
	t.Run("CancelledContext", func(t *testing.T) {
		ctx, cancel := context.WithCancel(context.Background())
		cancel() // Cancel immediately
		
		testData := TestData{ID: 1, Name: "test", Value: 42}
		err := manager.WriteJSON(ctx, testData)
		if err == nil {
			t.Error("Expected error with cancelled context")
		}
		
		var readData TestData
		err = manager.ReadJSON(ctx, &readData)
		if err == nil {
			t.Error("Expected error with cancelled context")
		}
	})
	
	t.Run("TimeoutContext", func(t *testing.T) {
		ctx, cancel := context.WithTimeout(context.Background(), 1*time.Nanosecond)
		defer cancel()
		
		time.Sleep(10 * time.Millisecond) // Ensure context times out
		
		testData := TestData{ID: 1, Name: "test", Value: 42}
		err := manager.WriteJSON(ctx, testData)
		if err == nil {
			t.Error("Expected timeout error")
		}
	})
}

// Benchmark tests
func BenchmarkJSONManager_Write(b *testing.B) {
	tempDir := b.TempDir()
	filename := filepath.Join(tempDir, "benchmark.json")
	
	manager := NewJSONManager(filename, nil)
	defer manager.Close()
	
	ctx := context.Background()
	testData := TestData{ID: 1, Name: "benchmark", Value: 42}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		testData.ID = i
		err := manager.WriteJSON(ctx, testData)
		if err != nil {
			b.Fatalf("Write failed: %v", err)
		}
	}
}

func BenchmarkJSONManager_Read(b *testing.B) {
	tempDir := b.TempDir()
	filename := filepath.Join(tempDir, "benchmark_read.json")
	
	manager := NewJSONManager(filename, nil)
	defer manager.Close()
	
	ctx := context.Background()
	testData := TestData{ID: 1, Name: "benchmark", Value: 42}
	
	// Write initial data
	err := manager.WriteJSON(ctx, testData)
	if err != nil {
		b.Fatalf("Initial write failed: %v", err)
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		var data TestData
		err := manager.ReadJSON(ctx, &data)
		if err != nil {
			b.Fatalf("Read failed: %v", err)
		}
	}
}