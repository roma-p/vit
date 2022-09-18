import time
from vit.vit_lib.misc import tree_fetch
from vit.file_handlers.tree_asset import TreeAsset
from vit.connection.vit_connection import ssh_connect_auto

# -- BASIC DRAW FUNCTIONS --

def draw_tree_basic(branch_number):
    return "| "*branch_number


def draw_tree_star(branch_number, branch_id, char="*"):
    line = "| "
    line_n_left  = branch_id
    line_n_right = branch_number - branch_id - 1
    return line * line_n_left + char + " " + line * line_n_right


def draw_tree_push_left(branch_number, branch_id):
    line_n_left = branch_id
    line_n_right = branch_number - branch_id - 1
    return "| " * line_n_left + "|/ " + "/ " * line_n_right


def draw_tree_split_left(branch_number, branch_id):
    line_n_left = branch_id
    line_n_right = branch_number - branch_id - 1
    line = "| "
    return line * line_n_left + "|/" + line * line_n_right


# -- DRAW EVENTS --

def draw_commit(
        branch_number, branch_id,
        date, user, commit_mess):
    formatted_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(date))
    lines = []
    lines.append(draw_tree_star(branch_number, branch_id) + " " + commit_mess)
    lines.append(draw_tree_basic(branch_number) + " " + user + ": " + formatted_date)
    lines.append(draw_tree_basic(branch_number))
    return lines

def draw_branching(branch_number, *branches):

    br_root = min(branches)
    br_children  = sorted([b for b in branches if b != br_root], reverse=True)

    lines = list()

    #lines.append(draw_tree_basic(branch_number))

    split_idx = br_children[0] - 1

    for i in range(len(br_children)):

        br_0 = br_children[i]

        if i+1 < len(br_children):
            br_1 = br_children[i+1]
        else:
            br_1 = None

        if br_1 is not None:
            split_to_draw = br_0 - br_1
        else:
            split_to_draw = br_0 - br_root

        if br_0 + 1 <  branch_number:
            lines.append(draw_tree_push_left(branch_number - (i+1), split_idx))
            split_idx = split_idx - 1
            split_to_draw = split_to_draw - 1

        for j in range(split_to_draw):
            lines.append(draw_tree_split_left(branch_number - (i+1), split_idx))
            split_idx = split_idx - 1

    #lines.append(draw_tree_basic(branch_number - len(branches)+1))
    return lines


def test_draw_branching_new():
    def print_list(list_to_print):
        for l in list_to_print: print(l)
    print_list(draw_branching(5, 1, 0, 3))
    print("")
    print_list(draw_branching(4, 1, 0, 3))
    print("")
    print_list(draw_branching(7, 0, 1,  4))
    print("")
    print_list(draw_branching(6, 3, 5, 4))
    print("")
    print_list(draw_branching(7, 0, 1, 2, 5))
    print("")
    print_list(draw_branching(4, 0, 1, 2, 3))
    print("")
    print_list(draw_branching(7, 1, 2, 4, 6))
#test_draw_branching_new()

def draw_tip_of_branch(branch_number, branch_id, branch_name):
    return [
        draw_tree_star(branch_number, branch_id, "O") + " " + branch_name.upper(),
        draw_tree_basic(branch_number)
    ]

# -- DRAW GRAPH --

def get_tree_data(local_path, package_path, asset_name):
    with ssh_connect_auto(local_path) as ssh_connection:
        tree_asset, tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
            ssh_connection, local_path,
            package_path,asset_name
        )
        with tree_asset:
            tree_data = tree_asset.data
    return tree_data

# BUG: if branch but not commit afterward.

