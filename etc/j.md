
# 08/08/22 -------------------------------------------------------------------

todo:
    * commit.
    x commit by file and not global
    x commit releases "editor" and del local file
    x unless "keep" option
    - throw excpetions if readonly.
    * fetch
    - if file already exists, keep it and only fetch SHA of origin.
    - unless the "force" option. In this case overwrite original file.

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

