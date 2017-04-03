import sys
from unidiff import PatchSet
from subprocess import call
#TODO:use gitpython

def load_diff(commit1, commit2):
    diff_file_path = str(commit1)+" diff "+str(commit2)
    fd = open(diff_file_path, "w")#might need wb instead - write in binary
    try:
        status = call(["git", "diff", commit1, commit2], stdout=fd)
        #git diff is old commit, recent commit - to see what has been added in new commit
        if status != 0:
            print sys.stderr, "Call to git diff terminated", status
        else:
            #print sys.stderr, "Call to git diff successful", status
            pass
    except OSError as e:
        print sys.stderr, "Failed to call git diff", e
        sys.exit(1) 
    fd.close()
    #TODO: already have file descriptor - speed up available here?
    patchset = PatchSet.from_filename(diff_file_path)
    #rm diff information? - must return diff_file_path
    return patchset

def process_git_info(commit1, commit2):
    """
    commit1 is old, commit2 is new 
    """
    patchset = load_diff(commit1, commit2)

    patchset.removed
    files = {}
    for patchedfile in patchset:
        if patchedfile.is_added_file:
            #no modification of keys in new report needed - they will all be unique and new
            continue
        files[patchedfile.source_file] = [patchedfile] 
    #get a dictionary with each source file pointing to a list of their hunks
    return files
    #write a hunk parser in this module to update old source file linenos to their new ones.
    #idea is if an old line number is in a range - it has changed - count as introduction of new mutants - are can do direct comparison - or classify as new mutants
    #if an old line number is after the range of added or modified code - add to current lineno
    #if after a deletion of code - subtract from current lineno

#TODO: Remove this - testing purposes
process_git_info("HEAD^", "HEAD")
