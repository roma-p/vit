package vitlib

import "path/filepath"

func AddAssetFileWhenNoExistingSrcInRepo(path string) {
    package_path := filepath.Dir(path)
    _ = package_path

}
