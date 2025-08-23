package vitlib

import (
    "testing"
    "vit/internal/testutils"
    "path/filepath"
)

func TestInitVitRepo(t *testing.T) {
    tempDir, cleanup := testutils.TempDir(t, "test_init_vit_repo_*")
    repo_path:= filepath.Join(tempDir, "prod_test")
    InitVitRepo(repo_path)
    testutils.AssertExists(t, repo_path)
    testutils.AssertExists(t, filepath.Join(repo_path, ".vit", "path-index"))
    testutils.AssertExists(t, filepath.Join(repo_path, ".vit", "asset"))
    testutils.AssertExists(t, filepath.Join(repo_path, ".vit", "content"))
    defer cleanup()
}
