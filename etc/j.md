# 22/04/25 -------------------------------------------------------------------

ROADMAP:
    - support for ssh-key! (as server will only authorize ssh key login)
    - download progress bar for file.
    - rework base of packages: no 'package vs asset'
       -> only asset exists.
       -> assets are defined by path: eg "seq/shot/mod"
       -> but maybe an argument to tell "seq/shot" does not exists want to create it? or "-f"
       Why? Because it removes a concept from vit: "packages". Only assets exists. simpler.
       (big change though)
    - rework tag system to have "tag family" how does this work?
      is the tag family per branch ? (and therefore is a "category), or per asset?
      git tag file.ma -C realase 1
    - handle dependency system: dcc scenes only points to handle!
      therefore the overall versionning / dependency system is built OUT of dcc scenes.
      transparent to dcc.
    - maybe change: commit -r: release: default is keeping, not releasing?

vit handle add path/to/my/asset camera_wip     -b base # track branch base
vit handle add path/to/my/asset camera_release -T Release # track tag of type release

vit link add path/to/my_working_copy.ma path/to/my/asset -h camera_release

vit link update file.ma --dry-run
vit link update file.ma --last
vit link update file.ma -i
vit link update * -i

vit commit path/to/my_working_copy.ma -m updated dependancy

vit info dump file.ma out.json -> dump manifest of asset with all resolved dependancy.

can also link with static file without handle:
vit link add path/to/my_working_copy.ma -t RELEASE 1.2.3
vit link add path/to/my_working_copy.ma -b base

rig/
    rig_branch_base.ma
    links/
        handle_mod_tag_release.ma -> ../mod/handle_mod_tag_release.ma
mod/
    mod_tag_release_0.1.3.ma
    handle_mod_tag_release.ma -> mod_tag_release_0.1.3.ma

vit link add camera path/to/my_working_copy.ma path/to/other/asset -h handle_name
vit link add camera path/to/my_working_copy.ma path/to/other/asset -t base release

lgt:
    lgt_branch_base.ma
    links/
	camera -> ../path/to/other/asset_base_release.1.2.3.ma

# 06/02/23 -------------------------------------------------------------------

- rework of already existing need to be finer...
    -> branch / commit / tag can be grouped.

# 04/02/23 -------------------------------------------------------------------

>>> required before merge: 
    - vit_conncetions instanciations entirely removed from vit_lib
    - no test corrected (maybe copy paste of setup in distant class)
    - reworked exceptions. 
    - local functions identified. 
    - tree_fetch / tree_func cleaned. 
    - code duplications fixed.

- in tests: multiple "init_repos" : 
    - empty 
    - basic
    - with packages etc...
- retro fit asset_template to use "empty".
    
# 03/02/23 -------------------------------------------------------------------

x editability cache
x fetch (or displaying infos: time of last fetch.)
    so when fetching, track_info : trackinfo_last-fetch 

add vit_connection as argument to vit_command: 
x asset create
x asset template
x branch 
x checkout 
x commit
x fetch
x package
x rebase
? repo_init_clone -> maybe only CLI available for now, to patch later
x tag
x update

-> handle repo_init_clone before patching tests...

# 02/02/23 -------------------------------------------------------------------

>>> delete all "list" stuff
x asset
x package
x template
x branch 
x tag
x log
x clean -> ajouter le cache d'éditabilité. (info duplication but no choice)
x info  -> same 

- tree_func & tree_fetch to clean someday...

# 26/01/23 -------------------------------------------------------------------

- so no vit_connection created by vit_lib? 
- a vit_context obj? local_path / vit_conncetion.

# 09/12/22 -------------------------------------------------------------------

- rework exceptions into 
    - vit_data_already_exists(enum vit_data_type)
    - vit_data_not_found(enum vit_data_type)
(raher than having specifically tagnotfound, assetnotfound etc...)
better compromise between 'having exceptions that are treated the same'
and 'just reading the code I know what happened.'

# 02/12/22 -------------------------------------------------------------------

cl_fetch with ideal vit_sshconncetion constructor. 
then write contructor for neovit and test it. 
If it works on both, then move on...

# 02/12/22 -------------------------------------------------------------------

-> things to do in order to get neovit running! 
- fetchilize vit... -> a backup of who is editor of what shall be maintained in local
			(even if not up to date)
- so get rid of getting files for lot of "ssh_connect" 
- for the remaining command: 
	- get rid of ssh_connect -> use it in CLI LIB. 
	- create another construct to ssh_connect with password (to be used by vit)

Service vit : 
- @vit_connection.lock
- @vit_connection.lock_unlock

What differences between vit_connection and ssh_connection?
Needs to différenciate "dbb transaction" and "data transfer":
	- lock only when dbb transaction
	- unlock with data transfer
	- add a tmp file to delete when data transfer is complete. 
	- but again, if crash? what do we do? 
		- an attribute: "downloading this file."
		- then crahs....
		- then reevert metadata copy!!!
COMPLICATED

# 10/11/22 -------------------------------------------------------------------

(to test but done).
missing before presentation: 
    x organised command line lib.
    - test every single command of the new command line lib.
    x Json: raise STUPID ERROR if json file func is read before beeing open.
    X Json: SHALL NOT UPDATE if any exceptions happens
    x VIT CONNECTION: dispose mechanism to unlock dir if something happens. 
    x correct graph bug
    > Exceptions to be split into vitlib / ssh / fileHandlers.
    - EXEMPLE PACAKGE.

# 06/10/22 -------------------------------------------------------------------

- bug on graph: if branch from first commit of asset, doest not print branch.
- bug on ssh_connect on at list one command.
- need a way to update commit, replace commit. replace last. -r

# 26/08/22 -------------------------------------------------------------------

vit tag package asset -b branch -l -name <name>
vit tag package asset -c commit -l -name <name>
vit tag package asset -b branch -a -name <name> -m <message>

#only available with package asset.
vit tag package asset -b branch -v <increment id> -m <message>

# requires checkout of a branch.
vit publish checkout_file increment

# 22/08/22 -------------------------------------------------------------------

x bug on update to get editable: does not discard local change but indextrackfile see no changes
x bug on tag version: if auto no need for tag name.
x graph branch: "branch: nouppercase branch"
x rebase does not work.
- checkout from commit does not make use of package path? weird...
    -> also the case for branch from commit.
> list tag by branch / only versionned tag not done.
x rebase does not appear on graph but appears on log. Maybe branch tip not updated upon rebase?
x rebase if I'm the editor? need to check if local changes. either commit it or reset it.
x K don't keep file. kept as editor in tree-asset but file deleted and removed from indexTracked file.
- rebase from tag.
x versionned tag on branch dir when created asset
x probalby editor of too much things! editor is not always released.
x info
- branch from commit.

x add clean to CLI.
- debug install.

update spec:
"don't want the pain of using checkout when already have a checkout of the branch"

"I have changes on branch wich i'm not editor".
"I want to see progress on the file that I keept as ref for conveniance".

!!! > bug: update -e with no reset still reset asset? at least commit see nothing to commit

> log / graph pager
> ssh_key support.


# 21/08/22 -------------------------------------------------------------------

x committing file and keeping it does not update traced_index_sha.


ROADMAP:

- ALPHA 0.1
    x graph
    x log
    x update
    x clean
    x info
    x rebase
    - (and debug obviously...)
- ALPHA 0.2
    - reference between assets
        (either by branch / commit / tag)
    - static asset
    - hook on commit / tag / branch.
    - maya hooks.
- ALPHA 0.3
    - differenct type of asset handled:
        - dcc scene file.
        - cache file (to compress? no need to branch commit and so?)
        - sequence of image: a directory is the asset. compress dir.
    - macro: to execute multiple vit command at once.
- BETA 0.4:
   -> enough to create first vesion of "making decisions" repository.

# 20/08/22 -------------------------------------------------------------------

> rename rebase to reset... rebase here does not make sense.

x finish graph once for all !!
x do update and 100 % test coverage.

# 19/08/22 -------------------------------------------------------------------

graph:
    x multiple branches at once
    x no commit on new branch debug.
    x draw index error.
    x add tagg ! (multiple tag possible?)
    x rewrite gen_graph so it is cleaner? a class? a scene?

bug:
    annotated_tag creation crash sometimes...
    if tag before is not auto? '5 args instead of 6...'
    (you can find it in test_graph)

# 15/08/22 -------------------------------------------------------------------

nexts:
    x vit graph
    x vit update
    x vit clean
    x vit rebase ?
    x debug command line.

then first alpha done

# 14/08/22 -------------------------------------------------------------------

x implement auto versionning.
x detect manual versionning that match formatter of auto versionning
- for fun: do graph.

>> for increased clarity: three types of commit: light / annotated / versionned
>> all helpers for versionned tag in a single file.

# 13/08/22 -------------------------------------------------------------------

>> when tagging: asset tag and branch.
>> register last update. 

and I forgot, but this morning it was crystal clear lol.
When referencing asset to another one: 
    - give tag and branch
    - when tagging: registering last tag on branch. 
    - if ta referenced is not equal to asset "last tag on branch"
        inform user that anotehr tag is available. 

REFACTO NEEDED AT SOME POINT: 
    needs to separate "commit id" from "commit file".
    needed to cheeckout by commit. But might be useful elsewhere.


-> if not rebase but modification... Raises ChangeToCommit. So conflict...
   but because of exclusive commit shall be ok..
-> when cleaning: if file no longer exists, removed from tracked file.

TAG:
    - tag normal
    - auto versionning.
    - auto tag by branch? 

# 09/08/22 -------------------------------------------------------------------

unit test every command, 100% !!!

x asset_template
x package
x init_repo
x asset create from template.
x asset create from file.
x checkout branch
x checkout tag
x checkout commit
x branch
- clean
x commit
x release_editable
x info
x tag

- change all path to local_path

-> probably list / get package / branchs etc from display_info to asset/package...

# 07/08/22 -------------------------------------------------------------------

- how to release file when fetch as editable? 
  vit release as begining? (and maybe change CLI afterwards...)
- problem: same info define at multiple places...
            -> editable: ONLY IN tree asset. NOT IN tracked file.
            -> but no "ssh_connect" on tree file to get the latest version for checking
               (it is always up to date since no user can set current users editor at distance).
               but need to fetch it
            -> commit is to refactore... checkout the file once? I don't think I can even do that.

- vit info:
    x taaaaabs
    x separate sha from the info "is readonly".

- make commit works again: 
    x distinguish sha from "is editable"
    x refactore: editable information only in tree_asset..
    - make clean works again
    - test case: 
        - fetch
        - commit -K
        - clean (file not deleted)
        - commit -k 
        - new modification
        - clean (file not deleted)
        - clean -force(file deleted)

# 04/08/22 -------------------------------------------------------------------

for first alpha: beeing able to store txt files (script / pitch etc)...
so!
x beeing able to create asset from file (not from template). 
x checkout: from package path / asset name - branch. 
x update: using the ref file.
x tracked file udpate: store SHA and "is_editable" as two different informations
  (now if sha is None -> means file is readonly).
- vit update /path/to/file.ma -e shall be an autorized syntax. !!!!!!!!!!!

# 03/08/22 -------------------------------------------------------------------

> afirst usable version of vit (without file interlinked):
x rename "fetch" to "checkout". (co shall be ok).
x commit with messages... "-m" for the first time.
- logs by branch (therefore log original branchng commit)
x tags (and not just the lighweight)
x checkout by commit
x tagging auto increment.
x when creating a branch, auto tagging? at least an option to do it.
x commit -K (to keep file and editable if there is), otherwise -k.
- checkout by ref: (or maybe update command?) vit update /path/to/file
x info for ref file.

with all that code to add, where to move code around shall become clearer.

# 02/08/22 -------------------------------------------------------------------

bugs:
    x create clone dir before beeing able to clone.
    x list assets of non existing package makes things crash
    x same bug with fetching asset.
    x fetch return path... deleted during refacto. That was a mistake.
    - good idea to help with commit fail message but wrongly format, too bad.
    x branch new and old inverted on CLI. 
    x creating branching breaks fetching by branch (copy dir and not file...)
    x tag just does not works...
    - fetching by tag does not work. 

# 01/08/22 -------------------------------------------------------------------

x draft of a "unit_of_work".

> define a standardize "git fetch". (what data to get for *every operation*)
  at the moment, lots of hidden bugs...


# 31/08/22 -------------------------------------------------------------------

x make basic test works with new implementation of packageIndex / packageTree / assetTree
x convert track list to work with JsonFile class.
x rename file handlers properly.
x considering only create / fetch / commit functions: find out wich path helpers I choose use.

=> path refacto.
for each path, needs three variant: 
- "raw_path": eg "assets/elephant/..."
- "local_path": eg "tests/local_repo/assets/elephant/..."
- "origin_path": eg "tests/origin_repo/assets/elephant/..."
> now: manually compute that every time I need. 
> updates? factory ?


# 17/08/22 -------------------------------------------------------------------

(no need to store tree file using SHA like git as there is likely tp have 
way less assets/package to index in vit than anonymous commits in git).


> .vit shall only contians info files (as json or whatever). It shall not contains
  any DCC files. 
> therefore templates shall be assets on their own, in a package 'templates'.

> I copy poaste only the files that are important during my operation. I shall
  create an "update" method that airsync the all .vit dir when called. Not used
  when I list data in local but used by defaut when acting on server: (branching, commiting etc...)

x make package works with new design
- clean repo before doing anythong else: 
    - path and name resolution in a single module
    - vit file handling in a submodule
    - vocb correction

# 16/08/22 -------------------------------------------------------------------

(to get rid of current pacakge / asset listing):
* packages only exist as directory, assets as a json file.
* either I get rid of the notion of package, either I found a proper to describe them. 
* a gitish solution:
* in .vit, store a package.json lists all packages names and a SHA (path to another .json)
* in the matching json: store information about the package and list all the assets
    as a map of "asset name" / sha -> path to the assetTreeFile json that already exists.
* asset tree file format does not change, but are store alongside the package.json files. 
* here the "need" to create subdir in tree with the two first characters of the sha.

>> references are declared at begining of ma file. (after fileinfo, drop it).
>> set project to set root where to find projects. 

>> How to versionned image sequence?
-> Need a feature to version directoy (full of images) (and not each image...)

>> maybe store dumb assets: assets without branch and version.
-> Constants You can just overwrite it. (for plane file).

so what are objects to store in .vit/tree? 
    - asset: a file that can be branched and tagged.
             Either a DCC scene file (ascii if possible) or a texture file or so.
    - <TODO: find a better name> a collection: a directory containing lots of file.
             The directory is versionned but not each individual file in it. 
             (and won't be 'gitted' if that feature is one day implemented). 
             Used for image sequence.
    - package: collections of the previous too.

So: abstract tree object structure. 
    can:
        - init the json file.
        - parse it from an identifier. 


# 13/08/22 -------------------------------------------------------------------

x list templates
x list packages
    - modify "add template to create the package in 'tree' subdir.
x from package list assets
x from assets list branch
x from assets list tag

x get templates from id (no track)
x update template using -f

>>  when listing assets / packages: sort them by estensions? 
    an universal way for assets / branch etc to be listed? 
>> use dot and bash autocomplete? 
>> move to a real CAS ("content addressed service").
   (therefore pacakges stored as objects too).
>> need for an update command? so that origin is not requested everytime?

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
    - sshConnection -> ssh_connection
    - package_path to package_id (and everywhere -> name to id)

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
    "branches" : {} -> only files listed here can you commit. And reference them somewhere.
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

