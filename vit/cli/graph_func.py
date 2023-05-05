import time

# -- BASIC DRAW FUNCTIONS -----------------------------------------------------

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

# -- DRAW EVENTS --------------------------------------------------------------

def draw_commit(branch_number, branch_id, commit_id, date, user, mess):
    formatted_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(date))
    lines = []
    lines.append(draw_tree_star(branch_number, branch_id)+ " "+commit_id)
    lines.append(draw_tree_basic(branch_number) + " " + user + " at " + formatted_date)
    lines.append(draw_tree_basic(branch_number) + "    " + mess)
    lines.append(draw_tree_basic(branch_number))
    return lines


def draw_tag(branch_number, branch_id, commit_id, date, user, mess, *tags):
    formatted_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(date))
    lines = []

    tag_line = "TAG: "
    for tag in tags:
        tag_line += tag + ", "
    tag_line = tag_line[:-2]

    lines.append(draw_tree_star(branch_number, branch_id, "o") + " "+tag_line)
    lines.append(draw_tree_basic(branch_number) + " "+commit_id)
    lines.append(draw_tree_basic(branch_number) + " " + user + " at " + formatted_date)
    lines.append(draw_tree_basic(branch_number) + "    " + mess)
    lines.append(draw_tree_basic(branch_number))
    return lines


def draw_branching(branch_number, *branches):

    br_root = min(branches)
    br_children  = sorted([b for b in branches if b != br_root], reverse=True)

    lines = list()

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
    return lines


def draw_tip_of_branch(branch_number, branch_id, branch_name):
    return [
        draw_tree_star(branch_number, branch_id, "O") + " BRANCH " + branch_name,
        draw_tree_basic(branch_number)
    ]
