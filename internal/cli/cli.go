package cli

import ("os"; "fmt")


type Command struct {
    Name        string
    Description string
    Run         func([]string)
}


func Run() {
    commands := map[string]Command{
        "init": {
            Name:        "init",
            Description: "Initialize a repository",
            Run:         initCmd,
        },
        "add": {
            Name:        "add",
            Description: "add an asset",
            Run:         addCmd,
        },
    }
    
    if len(os.Args) < 2 {
        showHelp(commands)
        return
    }
    
    cmdName := os.Args[1]
    if cmd, exists := commands[cmdName]; exists {
        cmd.Run(os.Args[2:])
    } else {
        fmt.Printf("Unknown command: %s\n", cmdName)
        showHelp(commands)
    }
}

func showHelp(cmdName map[string]Command) {
    fmt.Printf("aurevoir!\n")
}
