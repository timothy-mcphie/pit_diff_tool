import xml.etree.ElementTree as ET
import sys
import cmd
import csv
import fnmatch
from mutant import Mutant
from scores import Report_score, File_score, Class_score, Method_score, Mutation_score

#can provide a granularity of detecting if a method or class has changed (a mutant which belongs to it is no longer present or a new mutant has appeared/edited) - can't do if edits has occurred level of granularity

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
    Return a flag if it belongs to a file that was modified
    """
    #TODO: Class and method level impact analysis granularity - for ANY edit.
    #For a class or method to be edited, a diff line must be removed or added (source_line_no or target_line_no == None)
    #If mutants are added or removed due to these edits, we can determine the class/method has been edited
    #But if no mutants are added/removed, we can't state that an edit has occurred.
    #Needs more advanced diff parsing - build class and method level boundaries watch for changes impacting within. 

    source_file = mutant.source_file
    if source_file not in modified_files:
        return False
    
    ((target_to_source_dict, target_to_source_list), target_file) = modified_files[source_file]

    if target_file != source_file:
        #if the file was renamed, assign the mutant the old file name
        mutant.target_file = target_file
        mutant.source_file = source_file

    mutant.target_line_no = mutant.line_no
    if mutant.line_no in target_to_source_dict:
        #a new line with no line number in the previous snapshot, gets None as source_line_no
        mutant.line_no = target_to_source_dict[mutant.line_no].source_line_no
        return True
    
    i = 0
    while i < len(target_to_source_list) - 1 and mutant.line_no < target_to_source_list[i].target_line_no:
        i += 1 
    while i > 0 and target_to_source_list[i].target_line_no < mutant.line_no:
        if target_to_source_list[i].source_line_no is None:
            i -= 1 
        else:
            break
    line = target_to_source_list[i]
    if line.source_line_no is None:
        #no update to take place
        return True
    mutant.line_no = mutant.line_no + (line.source_line_no - line.target_line_no) 
    return True

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

def update_class_and_method_modified(score, mutant):
    #TODO: use the "interface class" and loop over -> neater
    file_score = score.get_child(File_score, mutant.source_file)
    class_score = file_score.get_child(Class_score, mutant.mut_class)
    class_score.modified = True
    method_score = class_score.get_child(Method_score, mutant.mut_method)
    method_score.modified = True


def get_differences(old_report, new_report, report_name, modified_files):
    """
    Get the changed mutants between two mutation reports, if show_all is true, removed, unchanged and new mutants will be added to the score.
    """
    score = Report_score(report_name, None)
    old_mutants = process_report(old_report)
    new_mutants = process_report(new_report)
    
    #TODO: Use sets - iterate over an intersection for changed statuses
    #broken out of unchanged/new loop for speed and readability, although calling with show_all introduces additional overhead
    
    name_map = {}
    for mutant in new_mutants.values():
        modified = update_mutant(mutant, modified_files)
        if mutant.key() in old_mutants:
            old_mutant = old_mutants[mutant.key()]
            if mutant.status != old_mutant.status or mutant.detected != old_mutant.detected:
                score.update_changed(old_mutant, mutant, modified) 

            #translate old class/method names to new
            if old_mutant.name_key() not in name_map:
                name_map[old_mutant.name_key()] = (mutant.mut_class, mutant.mut_method)

            del old_mutants[mutant.key()]
        else: #brand new mutant
            update_class_and_method_modified(score, mutant)

    for old_mutant in old_mutants.values():
        if old_mutant.name_key() in name_map:
            renamed_class = name_map[old_mutant.name_key()][0]
            renamed_method = name_map[old_mutant.name_key()][1]
            old_mutant.mut_class = renamed_class 
            old_mutant.mut_method = renamed_method
        update_class_and_method_modified(score, old_mutant)
    return score

def parse_file_score(report_score):
    """
    Get two lists of directly changed mutants (those in modified files) 
    and the indirectly changed mutants (those in unmodified files) 
    """ 
    modified = Mutation_score("modified", None)
    unmodified = Mutation_score("unmodified", None)
    for file_score in report_score.children.values(): 
        if file_score.modified:
            modified.add_changed(file_score.changed)
        else:
            unmodified.add_changed(file_score.changed)
    return (modified, unmodified)

def parse_class_method_score(report_score):
    """
    Get two lists of directly changed mutants (those in modified files) 
    and the indirectly changed mutants (those in unmodified files) 
    """ 
    modified_class = Mutation_score("modified_class", None)
    unmodified_class = Mutation_score("unmodified_class", None)
    modified_method = Mutation_score("modified_method", None)
    unmodified_method = Mutation_score("unmodified_method", None)
    for file_score in report_score.children.values(): 

        if file_score.modified is True:
            for class_score in file_score.children.values():
                if class_score.modified:
                    modified_class.add_changed(class_score.changed)
                else:
                    unmodified_class.add_changed(class_score.changed)

                if class_score.modified is True:
                    for method_score in class_score.children.values():
                        if method_score.modified:
                            modified_method.add_changed(method_score.changed)
                        else:
                            unmodified_method.add_changed(method_score.changed)

    return (modified_class, unmodified_class, modified_method, unmodified_method)

def get_pit_diff(old_commit, new_commit, repo, old_report, new_report, modified_files):
    """
    Entry point for getting difference between two pit reports
    NB it is the job of calling programs to check both repo and modified_files are not empty/uninitialised
    """
    check_report(old_report)
    check_report(new_report)
    return get_differences(old_report, new_report, old_commit+" -> "+new_commit, modified_files)