def __gen_graph_data(local_path, package_path, asset_name):

    lines = list()

    tree_data = get_tree_data(local_path, package_path, asset_name)
    tree_commits = tree_data["commits"]
    tree_branchs = tree_data["branches"]

    branch_draw_index = {}
    _branch_start_draw = []
    branch_next_commit = {}

    for branch, commit in tree_branchs.items():
        branch_next_commit[branch] = commit
        _branch_start_draw.append((branch, tree_commits[commit]["date"]),)
    branch_start_draw = iter(sorted(_branch_start_draw, key=lambda x:x[1], reverse=True))

    first_branch, first_branch_date = next(branch_start_draw)
    branch_draw_index[first_branch] = 0
    current_date = first_branch_date + 1
    treated_branch = list()

    def get_next_branch():
        nonlocal next_branch
        nonlocal next_branch_date
        nonlocal branch_start_draw

        while True:
            try:
                next_branch, next_branch_date = next(branch_start_draw)
            except StopIteration:
                next_branch, next_branch_date = None, None
                break
            if next_branch not in treated_branch:
                break

    try:
        next_branch, next_branch_date = next(branch_start_draw)
    except StopIteration:
        next_branch, next_branch_date = None, None
    lines += draw_tip_of_branch(1, 0, first_branch)
    while True:

        # figuring out which branch to draw.
        branch_to_draw = None
        bigger_date = None
        for branch in branch_draw_index:
            commit = branch_next_commit[branch]
            if bigger_date is None or tree_commits[commit]["date"] > bigger_date:
                bigger_date = tree_commits[commit]["date"]
                branch_to_draw = branch

        # if new branch to draw, register it.
        if next_branch and next_branch_date > bigger_date:
            bigger_date = next_branch_date
            branch_to_draw = next_branch
            branch_idx = max(branch_draw_index.values())+1
            branch_draw_index[next_branch] = branch_idx
            lines += draw_tip_of_branch(len(branch_draw_index), branch_idx, branch_to_draw)
            get_next_branch()

        # getting commit to draw and updating next commit.
        commit = branch_next_commit[branch_to_draw]
        commit_data = tree_commits[commit]

        # drawing commit.
        lines += draw_commit(
            len(branch_draw_index),
            branch_draw_index[branch_to_draw],
            commit_data["date"],
            commit_data["user"],
            commit_data["message"]
        )

        next_commit = commit_data["parent"]

        # checking if there is a branch to fold.
        branches_on_commit = list()
        for branch, commit in branch_next_commit.items():
            if commit == next_commit:
                branches_on_commit.append(branch)

        # folding branch
        if len(branches_on_commit) > 1:

            branches_idx = []

            for branch in branches_on_commit:
                # dealing with branch not register yet (aka: no commit after branching)
                if branch not in branch_draw_index:
                    add_branch_to_draw_index(branch)
                    next_branch, next_branch_date = get_next_branch()
                    lines += draw_tip_of_branch(
                        len(branch_draw_index),
                        branch_draw_index[branch],
                        branch
                    )
                branches_idx.append(branch_draw_index[branch])

            lines += draw_branching(len(branch_draw_index), *branches_idx)

            branch_root = min(branches_on_commit)
            for branch in branches_on_commit:
                if branch != branch_root:
                    branch_draw_index.pop(branch)
            for branch in branch_draw_index.keys():
                if branch != branch_root:
                    branch_draw_index[branch] = branch_draw_index[branch] - 1
            branch_next_commit[branch_root] = next_commit

        # updating branch next commit.
        branch_next_commit[branch_to_draw] = next_commit
        if branch_next_commit[branch_to_draw] is None:
            break
        # TODO: O head of branch. o tag. x/-- for rebase? or overwriting branch?
    lines.append(draw_tree_star(1, 0, "X"))
    return lines


