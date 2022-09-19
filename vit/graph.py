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

    # parsing commits a first time to get branching.
    _commits = {}
    branching_commits = {}
    branching_commits_drawn = {}

    for commit, commit_data in tree_commits.items():
        parent_commit = commit_data["parent"]
        if parent_commit not in _commits:
            _commits[parent_commit] = 1
        else:
            _commits[parent_commit] += 1
    for commit in tree_branchs.values():
        if commit in _commits:
            _commits[commit] += 1
    for commit, number_of_children in _commits.items():
        if number_of_children > 1:
            branching_commits[commit] = number_of_children

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

        # drawning commit. 
        commit = branch_next_commit[branch_to_draw]
        commit_data = tree_commits[commit]
        commit_draw_index = branch_draw_index[branch_to_draw]
        next_commit = commit_data["parent"]

        # checking if it is a branching commit / if so, checking if folding is required.
        draw_folding = False
        is_folding_commit = False

        if commit in branching_commits:
            is_folding_commit = True
            required_branch_on_commits = branching_commits[commit]
            if commit not in branching_commits_drawn:
                branching_commits_drawn[commit] = {branch_to_draw}
            else:
                branching_commits_drawn[commit].add(branch_to_draw)
            if len(branching_commits_drawn[commit]) == required_branch_on_commits:
                draw_folding = True

        if draw_folding:
            branches_on_commit = branching_commits_drawn[commit]
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

            # updating branch_draw_index.
            branch_root = None
            min_root_id = None

            # resloving which is the main branch and which are the branch to delete.
            for b in branches_on_commit:
                b_id = branch_draw_index[b]
                if branch_root is None or b_id < min_root_id:
                    branch_root = b
                    min_root_id = b_id
            branch_id_deleted = [br_id for br_id in branches_idx if br_id != min_root_id]
            for b in branches_on_commit:
                if b != branch_root:
                    branch_draw_index.pop(b)
            
            for b in branch_draw_index.keys():
                b_id = branch_draw_index[b]
                deleted_branch_before_b_number = len([
                    deleted_id for deleted_id in branch_id_deleted 
                    if deleted_id < b_id
                ])

                if b != branch_root:
                    branch_draw_index[b] = branch_draw_index[b] - deleted_branch_before_b_number 

            branch_next_commit[branch_root] = next_commit
            commit_draw_index = branch_draw_index[branch_root]

        if not is_folding_commit or draw_folding:
            lines += draw_commit(
                len(branch_draw_index),
                commit_draw_index,
                commit_data["date"],
                commit_data["user"],
                commit_data["message"]
            )


#       if is_folding_commit and not draw_folding:


        branch_next_commit[branch_to_draw] = next_commit

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
