import sys
import os
import csv
from pit_diff import cmd, diff, git_diff, scores as s
#repo is directory that jenkins is already in.
repo = os.getcwd()
report_dir = repo
report_dir = repo#repo is not cleaned of all files
pit_filter = str(sys.argv[1])
new_commit = cmd.get_commit_hash("HEAD")
old_commit = cmd.get_commit_hash("HEAD^")
if old_commit is None:
    print "No previous history available to compare, exiting"
    sys.exit(0)
new_report = cmd.get_pit_report(repo, new_commit, report_dir, pit_filter, lib_dir)
old_report = cmd.get_pit_report(repo, old_commit, report_dir, pit_filter, lib_dir)
modified_files = git_diff.process_git_info(old_commit, new_commit, repo)
#run pit_diff 
report_score = diff.get_pit_diff(old_commit, new_commit, repo, old_report, new_report, modified_files)
(modified, unmodified) = diff.parse_report_score(report_score)
print "Mutation testing results"
print "In modified files: ", total_modified.str_changed(), " mutants"
print "In unmodified files have: ", total_unmodified.str_changed(), " mutants"