def _gen_graph_data(local_path, package_path, asset_name):

    lines = list()

    tree_data = get_tree_data(local_path, package_path, asset_name)
    tree_commits = tree_data["commits"]
    tree_branchs = tree_data["branches"]

    branch_draw_index = {}
    _branch_start_draw = []
    branch_next_commit = {}

    for branch, commit in tree_branchs.items():
        branch_next_commit[branch] = commit
        _branch_start_draw.append((branch, tree_commits[commit]["date"]),)
    branch_start_draw = iter(sorted(_branch_start_draw, key=lambda x:x[1], reverse=True))

    first_branch, first_branch_date = next(branch_start_draw)
    branch_draw_index[first_branch] = 0
    current_date = first_branch_date + 1
    treated_branch = list()

    def get_next_branch():
        nonlocal next_branch
        nonlocal next_branch_date
        nonlocal branch_start_draw

        while True:
            try:
                next_branch, next_branch_date = next(branch_start_draw)
            except StopIteration:
                next_branch, next_branch_date = None, None
                break
            if next_branch not in treated_branch:
                break

    try:
        next_branch, next_branch_date = next(branch_start_draw)
    except StopIteration:
        next_branch, next_branch_date = None, None
    lines += draw_tip_of_branch(1, 0, first_branch)
    while True:

        # figuring out which branch to draw.
        branch_to_draw = None
        bigger_date = None
        for branch in branch_draw_index:
            commit = branch_next_commit[branch]
            if bigger_date is None or tree_commits[commit]["date"] > bigger_date:
                bigger_date = tree_commits[commit]["date"]
                branch_to_draw = branch

        # if new branch to draw, register it.
        if next_branch and next_branch_date > bigger_date:
            bigger_date = next_branch_date
            branch_to_draw = next_branch
            branch_idx = max(branch_draw_index.values())+1
            branch_draw_index[next_branch] = branch_idx
            lines += draw_tip_of_branch(len(branch_draw_index), branch_idx, branch_to_draw)
            get_next_branch()

        # getting commit to draw and updating next commit.
        commit = branch_next_commit[branch_to_draw]
        commit_data = tree_commits[commit]

        # drawing commit.
        lines += draw_commit(
            len(branch_draw_index),
            branch_draw_index[branch_to_draw],
            commit_data["date"],
            commit_data["user"],
            commit_data["message"]
        )

        next_commit = commit_data["parent"]

        # checking if there is a branch to fold.
        branch_to_root = None
        for branch, commit in branch_next_commit.items():
            if commit == next_commit:
                branch_to_root = branch

        # folding branch
        if branch_to_root is not None:

            #if branch to root is not yet register (aka: no commit yet)
            if branch_to_root not in branch_draw_index:
                branch_number = len(branch_draw_index)
                lines += draw_tip_of_branch(
                   branch_number + 1,
                   branch_number,
                   branch_to_root
                )
                #lines += draw_tree_basic(branch_number+1)
                branch_draw_index[branch_to_root] = branch_number
                treated_branch.append(branch_to_root)
                get_next_branch()

            branch_to_draw_id = branch_draw_index[branch_to_draw]
            branch_to_root_id = branch_draw_index[branch_to_root]
            lines += draw_branching(
                len(branch_draw_index),
                branch_to_draw_id,
                branch_to_root_id
            )
            if branch_to_draw_id > branch_to_root_id:
                branch_to_remove = branch_to_draw
            else:
                branch_to_remove = branch_to_root

            branch_to_remove_id = branch_draw_index[branch_to_remove]
            branch_draw_index.pop(branch_to_remove)

            for branch, index in branch_draw_index.items():
                if index > branch_to_remove_id:
                    branch_draw_index[branch] = index - 1
            #branch_next_commit[branch_to_root

        # updating branch next commit.
        branch_next_commit[branch_to_draw] = next_commit
        if branch_next_commit[branch_to_draw] is None:
            break
        # TODO: O head of branch. o tag. x/-- for rebase? or overwriting branch?
    lines.append(draw_tree_star(1, 0, "X"))
    return lines


