import xml.etree.ElementTree as ET
import sys
import cmd
import fnmatch
from mutant import Mutant
from scores import Report_score

def check_report(report):
    if not fnmatch.fnmatch(report, "*.xml"): 
        print "[PIT_DIFF] Report ", old_rep, " is not named as an XML file exiting"
        sys.exit(1)

def parse_report(filename):
    """
    Returns the root tag of an XML file
    """
    #TODO: Add error handling
    tree = ET.parse(filename)
    root = tree.getroot()
    return root

def update_mutant(mutant, modified_files):
    """
    Update a mutant in the new report to have the line numbers and file name it had in the previous commit
    """
    source_file = mutant.source_file
    if source_file not in modified_files:
        return

    ((target_to_source_dict, target_to_source_list), target_file) = modified_files[source_file]

    if target_file != source_file:
        #if the file was renamed, assign the mutant the old file name
        mutant.target_file = target_file
        mutant.source_file = source_file

    mutant.target_line_no = mutant.line_no
    if mutant.line_no in target_to_source_dict:
        #a new line with no line number in the previous snapshot, gets None as source_line_no
        mutant.line_no = target_to_source_dict[mutant.line_no].source_line_no
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
    mutant.line_no = mutant.line_no + (line.source_line_no - line.target_line_no) 

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

def get_differences(old_report, new_report, report_name, modified_files):
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

    for old_mutant in old_mutants.values():
        if old_mutant.name_key() in name_map:
            renamed_class = name_map[old_mutant.name_key()][0]
            renamed_method = name_map[old_mutant.name_key()][1]
            old_mutant.mut_class = renamed_class 
            old_mutant.mut_method = renamed_method
        if old_mutant.source_file in name_map:
            old_mutant.source_file = name_map[old_mutant.source_file]
        score.update_removed(old_mutant)
    return score

def parse_report_score(report_score, csv=False):
    """
    Parse score and write to csv
    """
    if csv:
        #csv module set up code here
        pass

    delta = []
    #output only the changed mutants and their locations
    for file_score in report_score.children.values():
        for class_score in file_score.children.values():
            for method_score in class_score.children.values(): 
                if method_score.changed.mutants > 0:
                    delta += (method_score.changed_mutants)
                    #TODO: use a lambda to print the str of each changed mutant each method score

    return delta

def get_pit_diff(old_commit, new_commit, repo_path, old_rep, new_rep, modified_files):
    check_report(old_rep)
    check_report(new_rep)
    if not modified_files:
        print "[PIT_DIFF] Modified files translation dictionary not initialised, cannot update mutants"
        return None
    #TODO: Move repo check into sputnik program - is it necessary?
    #if not cmd.is_repo(repo_path):
    #    return None
    report_score = get_differences(old_rep, new_rep, old_commit+" -> "+new_commit, modified_files)
    return report_score
