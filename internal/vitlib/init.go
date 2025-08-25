package vitlib

import (
    "fmt"
    "os"
    "path/filepath"
)

func InitVitRepo(path string) error {
    // Check if directory already exists
    // TODO: lots of more checks here: already a vit dir? children of a vit dir?
    if _, err := os.Stat(path); err == nil {
        // TODO should allow existing directory...
        return fmt.Errorf("directory '%s' already exists", path)
    } else if !os.IsNotExist(err) {
        return fmt.Errorf("error checking directory: %w", err)
    }

    // Create all directories at once
    dirs := []string{
        path,
        filepath.Join(path, ".vit"),
        filepath.Join(path, ".vit", "path-index"),
        filepath.Join(path, ".vit", "asset"),
        filepath.Join(path, ".vit", "content"),
        filepath.Join(path, ".vit", "transaction"),
    }

    for _, dir := range dirs {
        if err := os.Mkdir(dir, 0755); err != nil {
            return fmt.Errorf("failed to create directory '%s': %w", dir, err)
        }
    }

    return nil
}
