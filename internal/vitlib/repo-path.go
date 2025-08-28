package vitlib

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// RepoPathError
type RepoPathErrorTag int
const (
    NotARepo RepoPathErrorTag = iota
    NoRepoFound
)
type RepoPathError struct {
    Tag  RepoPathErrorTag
    Path  string
}
func (e *RepoPathError) Error() string {
	switch e.Tag {
	case NotARepo:
        return fmt.Sprintf("path is not a vit repository: %s", e.Path)
	case NoRepoFound:
        return fmt.Sprintf("path does not belong to any vit repository: %s", e.Path)
	default:
		return "repo error"
	}
}


func CheckPathIsVitRepo(path string) (bool, error) {
    info, err := os.Stat(filepath.Join(path, ".vit"))
    if err != nil {
        return false, &RepoPathError{Tag: NotARepo, Path: path}
    } else if !info.IsDir() {
        return false, &RepoPathError{Tag: NotARepo, Path: path}
    } else {
        return  true, nil
    }
}

func FindVitRepoFromPath(path string, ignore_non_existing bool) (string, string, error) {

    if !ignore_non_existing {
        _, err := os.Stat(path)
        if err != nil {
            return  "", "", err
        }
    }

    found := false
    currpath, err := filepath.Abs(path)

    if err != nil {
        return  "", "", &RepoPathError{Tag: NoRepoFound, Path: path}
    }

    for {
        if currpath == string(filepath.Separator){
            break
        }
        s, _ := CheckPathIsVitRepo(currpath)
        if s {
            found = true
            break
        } else {
            currpath = filepath.Dir(currpath)
        }
    }

    if found {
        return  currpath, strings.TrimPrefix(path, currpath + string(filepath.Separator)), nil
    } else {
        return  "", "", &RepoPathError{Tag: NoRepoFound, Path: path}
    }
}
