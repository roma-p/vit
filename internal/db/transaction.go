package db

import (
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
