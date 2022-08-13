
# 13/08/22 -------------------------------------------------------------------
- finish doc on current version of CLI.
- play with on install and list all things that does not work.

- find a way to distribues man.
- autocompletion?

Playing with viti, notes:
    - list template
    - update template using vit template add -f (done on CLI but not in code). 


# 12/08/22 -------------------------------------------------------------------

x To properly 'play' with the package needs to setup the packaging...
- Add CLI documentation. 
- Tests:
    x Change tests to not repeat the "package and asset creation".
    x Correct tests to handle all the raises.


# 11/08/22 -------------------------------------------------------------------

on a single big modif: 
    x add a command line interface
    x use exception for major functions instead of return code.
    x write all the requird log.
the 500 lines commit.

deleted "commit" function. To recode later...  

vocabulary notes: 
    - file_path not filepath
    - get rid of every "add" -> "create" instead. Makes more sense.

# 10/08/22 -------------------------------------------------------------------

todo:
    x remove branch from file_file_track_list (and handle side effects)
    x you can only commit at the top of the branch.
      If a file is not at top of any branches, commit shall be refused.
    - bug on "ditors": when keeping file, editors not updated.
    - first naîve implementation of commnand line -> main_commads.

rules:
    - when committing a file on local repo: 
        - if the file is not on a branch, just can't commit it. sry.
    - SO in tracked file:
        - only track files, undifferently of branches/tag etc
        - track files should only be : file local / file origin 
          (no info on branch / tag).

what a real commit is? annotated I mean.
I guess a commit that does not belong to the branch, just the tagged filed as origin.
naming of this file has to include branch name. how to get it?
How to get branch from a middle commit when branch info is only on the tip...?

>> Lock: should not lock all repo,
    - too much constraint that too person can modify repo at same time
    - lcok file for every asset (store them into asset dir).

>> probably needs some live easing feature: 
    vit update file -> we saved the command that was able to fetch asset
                       so we can launch it again.
    vit commit does not delete file but remove the editor token? 
    so that "clear" only delete file without editor token?


# 09/08/22 -------------------------------------------------------------------

todo: 
    x fetch asset from a different repo that the one used to create the asset fetch.
    x debug with real SCP connection...
    x make branching works again.
    x tag light naive first implementation ("let's see")
    - fetch by tag. (why so?)
    - commit message, therefore, maybe restructure tree data as namedtuple.

next: 
    - 1 tag for real.
    - 2 command line
    - 3 rework exception
    - 4 add commit message

one tagging: 
    - allow lightweight tags? just a static pointer to a commit, easy to implement.
    - annoted tags: a commit in its own form:
        - existing in its own real (not in the commit section of the tree file).
        - therefore, a commit message, and possibility for hooks (define hooks by asset or package).
        - possibility to automatically name the tag:
            -a (autoname), by default upgrade minor version.
            -a -m upgrade minor. 
            -a -M upgrade Major. 

SSH_connection.py started to work again by doing some terminal scp to restart it. 
(it asked for a "do you know host", "host is known as" -> to autoresolve using paramiko...)

file_tracker.py {
    "branchs" : {} -> only files listed here can you commit. And reference them somewhere.
    "tags": {} -> you can't commit, but fetch it as readonly.
    "file": {} -> same
}

# 08/08/22 -------------------------------------------------------------------

todo:
    * commit.
    x commit by file and not global
    x commit releases "editor" and del local file
    x unless "keep" option
    x throw excpetions if readonly.
    * fetch
    x if file already exists, keep it and only fetch SHA of origin.
        x therefore store sha for commis in treefile.
        x therefore store sha of templates.
    x unless the "force" option. In this case overwrite original file.
    - convert commit to exception code...

Behaviour on commit:
    - if editable and no keep:
        - if changes:
            - create a new file on origin.
            - release the "editor".
            - delete local file.
        - if no changes:
            - no file created.
            - release the "editor"
            - delete local file.
    - if editable and keep:
        - create file at origin if changes.
        - no deletion of local file.
        - editor token is kept.
    - if readonly:
        - not affected by commit...
        - if try to commit it:
            - will ask to take "editor token"
            - otherwise will ask for to create another branch.
    - global commit:
        commit only the "editor" files. Ignore the readonlys.

Rules:
    - when releasing "editor" token, always delete local file to prevent ambiguity for user.
    - by default we commit files one by one, not patches over various files.

Patches to do from current behaviour:
- commit (file):
    - if not tracked: ignore.
    - if readonly : fetch it as editor first.
    - else: proceeds...

- fetchAsset(file):
    - shall handle the case where the file alrady exists...
    - if so:
        - get the sha_256 from origin file.
        - but does not copy origin file to local branch (to not overwrite it).

