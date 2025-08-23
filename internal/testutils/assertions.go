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

func AssertEqual[T comparable](t *testing.T, expected, got T) {
    t.Helper()
    
    if got != expected {
        t.Fatalf("got %v, expected %v", got, expected)
    }
}

func AssertSliceEqual[T comparable](t *testing.T, expected, got T) {
    t.Helper()
    
    if !reflect.DeepEqual(got, expected) {
        t.Fatalf("got %v, expected %v", got, expected)
    }
}
