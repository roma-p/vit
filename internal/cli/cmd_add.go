package cli
import (
    "log"
    "fmt"
    "vit/internal/db"
)

func addCmd(args []string) {
    path:= db.GenerateNodePathFromPkgPath(args[0]);
    err := db.CreateNewTransaction(args[0]);
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("bonjour '%s'\n", path)
}

