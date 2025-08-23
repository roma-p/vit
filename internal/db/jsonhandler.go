package db

import (
    "context"
    "encoding/json"
    "fmt"
    "os"
    "time"
)

type SafeJSONManager struct {
    filename    string
    timeout     time.Duration
    retryDelay  time.Duration
    maxRetries  int
}

func NewSafeJSONManager(filename string) *SafeJSONManager {
    return &SafeJSONManager{
        filename:   filename,
        timeout:    10 * time.Second,
        retryDelay: 50 * time.Millisecond,
        maxRetries: 200, // 10 secs total
    }
}

func (m *SafeJSONManager) WriteJSON(ctx context.Context, data any) error {
    return m.withLock(ctx, func() error {
        return m.writeJSONAtomic(data)
    })
}

func (m *SafeJSONManager) ReadJSON(ctx context.Context, data any) error {
    return m.withLock(ctx, func() error {
        return m.readJSON(data)
    })
}

// Generic to exec func with lock.
func (m *SafeJSONManager) withLock(ctx context.Context, operation func() error) error {
    lockfile := m.filename + ".lock"
    
    // timeout ctx.
    ctx, cancel := context.WithTimeout(ctx, m.timeout)
    defer cancel()
    
    if err := m.acquireLockWithTimeout(ctx, lockfile); err != nil {
        return err
    }
    defer func() {
        if err := os.Remove(lockfile); err != nil {
            fmt.Printf("Warning: failed to remove lock file: %v\n", err)
        }
    }()
    
    return operation()
}

func (m *SafeJSONManager) acquireLockWithTimeout(ctx context.Context, lockfile string) error {
    ticker := time.NewTicker(m.retryDelay)
    defer ticker.Stop()
    
    attempts := 0
    for {
        select {
        case <-ctx.Done():
            return fmt.Errorf("timeout acquiring lock after %d attempts: %w", attempts, ctx.Err())
        case <-ticker.C:
            attempts++
            
            // Try getting lock.
            lockFile, err := os.OpenFile(lockfile, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0666)
            if err == nil {
                // write debug data into lockfile. useful?
                fmt.Fprintf(lockFile, "pid: %d\ntime: %s\n", os.Getpid(), time.Now().Format(time.RFC3339))
                lockFile.Close()
                return nil
            }
            
            // Vérifier si le lock file est trop vieux (lock orphelin)
            if info, statErr := os.Stat(lockfile); statErr == nil {
                if time.Since(info.ModTime()) > m.timeout {
                    // Lock file trop vieux, le supprimer et réessayer
                    os.Remove(lockfile)
                }
            }
        }
    }
}

func (m *SafeJSONManager) writeJSONAtomic(data any) error {
    tempFile := m.filename + ".tmp"
    
    file, err := os.Create(tempFile)
    if err != nil {
        return fmt.Errorf("failed to create temp file: %w", err)
    }
    
    defer func() {
        file.Close()
        if err != nil {
            os.Remove(tempFile)
        }
    }()
    
    encoder := json.NewEncoder(file)
    encoder.SetIndent("", "  ")
    encoder.SetEscapeHTML(false)
    
    if err = encoder.Encode(data); err != nil {
        return fmt.Errorf("failed to encode JSON: %w", err)
    }
    
    if err = file.Sync(); err != nil {
        return fmt.Errorf("failed to sync file: %w", err)
    }
    
    file.Close()
    
    if err = os.Rename(tempFile, m.filename); err != nil {
        return fmt.Errorf("failed to rename temp file: %w", err)
    }
    
    return nil
}

func (m *SafeJSONManager) readJSON(data any) error {
    if _, err := os.Stat(m.filename); os.IsNotExist(err) {
        return fmt.Errorf("file %s does not exist", m.filename)
    }
    
    file, err := os.Open(m.filename)
    if err != nil {
        return fmt.Errorf("failed to open file: %w", err)
    }
    defer file.Close()
    
    decoder := json.NewDecoder(file)
    decoder.DisallowUnknownFields() // Optionnel: strict parsing
    
    if err := decoder.Decode(data); err != nil {
        return fmt.Errorf("failed to decode JSON: %w", err)
    }
    
    return nil
}

func (m *SafeJSONManager) Exists() bool {
    _, err := os.Stat(m.filename)
    return err == nil
}
