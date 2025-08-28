package db

import (
	"os"
	"context"
	"strings"
	"crypto/rand"
	"encoding/hex"
	"path/filepath"
	"time"
)

type AssetNodeCommit struct {
	CommitId string `json:"id"`
	PayloadSize string `json:"size"`
	PayloadFile string `json:"file"`
	PayloadHash string `json:"hash"`
	Author string `json:"author"`
	Timestamp time.Time `json:"timestamp"`
	Message string `json:"message"`
	Dependencies map[string]string `json:"dependencies"`
}

type AssetNode struct {
    AssetUID     string           `json:"asset-uid"`
    PathHistory []string          `json:"path-history"`  // store commitid? general commits to the prod?
    Commits []AssetNodeCommit	  `json:"commits"`  // store commitid? general commits to the prod?
}

func NewAssetNodeFromAssetPath() (*AssetNode, error) {
	uid, err := GenerateAssetNodeUID()
	if err != nil { return  nil,  err}
	return &AssetNode{
		AssetUID: uid,
	}, nil
}

func GenerateAssetNodePathFromUID(uid string) string{
	return  filepath.Join(
		".vit",
		"asset",
        uid[:2], 
        uid[2:] + ".json",
	)
}

func (a *AssetNode) AddComit(asset_path, parent_commit_id, branch string) error {
	commit_id, err := generatUID(2)
	if err != nil {return err}
	t := AssetNodeCommit{
		CommitId: commit_id,
		PayloadFile: a.GeneratePayloadPathForBranch(asset_path, branch, commit_id),
	}
	a.Commits = append(a.Commits, t)
	return  nil
}

func GenerateAssetNodeUID() (string, error){
	return  generatUID(16)
}

func (a *AssetNode) WriteAssetNode(repo_path string) error{
	path := filepath.Join(repo_path, GenerateAssetNodePathFromUID(a.AssetUID)) 
    if err := os.MkdirAll(filepath.Dir(path), 0755); err != nil {
        return err
    }
    manager := NewSafeJSONManager(path)
    ctx := context.Background()
    if err:= manager.WriteJSON(ctx, a); err != nil {
        return  err
    }
	return  nil
}

func (a *AssetNode) GeneratePayloadPathForBranch(asset_path, branch, commit_id string) string {
	ext := filepath.Ext(asset_path)
	asset_path = strings.TrimSuffix(asset_path, ext)
	if branch == "" {
		branch = "main"
	}
	path := filepath.Join(
		".vit",
		"content",
		asset_path + "-branch-" + branch + "-" + commit_id + ext,
	)	
	return path
}

func generatUID(byteLength int) (string, error) {
    bytes := make([]byte, byteLength)
    if _, err := rand.Read(bytes); err != nil {
        return "", err
    }
    return hex.EncodeToString(bytes), nil
}

