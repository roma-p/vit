package db

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"testing"
	"time"
)

func TestJSONManager_ErrorHandling(t *testing.T) {
	tempDir := t.TempDir()
	
	t.Run("InvalidJSONData", func(t *testing.T) {
		filename := filepath.Join(tempDir, "invalid_data.json")
		manager := NewJSONManager(filename, nil)
		defer manager.Close()
		
		ctx := context.Background()
		
		// Try to write data that can't be marshaled to JSON
		invalidData := map[string]interface{}{
			"invalid": make(chan int), // channels can't be marshaled to JSON
		}
		
		err := manager.WriteJSON(ctx, invalidData)
		if err == nil {
			t.Error("Expected error when writing invalid JSON data")
		}
		
		if !containsSubstring(err.Error(), "marshal") && !containsSubstring(err.Error(), "encode") {
			t.Errorf("Expected marshal/encode error, got: %v", err)
		}
	})
	
	t.Run("CorruptedJSONFile", func(t *testing.T) {
		filename := filepath.Join(tempDir, "corrupted.json")
		
		// Write corrupted JSON manually
		corruptedJSON := `{"id": 1, "name": "test", "value": invalid_json_here}`
		err := os.WriteFile(filename, []byte(corruptedJSON), 0644)
		if err != nil {
			t.Fatalf("Failed to write corrupted JSON: %v", err)
		}
		
		manager := NewJSONManager(filename, nil)
		defer manager.Close()
		
		var data TestData
		err = manager.ReadJSON(context.Background(), &data)
		if err == nil {
			t.Error("Expected error when reading corrupted JSON")
		}
		
		if !containsSubstring(err.Error(), "unmarshal") && !containsSubstring(err.Error(), "decode") {
			t.Errorf("Expected JSON unmarshal/decode error, got: %v", err)
		}
	})
	
	t.Run("PermissionDeniedWrite", func(t *testing.T) {
		// Create a directory with no write permissions
		readOnlyDir := filepath.Join(tempDir, "readonly")
		err := os.Mkdir(readOnlyDir, 0755)
		if err != nil {
			t.Fatalf("Failed to create test directory: %v", err)
		}
		
		// Remove write permissions
		err = os.Chmod(readOnlyDir, 0444)
		if err != nil {
			t.Fatalf("Failed to change directory permissions: %v", err)
		}
		defer os.Chmod(readOnlyDir, 0755) // Restore for cleanup
		
		filename := filepath.Join(readOnlyDir, "test.json")
		manager := NewJSONManager(filename, nil)
		defer manager.Close()
		
		testData := TestData{ID: 1, Name: "test", Value: 42}
		err = manager.WriteJSON(context.Background(), testData)
		
		if err == nil {
			t.Error("Expected permission denied error")
		}
	})
	
	t.Run("DiskSpaceError", func(t *testing.T) {
		// This test simulates a disk full scenario
		// In a real environment, this would be hard to test reliably
		// So we'll test the error handling structure
		
		filename := filepath.Join(tempDir, "diskfull_test.json")
		manager := NewJSONManager(filename, nil)
		defer manager.Close()
		
		// Create a very large data structure to potentially fill disk
		// Note: This might not actually fill disk in test environment
		largeData := make(map[string]string)
		for i := 0; i < 1000; i++ {
			largeData[fmt.Sprintf("key_%d", i)] = fmt.Sprintf("value_%d", i)
		}
		
		err := manager.WriteJSON(context.Background(), largeData)
		// We can't guarantee this will fail due to disk space in tests,
		// but the error handling should be robust
		if err != nil {
			t.Logf("Write failed (possibly due to disk space): %v", err)
		}
	})
	
	t.Run("FileSystemErrors", func(t *testing.T) {
		// Test with invalid file path characters
		invalidFilename := filepath.Join(tempDir, "invalid\x00filename.json")
		manager := NewJSONManager(invalidFilename, nil)
		defer manager.Close()
		
		testData := TestData{ID: 1, Name: "test", Value: 42}
		err := manager.WriteJSON(context.Background(), testData)
		
		if err == nil {
			t.Error("Expected error with invalid filename")
		}
	})
	
	t.Run("InterruptedWrite", func(t *testing.T) {
		filename := filepath.Join(tempDir, "interrupted.json")
		manager := NewJSONManager(filename, nil)
		defer manager.Close()
		
		// First, write some data successfully
		testData := TestData{ID: 1, Name: "original", Value: 100}
		err := manager.WriteJSON(context.Background(), testData)
		if err != nil {
			t.Fatalf("Initial write failed: %v", err)
		}
		
		// Simulate interruption by making temp file creation fail
		// We'll test that the original file remains intact
		
		tempFile := filename + ".tmp"
		
		// Create a directory with the temp file name to cause creation to fail
		err = os.Mkdir(tempFile, 0755)
		if err != nil {
			t.Fatalf("Failed to create blocking directory: %v", err)
		}
		defer os.Remove(tempFile)
		
		// Try to write new data - should fail
		newData := TestData{ID: 2, Name: "new", Value: 200}
		err = manager.WriteJSON(context.Background(), newData)
		if err == nil {
			t.Error("Expected write to fail due to temp file conflict")
		}
		
		// Verify original data is still intact
		var readData TestData
		
		// Remove the blocking directory first
		os.Remove(tempFile)
		
		err = manager.ReadJSON(context.Background(), &readData)
		if err != nil {
			t.Fatalf("Failed to read original data: %v", err)
		}
		
		if readData.ID != testData.ID {
			t.Error("Original data was corrupted during failed write")
		}
	})
	
	t.Run("RaceConditionRecovery", func(t *testing.T) {
		filename := filepath.Join(tempDir, "race_test.json")
		manager := NewJSONManager(filename, nil)
		defer manager.Close()
		
		ctx := context.Background()
		
		// Write initial data
		initialData := TestData{ID: 0, Name: "initial", Value: 0}
		err := manager.WriteJSON(ctx, initialData)
		if err != nil {
			t.Fatalf("Failed to write initial data: %v", err)
		}
		
		// Simulate race condition by manually creating temp file
		tempFile := filename + ".tmp"
		err = os.WriteFile(tempFile, []byte("conflicting content"), 0644)
		if err != nil {
			t.Fatalf("Failed to create conflicting temp file: %v", err)
		}
		
		// Try to write - should handle the existing temp file
		newData := TestData{ID: 1, Name: "new", Value: 100}
		err = manager.WriteJSON(ctx, newData)
		
		// Should either succeed (by overwriting temp file) or fail gracefully
		if err != nil {
			t.Logf("Write failed due to temp file conflict: %v", err)
			
			// Verify original data is still readable
			var readData TestData
			err = manager.ReadJSON(ctx, &readData)
			if err != nil {
				t.Fatalf("Failed to read data after conflict: %v", err)
			}
			
			if readData.ID != initialData.ID {
				t.Error("Data corrupted during temp file conflict")
			}
		}
		
		// Clean up
		os.Remove(tempFile)
	})
}

