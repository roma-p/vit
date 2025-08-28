package db

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"time"
)

type TransactionOperation string
const (
    Creation TransactionOperation = "creation"
)

type Transaction struct {
    AssetPath string                `json:"asset_path"`
    Operation TransactionOperation  `json:"operation"`
    Modified time.Time              `json:"modified"`
    User string                     `json:"user"`
    Size uint32                     `json:"size"`
}

func GenerateTransactionPathFromAssetPath(asset_path string) string {
    hash := sha256.Sum256([]byte(asset_path))
    hex_string := hex.EncodeToString(hash[:16])
    return filepath.Join(
        ".vit",
        "transaction",
        hex_string + ".json",
    )
}

func CreateNewTransaction(repo_path, asset_path string) error {
    transaction_path := GenerateTransactionPathFromAssetPath(asset_path)
    if _, err := os.Stat(transaction_path); err == nil {
        return fmt.Errorf("asset already beeing created!")
    }
    manager := NewSafeJSONManager(filepath.Join(repo_path, transaction_path))
    ctx := context.Background()

    transaction_data := Transaction{
        AssetPath: asset_path,
    }

    if err:= manager.WriteJSON(ctx, transaction_data); err != nil {
        return  err
    }

    return nil
}
