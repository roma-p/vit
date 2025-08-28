
---

# 25/08/21

transaction add reccurive path
on commence par lock le plus haut repertoire (le seul existant).
et on descend. On doit pouvoir delock les deux.


---

# 23/08/21

next -> 
- [ ] add cli "path"
- [ ] add cmd
- [ ] transaction create file.

une fois ça fait, revoir pr rajouter des tests, piger mieux comment fonctionne gestionnaire ctx.

vit add?

vit add <path_to_file>  et pas de src_file
    -> if not in repo dir: erreur
    -> if file or dir exists: add and create a _bk_copy
    -> if file or dir exists: not exists: create empty (add -r for reportory)
vit add <path_to_file> <src>
    -> if in / out identical simiar to vit add and exists.
    -> otherwise juste create a copy, wherever it belongs to repo or not.

start with empty: 
vit add path/to/my/asset
(and does not exist)

add asset atomique?

--> fr un registre de trash des fichiers à clean. pr savoir quel ficheir sont à clean en cas 
    d'échec d'une transaction. and uplaoded unused file for quick retry of operation
    so no need to redownload stuff.

-> 1. copy du fichier (pas de lock necessaire? avec un morceau de code gen ca ira.)
-> 2. register de l'UID dans la partie 'asset' (et lock de cette partie là).
-> 3. partie de la transition atomique.
-> if package exists 
--> .lock ce package fr l'update.
-> if package does nnot exists 
--> trouver le dernier package qui existe et l'editer en dernier.
--> creer de bas en haut les tree-index. (mais créer les locks?)
--> lock le dernier existant, fr la modif et on a tout.

plus ou moins ok, mais il manque la partie "transactions".

bon un index "curr-transaction" pr éviter les conflits.
peut être aussi un historic globale de toute les transaction par date.
pour savoir qui a fait quoi par date. (et future grosse transaction)

transction object: 
{
    asset_path:
    operation: "add"
    time: ...
    user: ...
    asset_size: ...
}

pas besoin de, lock file sur les transaction: c'est un lock file en soit!
Non pas vraiment car je vais qd même le lire pr parser les données!

transaction fantôme, ou lock file fantome? doive être touch toute les 10sec.
par le processus parent, dc si on essaye d'add une transaction plus vieille de 10 sec. 
alors fantôme est osef on détruit le fichier.

Processus de transaction?

1/ if exists: -> safe read / print errors
2/ if not exists create it.

3/ on "add" -> (but maybe anytime), vit delete failed transaction. Or move it to "failed"?
  because a failed transaction has a transaction manifest not touch since 30 sec.


---

# 21/08/21

next: 

- [x] setup of test with test files (file existence)
- [x] .vit path resolution from arbitrary path
- [ ] nodePath creation on disk.
