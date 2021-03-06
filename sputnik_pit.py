import sys
import os
import csv
from pit_diff import cmd, diff, git_diff, scores as s

def display_score(name, mutation_score):
    if mutation_score.total_changed() > 0:
        print "                    CURRENT STATUS"
        print "FORMER STATUS | no_coverage | survived | killed"
        print "================================================"
        print mutation_score.str_changed()

#repo is directory that jenkins is already in.
repo = os.getcwd()
report_dir = repo#repo is not cleaned of all files
pit_filter = str(sys.argv[1])
old_commit = cmd.get_commit_hash("HEAD")
new_commit = cmd.get_commit_hash("HEAD^")
lib_dir = "/opt/sputnik/pit_diff_tool/lib"
if old_commit is None:
    print "No previous history available to compare, exiting"
    sys.exit(0)
new_report = cmd.get_pit_report(repo, new_commit, report_dir, pit_filter, lib_dir)
old_report = cmd.get_pit_report(repo, old_commit, report_dir, pit_filter, lib_dir)
modified_files = git_diff.process_git_info(old_commit, new_commit, repo)
report_score = diff.get_pit_diff(old_commit, new_commit, repo, old_report, new_report, modified_files)
(modified, unmodified) = diff.parse_file_score(report_score)
(modmutants, unmodmutants) = diff.parse_changed_mutants(report_score)
print "====================================\nPITEST MUTATION TESTING DIFF RESULTS\n===================================="
print "SUMMARY\n=======\nMUTATION_SCORE"
print report_score.overall, "killed/total mutants" 
print "NEW SURVIVED\n======="
if report_score.new.survived:
    print report_score.new.survived, " were new and survived"
display_score(report_score)
print "In MODIFIED files:\n ==================\n" 
if not modmutants:
    print "There were no mutants whose status changed as a result of this patchset."
else:
    print "MUTANTS CHANGED"
    print " The following mutants statuses changed as a result of this patchset:"
    for mutant in modmutants:
        print str(mutant)
print "In UNMODIFIED files:\n ==================\n" 
if not unmodmutants:
    print "There were no mutants whose status changed as a result of this patchset."
else:
    print "MUTANTS CHANGED"
    print " The following mutants statuses changed as a result of this patchset:"
    for mutant in unmodmutants:
        print str(mutant)
