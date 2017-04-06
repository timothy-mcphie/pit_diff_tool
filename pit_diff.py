import xml.etree.ElementTree as ET
import sys
import parser
import fnmatch
from mutation import Mutant, Mutation_score

def update_mutant(mutant, modified_files):
    """
    Update a mutant in the new report to have the correct line numbers by parsing the hunks in it's patchedfile
    an old_line_no is the new_line_no - (number of lines added < new_line_no) + (number of lines deleted < new_line_no)
    """
    source_file = mutant.source_file
    if source_file not in modified_files:
        return
    target_to_source_dict, target_to_source_list = modified_files[source_file]
    if mutant.line_no in target_to_source_dict:
        mutant.target_line_no = mutant.line_no
        mutant.line_no = target_to_source_dict[mutant.line_no].source_line_no 
        #A new mutant is updated to None, will be included in the delta (no original mutant has None in its key)
        return
    iterator = iter(target_to_source_list)
    line = iterator.next()
    while mutant.line_no > line.target_line_no:
        try:
            next_line = iterator.next()
            if mutant.line_no < next_line.target_line_no:
                break 
            line = next_line
        except StopIteration as e:
            print "Line is after all hunks, last hunk line:", line.target_line_no, " mutant line:", mutant.line_no
            break 
    mutant.target_line_no = mutant.line_no
    mutant.line_no = mutant.line_no + (line.source_line_no - line.target_line_no) 

def parse_report(filename):
    """
    Returns the root tag of an XML file
    """
    #TODO: Add error handling
    tree = ET.parse(filename)
    root = tree.getroot()
    return root

def process_report(report, commit, modified_files, report_score, new=False):
    """
    Traverses a pit XML report - returns a set of unique mutants and a score
    """
    mutant_set = {}
    root = parse_report(report) 
    for child in root:
        mutant = Mutant(child.attrib.get("detected"), child.attrib.get("status"), child[0].text, child[1].text, child[2].text, child[3].text, child[4].text, \
                child[5].text, child[6].text, child[7].text,  child[8].text)
        if new:
            update_mutant(mutant, modified_files) 
        if mutant not in mutant_set:
            mutant.add(mutant)
    return mutant_set

def get_differences(old_report, new_report, old_commit, new_commit):
    report_score = Report_score(old_commit+new_commit)
    #modified_files = parser.process_git_info("HEAD^", "HEAD", repo_path) 
    old_set = process_report(old_report, old_commit, modified_files)
    new_set = process_report(new_report, new_commit, modified_files, True)
    #TODO: Use sets, gives us easily the new mutants, deleted mutants, changed and unchanged
    for mutant in old_set.difference(new_set):
        report_score.update_removed(mutant)

    for mutant in mutant_list:
        key = mutant.key()
        if key in mutant_dict:
            old_mutant = mutant_dict[key]
            if mutant.status != old_mutant.status or mutant.detected != old_mutant.detected:
                report_score.update_changed(mutant)
        else:
            report_score.update_new(mutant)
    return report_score

def parse_report_score

"""
Main
#TODO: use the python arguments module
usage_string = "python parser.py old_report_path new_report_path repo_path old_commit [new_commit]"
if len(sys.argv) != 3 or sys.argv[2] < 1:
  print usage_string
  sys.exit(1)
old_rep = str(sys.argv[1])
new_rep = str(sys.argv[2])
if not fnmatch.fnmatch(old_rep, "*.xml"): 
    print sys.stderr, "Old report ", old_rep, " is not named as an XML file"
if not fnmatch.fnmatch(new_rep, "*.xml"):
    print sys.stderr, "New report ", new_rep, " is not named as an XML file"
repo_path = str(sys.argv[3])
old_commit = str(sys.argv[4])
new_commit = str(sys.argv[5]) #optional can just pass an old_commit to compare with current HEAD
"""

#TODO: change this to two commits predetermined - check them out and run pit on them - hardcode paths into old_rep, new_rep
#TODO: if using head use rev-parse to get hash for use in file operations
old_rep = "/Users/tim/Code/commons-collections/pitReports/201703191437/mutations.xml"
new_rep = "/Users/tim/Code/commons-collections/pitReports/201703191437/mutations.xml"
report_score = get_differences(old_rep, new_rep, "HEAD^", "HEAD")
print "DELTA ", str(report_score)
