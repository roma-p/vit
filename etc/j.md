
# 09/08/22 -------------------------------------------------------------------

todo: 
    x fetch asset from a different repo that the one used to create the asset fetch.
    x debug with real SCP connection...
    x make branching works again.
    - tag light naive first implementation ("let's see")
    - fetch by tag. (why so?)
    - commit message, therefore, maybe restructure tree data as namedtuple.

next: 
    - 1 tag
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

