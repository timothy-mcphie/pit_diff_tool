import sys
import os
import csv
from pit_diff import cmd, diff, git_diff, scores as s

def display_score(name, mutation_score, mutants):
    if mutation_score.total_changed() > 0:
        print "In ", name, " files: "
        print mutation_score.str_changed()
    mutants = [m for m in mutants if m.get_index() < 3] # timed_out, survived, killed
    if mutants:
        print "MUTANTS CHANGED"
        for mutant in mutants:
                print str(mutant)

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
if not modmutants and not unmodmutants:
    print "No preexisting mutants had their status changed"
else:
    print "Mutation testing results"
    display_score("MODIFIED", modified, modmutants)
    display_score("UNMODIFIED", unmodified, unmodmutants)
