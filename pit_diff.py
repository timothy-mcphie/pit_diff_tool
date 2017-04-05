import xml.etree.ElementTree as ET
import sys
import parser
from mutation import Mutant, Mutation_score

gitinfo = {}

def parse_report(filename):
    """
    Returns the root tag of an XML file
    """
    tree = ET.parse(filename)
    root = tree.getroot()
    return root

def update_mutation_score(score, mutant):
    """
    Helper method, given mutation_score object and a mutant, updates the score accordingly
    """
    score.total_mutants += 1
    if mutant.status == "no_coverage":
        score.no_coverage += 1
    elif mutant.status == "survived":
        score.survived += 1
    elif mutant.status == "killed": 
        score.killed += 1

def process_report(report, new=False):
    """
    Traverses a pit XML file - returns either a dictionary of unique mutants and a score object, or a list of unique mutants and a score object.
    """
    #TODO: we need to update old files to their new line numbers!
    #update_mutant(mutant, modified_files)
    mutant_dict = {}
    root = parse_report(report) 
    score = Mutation_score(report)
    repeats = 0
    if new:
        mutant_list = []
    for child in root:
        """
        store from XML into an object
        Object tuples: detected, status, source_file, mutated_class, mutated_method, method_description, line_no, mutator, index, killing_test, description
        """
        mutant = Mutant(child.attrib.get("detected"), child.attrib.get("status"), child[0].text, child[1].text, child[2].text, child[3].text, child[4].text, \
                child[5].text, child[6].text, child[7].text,  child[8].text)
        key = mutant.key()
        if key not in mutant_dict:
            #the mutant has not been seen
            mutant_dict[key] = mutant 
        else:
            #mutant has been seen on this line number before - only different due to ASM index
            repeats += 1 
            continue
        update_mutation_score(score, mutant)
        if new:
            mutant_list.append(mutant)
    if new:
        return (mutant_list, score)
    return (mutant_dict, score)

def get_differences(old_rep, new_rep):
    modified_files = parser.process_git_info("HEAD^", "HEAD") 
    #TODO: - testing purposes - if using head use rev-parse to get has for use in file operations
    #TODO: change this to two commits predetermined - check them out and run pit on them - hardcode paths into old_rep, new_rep
    (mutant_dict, old_score) = process_report(old_rep)
    (mutant_list, new_score) = process_report(new_rep, True)
    diff_score = Mutation_score(old_rep+new_rep)
    new_mutants = []
    changed_mutants = []
    for mutant in mutant_list:
        key = mutant.key()
        update_mutant(mutant, modified_files) 
        if key in mutant_dict:
            old_mutant = mutant_dict[key] #we've seen this mutant before 
            if mutant.status != old_mutant.status or mutant.detected != old_mutant.detected:
                changed_mutants.append(str(mutant)) #a changed mutant - this is part of the delta
                update_mutation_score(diff_score, mutant) 
        else:
            #we haven't seen this mutant before, this is part of the "delta"
            new_mutants.append(str(mutant))
            update_mutation_score(diff_score, mutant)
    differences = new_mutants + changed_mutants
    return (differences, diff_score)

#TODO: How to get the pit report names?
old_rep = "/Users/tim/Code/commons-collections/pitReports/201703191437/mutations.xml"
new_rep = "/Users/tim/Code/commons-collections/pitReports/201703191437/mutations.xml"
usage_string = "python parser.py [old_report_path] [new_report_path]"

"""
Main
if len(sys.argv) != 3 or sys.argv[2] < 1:
  print usage_string
  #TODO: could this be problematic for calling scripts?... Integrate into a project for stats part
  sys.exit(1)
old_rep = str(sys.argv[1])
new_rep = str(sys.argv[2])
TODO: add checks for files being XML files - introduce error checking into reports
(differences, diff_score) = get_differences(old_rep, new_rep)
print "DELTA ", str(diff_score)
"""

(differences, diff_score) = get_differences(old_rep, new_rep)
print "Differences in mutations is: ", str(diff_score)
