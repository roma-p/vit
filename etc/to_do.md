
clone/commit
    - commit/cloning only works because src/dst have same paths. 
    - find a way so all assets in local repo are on same dir, but different dir in real life.

fetch multiple version so artists can compare them. 
    - now: need to fetch/rfetch. 
    - how to allow user to fetch same asset multiple time?
## 
We don't want users to copy all templates scenes as it is useless copying....
so process for new asset from template is: 
    - 1/ fetch template from origin
    - 2/ check package existence on origin (if not, offer to create it). 
    - 3/ scp the template in a subdir of local dir but register the path of the asset somewhere. 
    - 4/ on commit: create the path to the package and scp the file. 

But not, confusing between asset and subpckage. an asset as to belong to a subpackage. 

Testing too much stuff at once

note: every commit is a new version? 
      for first implementation, we shall consider so. 
      If too much data is stored, add a "replace" option on commit.

### HOW TO OPEN file? 
At the moment, I have horrible files with terrible UUID. How, as an artist will I open it? 
simlinks? a bit shitty. A command? But with simlinks, only one possible version at the time wich is congruesome. I want to be able to open as much as I can. 

-> Actually a big problem to resolve, and I don't know the usage yet... So keep it simple: one branhc at the time...

-> basic info on what do you have locally. vit info local to implement...

-> all files handlers as context manager to only parse them once: 
    with ... as file_tree: 
    with ... as file_tracker:
    with ...
    maybe not.... 
    but optimisation to parse json file the minimum

-> what to do with "path"? how to get rid of it? see with thibaut... 

-> commits and track list to rethink. 
I guess on commit: 
- create the new file
- reference it in tree dir
- reference it in track file
- remove previous file from disk and tree dir. 

But then... why clear files? 
should i refetch it again? 
I guess i keep ownnership on the new file... or maybe not?
By default i don't keep ownership. a flag allows me to. (and to refetch new commit as editable. 

OK, so as I don't have readonly or referenced file at the moment, clear can't do anything I guess. 
Need to implement readonly first.  

---------------------------------------------------

Roadmap:
    x finish "create asset maya"
    x fetch the asset as editor
    x commit it 
    x fetch it again
    x branch it 
    x modify it 
    x commit it
    x print local repo status
    - clean local repo
    - fetch it as readonly 
    - branch from local? 
    - try to commit it -> fail
    - so create new branch instead.

THEN: 
    x clean code
    x split SSH Wrapper so I can mock it without having to write my password...
    - get / put method needs rework.
    - rename files...

FINALLY:
    - show it to T
    - rewrite it in Rust.

MISC: 
    - create_template and creat_asset shan't be connected to any DCC. (no maya houd etc...)
    - init_origin renamed to init.
