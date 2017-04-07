import xml.etree.ElementTree as ET
import sys
import diff_parser as parser
import fnmatch
from mutant import Mutant
from scores import Report_score

def update_mutant(mutant, modified_files):
    """
    Update a mutant in the new report to have the correct line numbers by parsing the hunks in it's patchedfile
    """
    source_file = mutant.source_file
    if source_file not in modified_files:
        return

    ((target_to_source_dict, target_to_source_list), target_file) = modified_files[source_file]

    if target_file != source_file:
        print "file rename"
        #if the file was renamed, assign the mutant the old file name
        mutant.target_file = target_file
        mutant.source_file = source_file

    if mutant.line_no in target_to_source_dict:
        mutant.target_line_no = mutant.line_no
        mutant.line_no = target_to_source_dict[mutant.line_no].source_line_no
        #if a line is new and belonged to no line in the previous snapshot, assign None as source_line_no
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

def process_report(report):
    """
    Parse a pit XML report - returns a dict of unique mutants and a score
    """
    mutant_dict = {}
    root = parse_report(report) 
    for child in root:
        mutant = Mutant(child.attrib.get("detected"), child.attrib.get("status"), child[0].text, child[1].text, child[2].text,\
                child[3].text, child[4].text, child[5].text, child[6].text, child[7].text,  child[8].text)
        if mutant.key() not in mutant_dict:
            mutant_dict[mutant.key()] = mutant
    return mutant_dict

def get_differences(old_report, new_report, report_name):
    """
    Get the differences
    """
    #TODO: Use sets, to get the unchanged mutants and missing mutants
    score = Report_score(report_name, None)
    old_mutants = process_report(old_report)
    new_mutants = process_report(new_report)
    name_map = {}
    for mutant in new_mutants.values():
        update_mutant(mutant, modified_files)
        if mutant.key() in old_mutants:
            old_mutant = old_mutants[mutant.key()]
            if mutant.status != old_mutant.status or mutant.detected != old_mutant.detected:
                score.update_changed(mutant)
            else:
                score.update_unchanged(mutant)
            if mutant.mut_class != old_mutant.mut_class or mutant.mut_method != old_mutant.mut_method:
                if old_mutant.name_key() not in name_map:
                    name_map[old_mutant.name_key()] = (mutant.mut_class, mutant.mut_method)
            if mutant.target_file is not None:
                name_map[mutant.source_file] = mutant.target_file
            del old_mutants[mutant.key()]
        else:
            score.update_new(mutant)
    for mutant in old_mutants.values():
        if mutant.name_key() in name_map:
            renamed_class = name_map[mutant.name_key()][0]
            renamed_method = name_map[mutant.name_key()][1]
            mutant.mut_class = renamed_class 
            mutant.mut_method = renamed_method
        if mutant.source_file in name_map:
            mutant.source_file = name_map[mutant.source_file]
        score.update_removed(mutant)
    return score

def parse_score(report_score):
    for file_score in score.children.keys():
        pass

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
old_rep = "/Users/tim/Code/commons-collections/pitReports/201704062226/mutations.xml"
new_rep = "/Users/tim/Code/commons-collections/pitReports/201704062043/mutations.xml"
old_commit="cfffa7138c04b971d119a5da94b9a71d610bba0a"
new_commit="HEAD"
repo_path="/Users/tim/Code/commons-collections"
modified_files = parser.process_git_info(old_commit, new_commit, repo_path) 
report_score = get_differences(old_rep, new_rep, old_commit+" -> "+new_commit)
print str(report_score)
