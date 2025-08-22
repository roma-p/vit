package db

// import (
// 	"slices"
// 	"strings"
// 	"time"
// )


// func (am *AssetManager) AddAsset(assetPath string, assetID string) error {
//     pathParts := strings.Split(assetPath, "/")
//     
//     // Update each level of the path hierarchy
//     for i := 1; i <= len(pathParts); i++ {
//         partialPath := strings.Join(pathParts[:i], "/")
//         
//         // Each path level gets its own node - no contention!
//         err := am.updatePathNode(partialPath, func(node *PathNode) {
//             if i == len(pathParts) {
//                 // Leaf node - add the actual asset
//                 if node.Assets == nil {
//                     node.Assets = make(map[string]string)
//                 }
//                 node.Assets[pathParts[i-1]] = assetID
//             } else {
//                 // Intermediate node - ensure child path exists
//                 childPath := strings.Join(pathParts[:i+1], "/")
//                 if !slices.Contains(node.Children, childPath) {
//                     node.Children = append(node.Children, childPath)
//                 }
//             }
//             node.Version++
//             node.Modified = time.Now()
//         })
//         
//         if err != nil { return err }
//     }
//     
//     // Also update asset registry for fast UUID lookups
//     return am.updateAssetRegistry(assetID, assetPath)
// }
//
// func (am *AssetManager) updatePathNode(path string, updateFn func(*PathNode)) error {
//     nodePath := am.getNodePath(path)
//     lockPath := nodePath + ".lock"
//     
//     // Simple file locking per node - fine-grained, no global bottleneck
//     return am.withFileLock(lockPath, func() error {
//         node, _ := am.loadPathNode(path)
//         if node == nil {
//             node = &PathNode{Path: path}
//         }
//         
//         updateFn(node)
//         return am.savePathNode(node)
//     })
// }
