package db

import (
    "time"
    "crypto/sha256"
    "encoding/hex"
    "path/filepath"
)

type PathNode struct {
    Path     string            `json:"path"`      // "sequence01/shot010"
    Assets   map[string]string `json:"assets"`    // filename -> assetID
    Children []string          `json:"children"`  // child path prefixes
    Parent   string            `json:"parent"`    // parent path
    Version  int64             `json:"version"`   // for conflict resolution
    Modified time.Time         `json:"modified"`
}

func GenerateNodePathFromPkgPath(pkg_path string) string {
    // Hash path to create filesystem-safe filename
    hash := sha256.Sum256([]byte(pkg_path))
    hex_string := hex.EncodeToString(hash[:16])
    return filepath.Join(
        ".vit",
        "path-index",
        hex_string[:2], 
        hex_string[2:] + ".json",
    )
}

func NewPathNodeFromPkgPath(pkg_path string) *PathNode {
    return &PathNode{
        Path: pkg_path,
    }
}
