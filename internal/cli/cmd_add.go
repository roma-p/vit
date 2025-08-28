package cli
import (
    "log"
    "fmt"
    "vit/internal/db"
    "vit/internal/vitlib"
)

func addCmd(args []string) {
    path:= db.GenerateNodePathFromPkgPath(args[0]);

    vit_path, asset_path, err := vitlib.FindVitRepoFromPath(args[0], true)
    if err != nil { log.Fatal(err) }

    err = db.CreateNewTransaction(vit_path, asset_path)
    if err != nil { log.Fatal(err) }


    asset, err := db.NewAssetNodeFromAssetPath()
    if err != nil { log.Fatal(err) }

    asset.AddComit(asset_path, "", "")
    err = asset.WriteAssetNode(vit_path)
    if err != nil { log.Fatal(err) }
    
    err = db.AddAssetToPackage(vit_path, asset_path, asset.AssetUID);
    if err != nil { log.Fatal(err) }
    fmt.Printf("bonjour '%s'\n", path)
}

