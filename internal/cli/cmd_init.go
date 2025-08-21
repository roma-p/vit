package cli
import (
    "fmt"
    "vit/internal/vitlib"
)

func initCmd(args []string) {
    fmt.Printf("bonjour!\n")
    vitlib.InitVitRepo(args[0])
}

