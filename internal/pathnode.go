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

func (pn *PathNode) NodePath() string {
    // Hash path to create filesystem-safe filename
    hash := sha256.Sum256([]byte(pn.Path))
    return filepath.Join(".vit", "path-index", 
        hex.EncodeToString(hash[:8]) + ".json")
}

