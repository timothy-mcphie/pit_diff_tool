import sys
import os
import csv
from pit_diff import cmd, diff, git_diff, scores as s

repo = "/Users/tim/Code/commons-collections"
report_dir = "/Users/tim/Code/pitReports/cc4"
modified_files = git_diff.process_git_info(old_commit, new_commit, repo)
new_commit = "5250fdfdf3720a96366cac57fd216e8fa6c13cce"
old_commit = "d684f950c4a29d10097590cbe4346ad6e82e5e25"
old_report = report_dir+"/"old_commit+".xml"
new_report = report_dir+"/"new_commit+".xml"
delta = diff.get_pit_diff(old_commit, new_commit, repo, old_report, new_report, modified_files)
