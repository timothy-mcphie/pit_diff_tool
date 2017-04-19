import os
from pit_diff import cmd, diff

#repo = "/Users/tim/Code/commons-collections"
#report_dir = "/Users/tim/Code/pitReports/cc4"
#numreports = 810

repo = "/Users/tim/Code/joda-time"
report_dir = "/Users/tim/Code/pitReports/joda"
numreports = 265
commit = "HEAD"

count = failed = passed = 0
while True:
    commit = cmd.get_commit_hash(repo, commit)
    if commit is None:
        print "No more commits left"
    report = report_dir+"/"+commit+".xml"
    if os.path.isfile(report):
        count += 1
        try:
            mut_dict = diff.process_report(report)
            passed += 1
            print "processed report ", passed
        except:
            failed += 1
            print "failed to process report ", failed
        if count >= numreports:
            break
    commit = cmd.get_commit_hash(repo, commit+"^")
