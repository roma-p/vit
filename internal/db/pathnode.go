package db

import (
    "os"
    "fmt"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"path/filepath"
	"time"
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


func AddAssetToPackage(repo_path, asset_string, uuid string,) error {
    pkg_path := filepath.Dir(asset_string)
    asset_name := filepath.Base(asset_string)
    node_data:= NewPathNodeFromPkgPath(pkg_path)
    node_data.Children = append(node_data.Children, asset_name)
    node_data.Assets = make(map[string]string)
    node_data.Assets[asset_string] = uuid
    path:= filepath.Join(repo_path, GenerateNodePathFromPkgPath(pkg_path))
    if err := os.MkdirAll(filepath.Dir(path), 0755); err != nil {
        return err
    }
    manager := NewSafeJSONManager(path)
    ctx := context.Background()

    fmt.Printf("%s\n", path)

    if err:= manager.WriteJSON(ctx, node_data); err != nil {
        return  err
    }

    return nil
}
