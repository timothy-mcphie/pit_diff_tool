import sys
import os
import csv
from pit_diff import cmd, diff, git_diff, scores as s

def output_score():
    with open("PIT_WORKED.TXT", "a+") as f:
        w = csv.writer(f, delimiter=",")
        w.writerow([1,2,3,4,5])
        w.writerow(pit_filter)

#repo is directory that jenkins is in
pit_filter = str(sys.argv[1])
print "we have ", pit_filter, " as pit_filter"
output_score()

#Sputnik script calls rev-parse HEAD^ - if fails no prev commits
#extract cp maven
#run pitest
#save mutation report as rev-parse HEAD in repo
#find HEAD^ report - if not found
#git checkout and build with mvn
#extract cp maven
#run pitest
#run git diff HEAD^
#save mutation report as rev-parse HEAD^ in repo
#git diff
#run pit_diff

#return via a pipe