func TestJSONManager_TypeSafety(t *testing.T) {
	tempDir := t.TempDir()
	filename := filepath.Join(tempDir, "typesafety.json")
	
	t.Run("StructTypeMismatch", func(t *testing.T) {
		manager := NewJSONManager(filename, nil)
		defer manager.Close()
		
		ctx := context.Background()
		
		// Write one type of data
		testData := TestData{ID: 1, Name: "test", Value: 42}
		err := manager.WriteJSON(ctx, testData)
		if err != nil {
			t.Fatalf("Failed to write test data: %v", err)
		}
		
		// Try to read into different struct type (but disable strict parsing first)
		type DifferentStruct struct {
			DifferentField string `json:"different_field"`
		}
		
		// Create a new manager without strict parsing for this test
		relaxedManager := NewJSONManager(filename, nil)
		defer relaxedManager.Close()
		
		// Temporarily modify the behavior by reading without DisallowUnknownFields
		file, err := os.Open(filename)
		if err != nil {
			t.Fatalf("Failed to open file for relaxed read: %v", err)
		}
		defer file.Close()
		
		// Use a standard JSON decoder without DisallowUnknownFields
		var differentData DifferentStruct
		decoder := json.NewDecoder(file)
		err = decoder.Decode(&differentData)
		
		// Should succeed but fields won't match
		if err != nil {
			t.Fatalf("Relaxed read should succeed even with type mismatch: %v", err)
		}
		
		// The different field should be empty since it doesn't exist in source
		if differentData.DifferentField != "" {
			t.Error("Field should be empty for non-existent JSON field")
		}
	})
	
	t.Run("StrictJSONParsing", func(t *testing.T) {
		manager := NewJSONManager(filename, nil)
		defer manager.Close()
		
		// Write JSON with extra field manually
		jsonWithExtra := `{"id": 1, "name": "test", "value": 42, "extra_field": "should_be_ignored"}`
		err := os.WriteFile(filename, []byte(jsonWithExtra), 0644)
		if err != nil {
			t.Fatalf("Failed to write JSON with extra field: %v", err)
		}
		
		var data TestData
		err = manager.ReadJSON(context.Background(), &data)
		
		// Should fail due to DisallowUnknownFields
		if err == nil {
			t.Error("Expected error due to unknown field")
		}
		
		if !containsSubstring(err.Error(), "unknown field") && !containsSubstring(err.Error(), "decode") {
			t.Errorf("Expected unknown field error, got: %v", err)
		}
	})
}

