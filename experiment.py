import sys
import os
import csv
from pit_diff import cmd, diff, git_diff, scores as s
#TODO: Use a logging function instead of prints - can ditch the [FNAME] tag - output status of cmds to file

def output_score(row, output_file):
    """
    Output and append to a csv file the change a new_commit introduces to the mutation score
    """
    #TODO: add headers to csv
    with open(output_file, "a+") as f:
        w = csv.writer(f, delimiter=",")
        for row in rows:
            w.writerow(row)

def main(repo, start_commit, end_commit, report_dir, pit_filter, output_file):
    """
    Iterate backwards over commits in a repo running pit
    """ 
    start_commit = cmd.get_commit_hash(repo, start_commit) 
    new_report = report_dir+"/"+start_commit+".xml" 
    new_commit = old_commit = start_commit
    missing_reps = 0
    fdc = 0
    reports = 1
    total_parsed = 0
    rows = []
    total_modified = s.Mutation_score("total_modified", None)
    total_unmodified = s.Mutation_score("total_unmodified", None) 
    while True:
        if reports >= 810:
                break
        old_commit = cmd.get_commit_hash(repo, old_commit+"^")
        if old_commit is None or old_commit == end_commit:
            print "[PIT_EXP] End of commit history, exiting"
            break
        try:
            modified_files = git_diff.process_git_info(old_commit, new_commit, repo)
        except:
            fdc += 1
            print "Couldn't parse diff"
            new_commit = old_commit
            continue
        if fdc > 1:
            print "[PIT_EXP] parsed git diff successfully after ", fdc, " failed diffs in a row - missing those reports"
        fdc = 0
        old_report = report_dir+"/"+old_commit+".xml" 
        if not os.path.isfile(old_report):
            print "[PIT_EXP] no file exists ", old_commit
            missing_reps += 1
            continue
        else:
            reports += 1
        if missing_reps > 0:
            print "gap between reports was ", missing_reps
        missing_reps = 0
        report_score = diff.get_pit_diff(old_commit, new_commit, repo, old_report, new_report, modified_files)
        (modified, unmodified) = diff.parse_file_score(report_score)
        (modified_class, unmodified_class, modified_method, unmodified_method) = diff.parse_class_method_score(report_score)
        print "[PIT_EXP] pit diffed successfuly ", old_commit, " to ", new_commit, " there were ", report_score.total_changed(), " changes"
        rows.append([new_commit, len(modified_files)]+modified.changed+unmodified.changed+modified_class.changed+unmodified_class.changed+modified_method.changed+unmodified_method.changed)
        total_parsed += 1
        new_report = old_report
        new_commit = old_commit
    output_score([new_commit, len(modified_files)]+modified.changed+unmodified.changed, output_file)
    print "Total parse ", total_parsed

repo = "/Users/tim/Code/commons-collections"
start_commit = "HEAD"
end_commit = "" 
report_dir = "/Users/tim/Code/pitReports/cc4"
output_file = "output.csv"
main(repo, start_commit, end_commit, report_dir, None, output_file)
