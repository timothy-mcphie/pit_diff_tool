import os
import fnmatch
import cmd
from unidiff import PatchSet
#TODO:use gitpython

def load_diff(commit1, commit2, repo):
    """
    Get a list of changed files between two commits
    """
    diff_file = str(commit1)+"diff"+str(commit2)
    cmd.run_cmd(["git", "-C", repo, "diff", commit1, commit2], diff_file)
    patchset = PatchSet.from_filename(diff_file)
    cmd.run_cmd(["rm", diff_file])
    return patchset

def process_git_info(commit1, commit2, repo):
    """
    Get a dictionary giving a mapping of lines in changed files to their original lines. commit1 is old, commit2 is new
    """
    patchset = load_diff(commit1, commit2, repo)
    modified_files = {}
    for patched_file in patchset:
        if not fnmatch.fnmatch(patched_file.source_file, "*.java"):
            #hardcoded java only compatability -> skip non src files
            continue
        elif patched_file.is_added_file:
            target_file = os.path.basename(patched_file.target_file)
            modified_files[target_file] = "ADDED"
            continue
        elif patched_file.is_removed_file:
            source_file = os.path.basename(patched_file.source_file)
            modified_files[source_file] = "REMOVED"
            continue
        target_to_source_dict = {}
        target_to_source_list = []
        target_file = os.path.basename(patched_file.target_file)
        source_file = os.path.basename(patched_file.source_file)
        for hunk in patched_file:
            for line in hunk.target_lines():
                target_to_source_dict[line.target_line_no] = line
            target_to_source_list.append(line)
        modified_files[target_file] = ((target_to_source_dict, target_to_source_list), source_file)
    return modified_files 
