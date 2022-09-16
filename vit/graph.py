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

# branching multiiiple branch.
# then redo the gaph algo from scractch...

def draw_branching(branch_number, branch_a, branch_b):
    branch_root  = min(branch_a, branch_b)
    branch_child = max(branch_a, branch_b)

    lines = []
    split_to_draw = branch_child - branch_root
    split_idx = branch_child - 1

    if branch_child + 1 <  branch_number:
        lines.append(draw_tree_push_left(branch_number - 1, split_idx))
        split_to_draw = split_to_draw - 1
        split_idx = split_idx - 1

    for i in range(split_to_draw):
        lines.append(draw_tree_split_left(branch_number - 1, split_idx))
        split_idx = split_idx - 1
    return lines


def draw_branching_new(branch_number, *branches):

    br_root = min(branches)
    br_children  = sorted([b for b in branches if b != br_root], reverse=True)

    lines = list()

    lines.append(draw_tree_basic(branch_number))

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

        #break
    #lines.append(draw_tree_basic(branch_number - len(branches)+1))
    return lines


def test_draw_branching_new():
    def print_list(list_to_print):
        for l in list_to_print: print(l)

    print_list(draw_branching_new(5, 1, 0, 3))
    print("")
    print_list(draw_branching_new(4, 1, 0, 3))
    print("")
    print_list(draw_branching_new(7, 0, 1,  4))
    print("")
    print_list(draw_branching_new(6, 3, 5, 4))
    print("")
    print_list(draw_branching_new(7, 0, 1, 2, 5))
    print("")
    print_list(draw_branching_new(4, 0, 1, 2, 3))
    print("")
    print_list(draw_branching_new(7, 1, 2, 4, 6))
    pass

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

def gen_graph_data(local_path, package_path, asset_name):

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

        # updating branch next commit.
        branch_next_commit[branch_to_draw] = next_commit
        if branch_next_commit[branch_to_draw] is None:
            break
        # TODO: O head of branch. o tag. x/-- for rebase? or overwriting branch?
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
        print(line)
#test_draw()


'''

| | | 
| * |
| | |

| | | |
|/ / /
| | |

| | |
| |  \
| |   |
| | O | BRANCH HIGH POLY
| | | |

| | | |
| | | *
| | | |
| | |/
| |/|
| * |
| | |

branch ended at last commit. (so with timing...)

'''

