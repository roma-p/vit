package testutils

import (
    "os"
    "testing"
    "path/filepath"
)

func TempDir(t *testing.T, pattern string) (string, func()) {
    t.Helper()
    tempDir, err := os.MkdirTemp("", pattern)
    if err != nil {
        t.Fatalf("Failed to create temp dir: %v", err)
    }
    cleanup := func() {
        if err := os.RemoveAll(tempDir); err != nil {
            t.Errorf("Failed to cleanup temp dir %s: %v", tempDir, err)
        }
    }
    return tempDir, cleanup
}


func CreateDirectories(t *testing.T, basePath string, dirs []string) {
    t.Helper()
    for _, dir := range dirs {
        fullPath := filepath.Join(basePath, dir)
        if err := os.MkdirAll(fullPath, 0755); err != nil {
            t.Errorf("Failed to create test directory %s: %v", basePath, err)
        }
    }
}
