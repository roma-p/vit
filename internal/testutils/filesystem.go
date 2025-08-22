package testutils

import (
    "os"
    "testing"
)

// TempDir crée un répertoire temporaire avec cleanup automatique
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