func TestJSONManager_ConfigurationErrors(t *testing.T) {
	t.Run("NilConfig", func(t *testing.T) {
		manager := NewJSONManager("/test/file.json", nil)
		defer manager.Close()
		
		// Should default to local mode
		if manager.config.UseSSH {
			t.Error("Expected UseSSH to be false with nil config")
		}
	})
	
	t.Run("SSHWithoutConfig", func(t *testing.T) {
		config := &JSONConfig{
			UseSSH:    true,
			SSHConfig: nil, // Missing SSH config
		}
		
		manager := NewJSONManager("/test/file.json", config)
		defer manager.Close()
		
		ctx := context.Background()
		testData := TestData{ID: 1, Name: "test", Value: 42}
		
		err := manager.WriteJSON(ctx, testData)
		if err == nil {
			t.Error("Expected error with missing SSH config")
		}
		
		expectedError := "SSH config is required when UseSSH is true"
		if err.Error() != expectedError {
			t.Errorf("Expected error: %s, got: %v", expectedError, err)
		}
	})
	
	t.Run("InvalidSSHKeyPath", func(t *testing.T) {
		sshConfig := &SSHConfig{
			Host:     "localhost",
			Port:     22,
			User:     "testuser",
			KeyPath:  "/nonexistent/key/path",
			Timeout:  5 * time.Second,
		}
		
		config := &JSONConfig{
			UseSSH:    true,
			SSHConfig: sshConfig,
		}
		
		manager := NewJSONManager("/test/file.json", config)
		defer manager.Close()
		
		ctx := context.Background()
		testData := TestData{ID: 1, Name: "test", Value: 42}
		
		err := manager.WriteJSON(ctx, testData)
		if err == nil {
			t.Error("Expected error with invalid SSH key path")
		}
		
		if !containsSubstring(err.Error(), "failed to read SSH key") {
			t.Errorf("Expected SSH key error, got: %v", err)
		}
	})
}

