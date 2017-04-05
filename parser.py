import sys
from unidiff import PatchSet
from subprocess import call
#TODO:use gitpython

def load_diff(commit1, commit2):
    """
    Get a list of changed files between two commits
    """
    #TODO:Make this work outside of the repo directory
    diff_file_path = str(commit1)+"diff"+str(commit2)
    fd = open(diff_file_path, "w")#might need wb instead - write in binary
    try:
        status = call(["git", "diff", commit1, commit2], stdout=fd)
        if status != 0:
            print sys.stderr, "Call to git diff terminated", status
        else:
            print sys.stderr, "Call to git diff successful", status
    except OSError as e:
        print sys.stderr, "Failed to call git diff", e
        sys.exit(1) 
    fd.close()
    patchset = PatchSet.from_filename(diff_file_path)#TODO: already have file descriptor - speed up available here?
    #TODO:rm diff file
    return patchset

def process_git_info(commit1, commit2):
    """
    Get a dictionary giving a mapping of lines in changed files to their original lines. commit1 is old, commit2 is new
    """
    patchset = load_diff(commit1, commit2)
    modified_files = {}
    for patched_file in patchset:
        if patched_file.is_added_file or patched_file.is_removed_file:
            continue
        target_to_source_dict = {}
        target_to_source_list = []
        for hunk in patched_file:
            for line in hunk.target_lines():
                target_to_source_dict[line.target_line_no] = line.source_line_no 
            target_to_source_list.append(line)
        modified_files[patched_file.source_file] = (target_to_source_dict, target_to_source_list)
    return modified_files

def update_mutant(mutant, modified_files):
    """
    Update a mutant in the new report to have the correct line numbers by parsing the hunks in it's patchedfile
    an old_line_no is the new_line_no - (number of lines added < new_line_no) + (number of lines deleted < new_line_no)
    """
    source_file = mutant.source_file
    if source_file not in modified_files:
        return
    target_to_source_dict, target_to_source_list = modified_files[source_file]
    if mutant.line_no in target_to_source_dict:
        mutant.line_no = target_to_source_dict[mutant.line_no] #If it is a new mutant it is updated to None and will be included in the delta (no original mutant has None in its key)
        return
    iterator = iter(target_to_source_list)
    line = iterator.next()
    while mutant.line_no > line.target_line_no:
        try:
            next_line = iterator.next()
            if mutant.line_no < next_line.target_line_no:
                break 
            line = next_line
        except:
            break 
    mutant.line_no = mutant.line_no + (line.source_line_no - line.target_line_no) 

