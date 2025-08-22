package cli
import (
    "fmt"
    "vit/internal/db"
)

func addCmd(args []string) {
    path:= db.GenerateNodePathFromPkgPath(args[0]);
    fmt.Printf("bonjour '%s'\n", path)
}

