package vitlib

import (
	"path/filepath"
	"testing"
	"vit/internal/testutils"
)

func TestCheckPathIsVitRepoOk(t *testing.T) {
    tempDir, cleanup := testutils.TempDir(t, "test_repo_path_vit_repo_*")
    defer cleanup()
    testutils.CreateDirectories(t, tempDir, []string{"path/to/ok/.vit"})
    s, _ := CheckPathIsVitRepo(filepath.Join(tempDir, "path/to/ok"))
    testutils.AssertEqual(t, true, s)
}

func TestCheckPathIsVitRepoNotRepo(t *testing.T) {
    tempDir, cleanup := testutils.TempDir(t, "test_repo_path_vit_repo_*")
    defer cleanup()
    testutils.CreateDirectories(t, tempDir, []string{"path/to/ko"})
    s, _ := CheckPathIsVitRepo(filepath.Join(tempDir, "path/to/ko"))
    testutils.AssertEqual(t, false, s)
}

func TestCheckPathIsVitRepoNotExists(t *testing.T) {
    tempDir, cleanup := testutils.TempDir(t, "test_repo_path_vit_repo_*")
    defer cleanup()
    s, _ := CheckPathIsVitRepo(filepath.Join(tempDir, "path/to/ko"))
    testutils.AssertEqual(t, false, s)
}

func TestFindVitRepoFromPathOk(t *testing.T) {
    tempDir, cleanup := testutils.TempDir(t, "test_repo_path_vit_repo_*")
    defer cleanup()
    testutils.CreateDirectories(
        t, tempDir,
        []string{
            "path/to/ok/.vit",
            "path/to/ok/some/subdir",
        },
    )
    path_to_test := filepath.Join(tempDir, "path/to/ok/some/subdir")
    path_repo, path_sub, error := FindVitRepoFromPath(path_to_test)
    testutils.AssertEqual(t, filepath.Join(tempDir, "path/to/ok/"), path_repo)
    testutils.AssertEqual(t, "some/subdir", path_sub)
    testutils.AssertEqual(t, nil, error)
}

func TestFindVitRepoFromPathNoRepoFound(t *testing.T) {
    tempDir, cleanup := testutils.TempDir(t, "test_repo_path_vit_repo_*")
    defer cleanup()
    testutils.CreateDirectories(t, tempDir, []string{ "path/to/ok/some/subdir"})

    path_to_test := filepath.Join(tempDir, "path/to/ok/some/subdir")
    _, _, err := FindVitRepoFromPath(path_to_test)
    testutils.AssertEqual(t, false, err==nil)
}

func TestFindVitRepoFromPathPathNotExists(t *testing.T) {
    tempDir, cleanup := testutils.TempDir(t, "test_repo_path_vit_repo_*")
    defer cleanup()
    testutils.CreateDirectories(t, tempDir, []string{ "path/to/ok/some/"})

    path_to_test := filepath.Join(tempDir, "path/to/ok/some/subdir")
    _, _, err := FindVitRepoFromPath(path_to_test)
    testutils.AssertEqual(t, false, err==nil)
}
