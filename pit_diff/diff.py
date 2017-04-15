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
    #TODO: if a mutant's source line number is None, the mutant is in a modified class/method
    #do we care if there are modifications which don't cause changes to mutants?
    #if a mutant disappears it is in a modified class/method
    #have a lookup dict to speedup - no need to traverse tree if we've already marked
    #as modified
    #does this catch all modifications?

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


def get_remaining_diff(old_mutants, new_mutants, score):
    """
    Called by get_differences, parses all other mutants which are not "changed" and inserts them into the score tree
    """
    #Check for unchanged and new mutants 
    name_map = {}
    for mutant in new_mutants.values():
        update_mutant(mutant, modified_files)
        if mutant.key() in old_mutants:
            old_mutant = old_mutants[mutant.key()]
            if mutant.status == old_mutant.status and mutant.detected == old_mutant.detected: 
                score.update_unchanged(mutant)
            #a mutant existing in both reports - check if it's parent classes/methods are renamed so removed mutants can be assigned in the tree
            if mutant.mut_class != old_mutant.mut_class or mutant.mut_method != old_mutant.mut_method:
                if old_mutant.name_key() not in name_map:
                    name_map[old_mutant.name_key()] = (mutant.mut_class, mutant.mut_method)
            if mutant.target_file is not None:
                name_map[mutant.source_file] = mutant.target_file
            del old_mutants[mutant.key()]
        else:
            score.update_new(mutant)

    #Add old mutants 
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

def get_differences(old_report, new_report, report_name, modified_files, show_all):
    """
    Get the changed mutants between two mutation reports, if show_all is true, removed, unchanged and new mutants will be added to the score.
    """
    score = Report_score(report_name, None)
    old_mutants = process_report(old_report)
    new_mutants = process_report(new_report)
    
    #TODO: Use sets - iterate over an intersection for changed statuses
    #broken out of unchanged/new loop for speed and readability, although calling with show_all introduces additional overhead
    for mutant in new_mutants.values():
        update_mutant(mutant, modified_files)
        if mutant.key() in old_mutants:
            old_mutant = old_mutants[mutant.key()]
            if mutant.status != old_mutant.status or mutant.detected != old_mutant.detected:
                score.update_changed(old_mutant, mutant) 
    if show_all:
        get_remaining_diff(old_mutants, new_mutants, score)
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

def get_pit_diff(old_commit, new_commit, repo, old_report, new_report, modified_files, show_all=False):
    check_report(old_report)
    check_report(new_report)
    if not modified_files:
        print "[PIT_DIFF] Modified files translation dictionary not initialised, cannot update mutants"
        return None
    #TODO: Move repo check into sputnik program - is it necessary?
    #if not cmd.is_repo(repo):
    #    return None
    report_score = get_differences(old_report, new_report, old_commit+" -> "+new_commit, modified_files, show_all)
    return report_score
