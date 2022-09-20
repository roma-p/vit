from vit.command_line_lib import graph_func
from vit.vit_lib.misc import tree_fetch
from vit.connection.vit_connection import ssh_connect_auto

def main(local_path, package_path, asset_name):
    graph = Graph(local_path, package_path, asset_name)
    return graph.gen_graph()

class Graph(object):

    def __init__(self, local_path, package_path, asset_name):

        # init param
        self.local_path = local_path
        self.package_path = package_path
        self.asset_name = asset_name

        # parameters resolved from tree assets.
        self.tree_commits = {}          # commit id to commit data for every commits
        self.tree_branches = {}         # branch id to commit id for every branches.

        self.branch_tip_date = {}       # branch id to date of last commit
        self.branching_commits = {}     # commit id to number of branches branching from it.
        self.tag_index = {}             # commit to list of tags referencing this commit.

        # iterators maintained during graph generation.
        self.branch_draw_index = {}     # branch to row index where to draw branch on terminal.
        self.branch_treated = set()     # branch that already have been added to branch_draw_index
        self.branch_next_commit = {}    # branch to next commit to draw on terminal.
        self.branch_next_date = {}      # branch to date of the next commit to draw on terminal.
        self.branching_commits_rdy = {} # branching commits to set of branches rdy to draw branching.

        self.next_branch = None         # branch id to draw on next cycle.
        self.next_branch_date = None    # date of branch to draw on next cycle.

        self.lines = []

    def gen_graph(self):

        # fetch data from repo and init iterators and buff.
        self._get_tree_data()
        self._resolve_branching_commits()
        self._init_branch_next_date_and_branch_next_commit()

        # init first cycle of loop.
        self._update_next_branch()
        first_branch = self.next_branch
        self._add_branch_to_draw_index(first_branch)
        self.lines += graph_func.draw_tip_of_branch(1, 0, first_branch)
        self._update_next_branch()

        while True:

            # -- getting branch_to_draw.
            branch_to_draw, _ = self._get_branch_to_draw()
            if branch_to_draw not in self.branch_draw_index:
                self._handle_new_branch_and_draw(branch_to_draw)

            # -- getting commit info.
            commit = self.branch_next_commit[branch_to_draw]
            commit_data = self.tree_commits[commit]
            commit_draw_index = self.branch_draw_index[branch_to_draw]
            next_commit = commit_data["parent"]

            # -- checking if commit is branching commit.
            is_branching_commit = False
            is_branching_to_draw = False
            if commit in self.branching_commits:
                is_branching_commit = True
                self._update_branching_commits_drawn(commit, branch_to_draw)
            is_branching_to_draw = self._check_is_branching_to_draw(commit)

            # -- if so, dealing with it.
            if is_branching_to_draw:
                branches_on_commit = self.branching_commits_rdy[commit]
                branches_idx = []
                for branch in branches_on_commit:
                    if branch not in self.branch_draw_index:
                        self._handle_new_branch_and_draw(branch)
                    branches_idx.append(self.branch_draw_index[branch])
                self.lines += graph_func.draw_branching(
                    len(self.branch_draw_index),
                    *branches_idx
                )
                branch_root = self._update_draw_index_after_branching(*branches_on_commit)
                self.branch_next_commit[branch_root] = next_commit
                commit_draw_index = self.branch_draw_index[branch_root]

            # -- drawning commit or tag.
            if not is_branching_commit or is_branching_to_draw:
                if commit not in self.tag_index:
                    self.lines += graph_func.draw_commit(
                        len(self.branch_draw_index),
                        commit_draw_index, commit,
                        commit_data["date"],
                        commit_data["user"],
                        commit_data["message"]
                    )
                else:
                    self.lines += graph_func.draw_tag(
                        len(self.branch_draw_index),
                        commit_draw_index, commit,
                        commit_data["date"],
                        commit_data["user"],
                        commit_data["message"],
                        *self.tag_index[commit]
                    )

            self.branch_next_commit[branch_to_draw] = next_commit
            if self.branch_next_commit[branch_to_draw] is None:
                break

        self.lines.append(graph_func.draw_tree_star(1, 0, "X"))
        return self.lines

    def _get_tree_data(self):
        with ssh_connect_auto(self.local_path) as ssh_connection:
            tree_asset, tree_asset_path = tree_fetch.fetch_up_to_date_tree_asset(
                ssh_connection, self.local_path,
                self.package_path, self.asset_name)
            with tree_asset:
                tree_data = tree_asset.data
                self.tag_index = tree_asset.get_tag_to_origin_commit()
            self.tree_commits = tree_data["commits"]
            self.tree_branches = tree_data["branches"]

    def _resolve_branching_commits(self):
        _commits = {}
        for commit, commit_data in self.tree_commits.items():
            parent_commit = commit_data["parent"]
            if parent_commit not in _commits:
                _commits[parent_commit] = 1
            else:
                _commits[parent_commit] += 1
        for commit in self.tree_branches.values():
            if commit in _commits:
                _commits[commit] += 1
        for commit, number_of_children in _commits.items():
            if number_of_children > 1:
                self.branching_commits[commit] = number_of_children

    def _init_branch_next_date_and_branch_next_commit(self):
        for branch, commit in self.tree_branches.items():
            self.branch_next_commit[branch] = commit
            self.branch_next_date[branch] = self.tree_commits[commit]["date"]

    def _update_next_branch(self):
        next_branch = None
        max_date = None
        for branch, date in self.branch_next_date.items():
            if not next_branch  or date > max_date and branch not in self.branch_treated:
                next_branch = branch
                max_date = date
        if next_branch is not None:
            self.next_branch = next_branch
            self.next_branch_date = max_date
            self.branch_next_date.pop(next_branch)
        else:
            self.next_branch = None
            self.next_branch_date = None

    def _add_branch_to_draw_index(self, branch):
        indexes = self.branch_draw_index.values()
        if not len(indexes):
            idx = 0
        else:
            idx = max(indexes) + 1
        self.branch_draw_index[branch] = idx
        self.branch_treated.add(branch)

    def _get_branch_to_draw(self):
        branch_to_draw = None
        branch_to_draw_date = None

        # 1 / getting branch with upper date from already registered branches.
        for branch in self.branch_draw_index:
            commit = self.branch_next_commit[branch]
            date = self.tree_commits[commit]["date"]
            if (branch_to_draw_date is None or date > branch_to_draw_date):
                branch_to_draw_date = date
                branch_to_draw = branch

        # 2 / checking if branch in next_branch buffer has upper date.
        if self.next_branch and self.next_branch_date > date:
            branch_to_draw = self.next_branch
            branch_to_draw_date = self.next_branch_date

        return branch_to_draw, branch_to_draw_date

    def _update_branching_commits_drawn(self, commit, branch):
        if commit not in self.branching_commits:
            return
        if commit not in self.branching_commits_rdy:
            self.branching_commits_rdy[commit] = {branch}
        else:
            self.branching_commits_rdy[commit].add(branch)

    def _check_is_branching_to_draw(self, commit):
        if commit not in self.branching_commits:
            return False
        required_branch_on_commits = self.branching_commits[commit]
        if len(self.branching_commits_rdy[commit]) == required_branch_on_commits:
            return True
        else:
            return False

    def _handle_new_branch_and_draw(self, branch):
        self._add_branch_to_draw_index(branch)
        self._update_next_branch()
        self.lines += graph_func.draw_tip_of_branch(
            len(self.branch_draw_index),
            self.branch_draw_index[branch],
            branch
        )

    def _update_draw_index_after_branching(self, *branches):
        branch_root = None
        min_root_id = None

        # resloving which is the main branch and which are the branch to delete.
        branches_idx = []
        for b in branches:
            b_id = self.branch_draw_index[b]
            if branch_root is None or b_id < min_root_id:
                branch_root = b
                min_root_id = b_id
            branches_idx.append(b_id)
        branch_id_deleted = [br_id for br_id in branches_idx if br_id != min_root_id]

        # removing merged branches from index.
        for b in branches:
            if b != branch_root:
                self.branch_draw_index.pop(b)

        # updating index of remaining branhces.
        for b in self.branch_draw_index.keys():
            b_id = self.branch_draw_index[b]
            deleted_branch_before_b_number = len([
                deleted_id for deleted_id in branch_id_deleted
                if deleted_id < b_id
            ])
            if b != branch_root:
                self.branch_draw_index[b] = self.branch_draw_index[b] - deleted_branch_before_b_number
        return branch_root