func TestJSONManager_ResourceLeaks(t *testing.T) {
	tempDir := t.TempDir()
	
	t.Run("FileDescriptorLeaks", func(t *testing.T) {
		filename := filepath.Join(tempDir, "fd_test.json")
		
		// Perform many operations to check for FD leaks
		for i := 0; i < 100; i++ {
			manager := NewJSONManager(filename, nil)
			
			testData := TestData{ID: i, Name: fmt.Sprintf("test_%d", i), Value: i * 10}
			err := manager.WriteJSON(context.Background(), testData)
			if err != nil {
				t.Fatalf("Write %d failed: %v", i, err)
			}
			
			var readData TestData
			err = manager.ReadJSON(context.Background(), &readData)
			if err != nil {
				t.Fatalf("Read %d failed: %v", i, err)
			}
			
			manager.Close()
		}
		
		// If there are FD leaks, this test will eventually fail
		// due to "too many open files" error
	})
	
	t.Run("LockFileCleanup", func(t *testing.T) {
		filename := filepath.Join(tempDir, "lock_cleanup_test.json")
		lockfile := filename + ".lock"
		
		// Perform operations and ensure lock files are cleaned up
		for i := 0; i < 10; i++ {
			manager := NewJSONManager(filename, nil)
			
			testData := TestData{ID: i, Name: fmt.Sprintf("cleanup_%d", i), Value: i}
			err := manager.WriteJSON(context.Background(), testData)
			if err != nil {
				t.Fatalf("Write %d failed: %v", i, err)
			}
			
			// Check that lock file is cleaned up
			if _, err := os.Stat(lockfile); !os.IsNotExist(err) {
				t.Errorf("Lock file not cleaned up after operation %d", i)
			}
			
			manager.Close()
		}
	})
}

func TestJSONManager_EdgeCases(t *testing.T) {
	tempDir := t.TempDir()
	
	t.Run("EmptyJSONData", func(t *testing.T) {
		filename := filepath.Join(tempDir, "empty.json")
		manager := NewJSONManager(filename, nil)
		defer manager.Close()
		
		// Write empty struct
		emptyData := TestData{}
		err := manager.WriteJSON(context.Background(), emptyData)
		if err != nil {
			t.Fatalf("Failed to write empty data: %v", err)
		}
		
		// Read it back
		var readData TestData
		err = manager.ReadJSON(context.Background(), &readData)
		if err != nil {
			t.Fatalf("Failed to read empty data: %v", err)
		}
		
		// Should have zero values
		if readData.ID != 0 || readData.Name != "" || readData.Value != 0 {
			t.Error("Empty data not preserved correctly")
		}
	})
	
	t.Run("VeryLargeData", func(t *testing.T) {
		filename := filepath.Join(tempDir, "large.json")
		manager := NewJSONManager(filename, nil)
		defer manager.Close()
		
		// Create large data structure
		largeData := make(map[string][]string)
		for i := 0; i < 100; i++ {
			key := fmt.Sprintf("key_%d", i)
			values := make([]string, 100)
			for j := range values {
				values[j] = fmt.Sprintf("value_%d_%d", i, j)
			}
			largeData[key] = values
		}
		
		err := manager.WriteJSON(context.Background(), largeData)
		if err != nil {
			t.Fatalf("Failed to write large data: %v", err)
		}
		
		// Read it back
		var readData map[string][]string
		err = manager.ReadJSON(context.Background(), &readData)
		if err != nil {
			t.Fatalf("Failed to read large data: %v", err)
		}
		
		// Verify some of the data
		if len(readData) != len(largeData) {
			t.Errorf("Data size mismatch: expected %d, got %d", len(largeData), len(readData))
		}
		
		if readData["key_0"][0] != "value_0_0" {
			t.Error("Large data not preserved correctly")
		}
	})
	
	t.Run("UnicodeAndSpecialCharacters", func(t *testing.T) {
		filename := filepath.Join(tempDir, "unicode.json")
		manager := NewJSONManager(filename, nil)
		defer manager.Close()
		
		testData := TestData{
			ID:    1,
			Name:  "Test with émojis 🚀 and unicode: ñoño",
			Value: 42,
		}
		testData.Nested.Field = "Special chars: \"quotes\", 'apostrophes', \\backslashes\\"
		
		err := manager.WriteJSON(context.Background(), testData)
		if err != nil {
			t.Fatalf("Failed to write unicode data: %v", err)
		}
		
		var readData TestData
		err = manager.ReadJSON(context.Background(), &readData)
		if err != nil {
			t.Fatalf("Failed to read unicode data: %v", err)
		}
		
		if readData.Name != testData.Name {
			t.Errorf("Unicode name not preserved: expected %q, got %q", testData.Name, readData.Name)
		}
		
		if readData.Nested.Field != testData.Nested.Field {
			t.Errorf("Special chars not preserved: expected %q, got %q", testData.Nested.Field, readData.Nested.Field)
		}
	})
}