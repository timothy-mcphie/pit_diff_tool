"""
Main
#TODO: use the python arguments module
usage_string = "python parser.py old_report_path new_report_path repo_path old_commit [new_commit]"
if len(sys.argv) != 3 or sys.argv[2] < 1:
  print usage_string
  sys.exit(1)
old_rep = str(sys.argv[1])
new_rep = str(sys.argv[2])
repo_path = str(sys.argv[3])
old_commit = str(sys.argv[4])
new_commit = str(sys.argv[5]) #optional can just pass an old_commit to compare with current HEAD
"""


def parse_score(report_score):
    for file_score in score.children.keys():
        pass

