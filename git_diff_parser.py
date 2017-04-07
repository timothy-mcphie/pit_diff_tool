import sys
import fnmatch
from unidiff import PatchSet
from subprocess import call
#TODO:use gitpython

def run_cmd(cmd_arr, stdout=None):
    """
    Helper function for running shell commands
    """
    fd = None
    if stdout is not None:
        fd = open(stdout, "w")#might need wb instead - write in binary
    try:
        status = call(cmd_arr, stdout=fd)
        if status != 0:
            print sys.stderr, "Call to ", str(cmd_arr), "terminated with non zero exit code", status
        else:
            print sys.stderr, "Call to ", str(cmd_arr), "successful", status
    except OSError as e:
        print sys.stderr, "Failed to call ", str(cmd_arr), "successfully", e
        print sys.stderr, "EXITING"
        sys.exit(1)
    if fd is not None:
        fd.close() 
    return status

def load_diff(commit1, commit2, repo_path):
    """
    Get a list of changed files between two commits
    """
    diff_file = str(commit1)+"diff"+str(commit2)
    run_cmd(["git", "-C", repo_path, "diff", commit1, commit2], diff_file)
    patchset = PatchSet.from_filename(diff_file)
    run_cmd(["rm", diff_file])
    return patchset

def process_git_info(commit1, commit2, repo_path):
    """
    Get a dictionary giving a mapping of lines in changed files to their original lines. commit1 is old, commit2 is new
    """
    patchset = load_diff(commit1, commit2, repo_path)
    modified_files = {}
    for patched_file in patchset:
        if patched_file.is_added_file or patched_file.is_removed_file or not fnmatch.fnmatch(patched_file.source_file, "*.java"):#hardcoded java only compatability
            continue
        target_to_source_dict = {}
        target_to_source_list = []
        for hunk in patched_file:
            for line in hunk.target_lines():
                target_to_source_dict[line.target_line_no] = line
            target_to_source_list.append(line)
        modified_files[patched_file.source_file] = (target_to_source_dict, target_to_source_list)
    return modified_files 
