import xml.etree.ElementTree as ET
import sys
import os
import logging
from git import Repo

class Mutation_score:
    """
    Helper class to store results of a mutation report
    """

    def __init__(self, name, total_mutants=0, killed=0, survived=0, no_coverage=0):
        self.name=str(name)
        self.total_mutants=total_mutants
        self.killed=killed
        self.survived=survived
        self.no_coverage=no_coverage

class Mutant:
    """
    Helper class to store information of each mutation test performed by pit (this is gleamed from the pit XML report)
    """

    def __init__(self, detected, status, src_file, mut_class, mut_method, method_description, lineno, mutator, index, killing_test, description):
        self.detected = str(detected).lower()
        self.status = str(status).lower()
        self.src_file = str(src_file)
        self.mut_class = str(mut_class)
        self.mut_method = str(mut_method)
        self.method_description = str(method_description)
        self.lineno = str(lineno)
        self.mutator = str(mutator)
        self.index = str(index)#this is the index to the first instruction on which the mutation occurs, it is specific to how ASM represents bytecode (MutationDetails.java:229)
        self.killing_test = str(killing_test)#is this causing the dupes?
        self.description = str(description) 
        self.count = 1#used to track repeat mutants ie different indexes but essentially the same mutant...

    #the mutation type, and method name must be the identifying descriptors - what can change?
    def key(self):
        """
        Used as a key to uniquely determine a mutation. Currently uses description as part of key to uniquely verify
        """
        return self.detected + \
        self.status + \
        self.src_file + \
        self.mut_class + \
        self.mut_method + \
        self.method_description + \
        self.lineno + \
        self.mutator + \
        self.description + \
        self.killing_test
        #+ self.index

    def __str__(self):
        """
        For output purposes, human readable
        """
        return "MUTANT Detected: "+self.detected+" Status: "+self.status+" Src File: "+self.src_file+" Class: "+self.mut_class+ \
                " Method: "+self.mut_method+" Mutator: "+self.mutator+" Description: "+self.description+" Lineno: "+self.lineno+" Killing test: "+self.killing_test

def parse_report(filename):
    """
    returns the root tag of an XML file
    """
    tree = ET.parse(filename)
    root = tree.getroot()
    return root

def update_mutation_score(score, mutant):
    """
    Helper method, given mutation_score object and a Mutant, updates the score accordingly
    """
    if mutant.status == "no_coverage":
        score.no_coverage += 1
    elif mutant.staus == "survived":
        score.survived += 1
    elif mutant.status == "killed": 
        score.killed += 1
    return

def preprocess_report(report):
    mutant_dict = {}
    root = parse_report(report) 
    score = Mutation_score(report)
    for child in root:
        """
        store from XML into an object
        detected, status, src_file, mutated_class, mutated_method, method_description, lineno, mutator, index, killing_test, description
        """
        mutant = Mutant(child.attrib.get("detected"), child.attrib.get("status"), child[0].text, child[1].text, child[2].text, child[3].text, child[4].text, \
                child[5].text, child[6].text, child[7].text,  child[8].text)
        if mutant.key() not in mutant_dict:
            score.total_mutants += 1
            update_mutation_score(score, mutant)
            mutant_dict[mutant.key()] = mutant
        else:
            mutant_dict[mutant.key()].count += 1
    logger.debug("Total number of mutants in report is ", old_score.total_mutants)
    return (mutant_dict, score)

def get_differences(old_rep, new_rep):
    (mutant_dict, old_score) = preprocess_report(old_rep)
    new_root = parse_report(new_rep)
    new_mutants = []
    changed_mutants = []
    new_score = Mutation_score(new_rep)
    for child in new_root:
        """
        store from XML into an object
        detected, status, src_file, mutated_class, mutated_method, method_description, lineno, mutator, index, killing_test, description
        """
        mutant = Mutant(child.attrib.get("detected"), child.attrib.get("status"), child[0].text, child[1].text, child[2].text \
                              child[3].text, child[4].text, child[5].text, child[6].text, child[7].text,  child[8].text)
        key = mutant.key()
        update_mutation_score(score, mutant)#where does this go logically?
        if key in mutant_dict:
            old_mutant = mutant_dict[key]
            #we've seen this mutant before 
            if mutant.status != old_mutant.status or mutant.detected != old_mutant.detected:
                #we have found an changed mutant, this is not part of the "delta"
                changed_mutants.append(str(mutant))
            else:
                #mutant is unchanged - unnecessary statement
                continue
        else:
            new_mutants.append(str(mutant))
        if mutant.
    differences = new_mutants + changed_mutants
    return differences

old_rep = "/Users/tim/Code/commons-collections/pitReports/201703191437/mutations.xml"
new_rep = "/Users/tim/Code/commons-collections/pitReports/201703191437/mutations.xml"
usage_string = "python parser.py [old_report_path] [new_report_path]"

"""
Main
"""
if len(sys.argv) != 3 or sys.argv[2] < 1:
  print usage_string
  #could this be problematic for calling scripts?... Integrate into a project for stats part
  sys.exit(1)
logger = Logger()
logger.setLevel(debug)
old_rep = str(sys.argv[1])
new_rep = str(sys.argv[2])
#TODO: add checks for files being XML files - introduce error checking into reports

differences = get_differences(old_rep, new_rep)
for mutant in differences:
    logger.debug(str(mutant))
logger.debug("There were ",len(differences)," mutants")
