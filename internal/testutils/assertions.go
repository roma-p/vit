package testutils

import (
    "os"
    "reflect"
    "testing"
)

func AssertExists(t *testing.T, path string) {
    t.Helper()
    
    if _, err := os.Stat(path); os.IsNotExist(err) {
        t.Fatalf("Path %s does not exist", path)
    }
}

func AssertNotExists(t *testing.T, path string) {
    t.Helper()
    
    if _, err := os.Stat(path); err == nil {
        t.Fatalf("Path %s should not exist", path)
    }
}

func AssertEqual[T comparable](t *testing.T, got, want T) {
    t.Helper()
    
    if got != want {
        t.Fatalf("got %v, want %v", got, want)
    }
}

func AssertSliceEqual[T comparable](t *testing.T, got, want []T) {
    t.Helper()
    
    if !reflect.DeepEqual(got, want) {
        t.Fatalf("got %v, want %v", got, want)
    }
}