def gen_graph_data(local_path, package_path, asset_name):

    lines = list()

    tree_data = get_tree_data(local_path, package_path, asset_name)
    tree_commits = tree_data["commits"]
    tree_branchs = tree_data["branches"]

    branch_tip_commit = {
        branch: tree_data["commits"][commit]["date"]
        for branch, commit in tree_branchs.items()
    }

    branch_draw_index = {}
    branch_next_commit = {k:v for k, v in tree_branchs.items()}
    branch_treated = set()

    def get_next_branch():
        nonlocal branch_tip_commit
        ret = None, None
        max_date = None
        for branch, date in branch_tip_commit.items():
            if not max_date  or date > max_date and branch not in branch_treated:
                ret = branch, date
        if ret != (None, None):
            branch_tip_commit.pop(branch)
        return ret

    def add_branch_to_draw_index(branch):
        nonlocal branch_treated
        nonlocal branch_draw_index
        indexes = branch_draw_index.values()
        if not len(indexes):
            idx = 0
        else:
            idx = max(branch_draw_index.values()) + 1
        branch_draw_index[branch] = idx
        branch_treated.add(branch)

    def get_branching_from_commit(commit):
        branches_on_commit = set()
        for branch, _commit in branch_next_commit.items():
            if commit == _commit:
                branches_on_commit.add(branch)
        return branches_on_commit

    def get_branch_to_draw_within_registered_branches():
        branch_to_draw = None
        branch_to_draw_date = None
        for branch in branch_draw_index:
            commit = branch_next_commit[branch]
            date = tree_commits[commit]["date"]
            if (branch_to_draw_date is None or date > branch_to_draw_date):
                branch_to_draw_date = date
                branch_to_draw = branch
        return branch_to_draw, branch_to_draw_date

    first_branch, _ = get_next_branch()
    add_branch_to_draw_index(first_branch)

    next_branch, next_branch_date = get_next_branch()

    lines += draw_tip_of_branch(1, 0, first_branch)

    while True:

        # figuring out which branwh to draw.
        branch_to_draw, date = get_branch_to_draw_within_registered_branches()

        # handling: branch to draw is next branch.
        if next_branch and next_branch_date > date:
            branch_to_draw = next_branch
            date = next_branch_date
            add_branch_to_draw_index(next_branch)
            next_branch, next_branch_date = get_next_branch()
            lines += draw_tip_of_branch(
                len(branch_draw_index),
                branch_draw_index[branch_to_draw],
                branch_to_draw
            )

        # brawning commit. 
        commit = branch_next_commit[branch_to_draw]
        commit_data = tree_commits[commit]
        lines += draw_commit(
            len(branch_draw_index),
            branch_draw_index[branch_to_draw],
            commit_data["date"],
            commit_data["user"],
            commit_data["message"]
        )

        # getting next commit and checking if requires folding.
        next_commit = commit_data["parent"]
        branch_next_commit[branch_to_draw] = next_commit


        # checking if folding branching needed, draw folding.
        branches_on_commit = get_branching_from_commit(next_commit)
        if len(branches_on_commit) > 1:

            branches_idx = []

            for branch in branches_on_commit:
                # dealing with branch not register yet (aka: no commit after branching)
                if branch not in branch_draw_index:
                    add_branch_to_draw_index(branch)
                    next_branch, next_branch_date = get_next_branch()
                    lines += draw_tip_of_branch(
                        len(branch_draw_index),
                        branch_draw_index[branch],
                        branch
                    )
                branches_idx.append(branch_draw_index[branch])

            lines += draw_branching(len(branch_draw_index), *branches_idx)

            branch_root = None
            min_root_id = None
            for b in branches_on_commit:
                b_id = branch_draw_index[b]
                if branch_root is None or b_id < min_root_id:
                    branch_root = b
                    min_root_id = b_id

            for b in branches_on_commit:
                if b != branch_root:
                    branch_draw_index.pop(b)
            for b in branch_draw_index.keys():
                if b != branch_root:
                    branch_draw_index[b] = branch_draw_index[b] - 1

            branch_next_commit[branch_root] = next_commit
        if branch_next_commit[branch_to_draw] is None:
            break
    lines.append(draw_tree_star(1, 0, "X"))

    return lines

def test_draw():

    print("------------------------")
    print(draw_tree_basic(4))
    print(draw_tree_star(4, 0))
    print(draw_tree_star(4, 1))
    print(draw_tree_star(4, 2))
    print(draw_tree_star(4, 3))
    print(draw_tree_push_left(3, 2))
    print(draw_tree_push_left(2, 0))
    print(draw_tree_basic(2))
    print(draw_tree_push_left(1, 0))
    print(draw_tree_basic(1))
    print("------------------------")
    for line in draw_branching(4, 1, 3):
        print(line)
    print("------------------------")
    for line in draw_branching(4, 0, 2):
        print(line)
    print("------------------------")
    for line in draw_branching(4, 0, 3):
        print(line)
    print("------------------------")
    for line in draw_branching(4, 0, 1):
        print(line)#
#test_draw()

