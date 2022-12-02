
## VIT: Vfx Information Tracker.

Why not use a VCS like tool to versionned vfx data as it is done with code data?
https://github.com/roma-p/vit

### requirements and needs.

Requirements of the tool: 
	- a "micro pipe" designed to be used like a standard VCS but adapted to VFX versionning.
	- lightweight enough to be installed without beeing invasive
	(no third parties dependancies and so).
	- seized for small spare time project devlopped on multiple personnal computer.
Why not just use git then? Personnal purpouse was:
	- understanding git under the hood (the file pointer part at least, not the 'diff' part)
	- have a ideal standardized python package.
Extra requirements would be:
	- easy to poc / deploy (not a big time comitement)
	- as less complexity as possible (again not a big time comitement), so no BDD, JS web client
	  etc...

---------

-> What differnces between code versionning and asset versionning? 
What problem would we encounter if we used git form the get go?
From my understanding:
	- asset files are hard to merge. When they are not straight up binaries.
	  So a diff algo is pretty much useless.
	- since there is no merging, conflict will occur if two artists work on the same "asset"
	  at the same time.
	- because of the size of the projects, it is impossible for every artist to have a full
	  copy of the project. Need of a centralized repo to be the "single source of truth",
	  distributed architecture like GIT is therefore impossible.
	- When code versionning, the enterity of the code base can be versionned, tagged, branched
	  etc... When dealing with VFX it is every asset that is versionned. The code source
	  counterpart would be creating branch / tag for each code file.
	- The VCS needs features to maintain references between all those assets. (eg: commit X from
	  asset Y on branch Z as a reference of Tag A of Asset B)

-> But lots in common too:
	- artists still needs to work as a team on a standardized file architecture.
	- lots of the term used for their versionning can be re interpreted with traditionnal VCS
	  terms: variant -> branch / publish -> tag.
	- maintaning pointers to file sounds not that different from managing working copies.

-> Best way to do it: probably just leverage Git itself in a C libary, only using git to version the
file pointers and creating a SSH bash library on top of it. But since it is no fun...

### specs

Global specs ended up beeing:
	- a centralized VCS (like SVN, unlike GIT).
	- which maintain pointers to entire files (not diff of files).
	- which enforces exclusive checkout to avoid conflicts.
	- Vit defines (at the moment), two concepts:
		- Asset: a vfx asset, either a image, a 3d scene, a comp scene, a sequence of images, a
	  	geocache etc... 
		- Package: a package is either (1) a collection of asset, (2) a collection of package, (3)
	  	a mix of package / asset. Just see it as a directory. 
	- Assets offers the following versionning features: 
		- commit
		- rebase from previous commit
		- branch
		- tag: lightweight, annotated and auto versionned (a annotated tag which
		  automatically increment major/minor/patch by branch).
	- Packages can't be versionned at the moment (for the sake of simplicity).

--> reference between assets not implemented yet. (no need at the moment, only doing mod).

### feature overview with examples.

installation of vit.

-> repo configuration: vit init. / vit clone. 

-> asset creation: template / package / asset.
	- create a template for modelisation.
	- create a asset by "task": one asset for mod, another one for rigg.

-> asset versionning: checkout / branch / commit / tag / rebase
	 - checkout mod base branch.
	 - create a new branch "low_poly" and add '-t'
	 - try to commit it without / with changes.
	 - update it as editable.
	 - commit it and keep it. 
	 - checkout the previous commit.
	 - add a auto tag.

-> working copies management: info / log / clean.  

### under the hood.

-> path to file: no info store in them.
-> tracked index.

### repo structure and code snippet.

-> "buisness code" in vit_lib
-> vit_lib leverages file_handlers and connection module. 
-> command_line_lib leverages vit_lib only. 
(if GUI, only import vit_lib)

process in every vit_lib API func is: 



-> lock and connect to server
	-> get .vit metatata
		-> parse / update / write those metatata
		-> upload metatata
	-> upload versionned file.
-> unlock 
	-> download versionned file. 

