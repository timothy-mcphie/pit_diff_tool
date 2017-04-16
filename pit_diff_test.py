import sys
import os
import csv
from pit_diff import cmd, diff, git_diff, scores as s

repo = "/Users/tim/Code/commons-collections"
report_dir = "/Users/tim/Code/pitReports/cc4"
old_commit = "930015a137f6bc34127d7646b36d0550842fedfb"
new_commit = "ff4f018553ac76f48e0f832e996812e95eae5cdd"
modified_files = git_diff.process_git_info(old_commit, new_commit, repo)
old_report = report_dir+"/"+old_commit+".xml"
new_report = report_dir+"/"+new_commit+".xml"
delta = diff.get_pit_diff(old_commit, new_commit, repo, old_report, new_report, modified_files)
print delta.str_changed()
(modified, unmodified) = diff.parse_changed_mutants(delta, True)
print "MODIFIED"
for changed in modified:
    print str(changed)
print "UNMODIFIED"
for changed in unmodified:
    print str(changed)

