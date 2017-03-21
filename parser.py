import xml.etree.ElementTree as ET
import sys
import os
from git import Repo

class Mutation_pit:

    #the mutation type, and method name must be the identifying descriptors - what can change?
    def __init__(self, detected, status, src_file, mut_class, mut_method, method_description, lineno, mutator, index, killing_test, description):
        self.detected = str(detected)
        self.status = str(status)
        self.src_file = str(src_file)
        self.mut_class = str(mut_class)
        self.mut_method = str(mut_method)
        self.method_description = str(method_description)
        self.lineno = str(lineno)
        self.mutator = str(mutator)
        self.index = str(index)#this is the index to the first instruction on which the mutation occurs, it is specific to how ASM represents bytecode (MutationDetails.java:229)
        self.killing_test = str(killing_test)#is this causing the dupes?
        self.description = str(description)

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

    def __str__(self):
        """
        For output purposes, human readable
        """
        return "Detected: "+self.detected+" Status: "+self.status+" Src File: "+self.src_file+" Class: "+self.mut_class+ \
                " Method: "+self.mut_method+" Mutator: "+self.mutator+" Description: "+self.description+" Lineno: "+self.lineno+" Killing test: "+self.killing_test

def parse_report(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    return root

def process_old(old_rep):
    mutant_dict = {}
    old_root = parse_report(old_rep)
    count = 0
    for child in old_root:
        """
        store from XML into an object
        detected, status, src_file, mutated_class, mutated_method, method_description, lineno, mutator, index, killing_test, description
        """
        mutant = Mutation_pit(child.attrib.get("detected"), child.attrib.get("status"), child[0].text, child[1].text, child[2].text, child[3].text, child[4].text, \
                child[5].text, child[6].text, child[7].text,  child[8].text)
        if mutant.key() not in mutant_dict:
            count += 1
            mutant_dict[mutant.key()] = mutant
    print "Count is ", count
    return (mutant_dict, count)

def get_differences(old_rep, new_rep):
    (mutant_dict, old_count) = process_old(old_rep)
    new_root = parse_report(new_rep)
    differences = []
    for child in new_root:
        """
        store from XML into an object
        detected, status, src_file, mutated_class, mutated_method, method_description, lineno, mutator, index, killing_test, description
        """
        mutant = Mutation_pit(child.attrib.get("detected"), child.attrib.get("status"), child[0].text, child[1].text, child[2].text, child[3].text, child[4].text, \
                child[5].text, child[6].text, child[7].text,  child[8].text)
        key = mutant.key()
        if key in mutant_dict:

            
            mutant.status == mutant_dict[key].status and mutant.detected == mutant_dict[key].detected:
            #we have found an unchanged mutant, this is not part of the "delta"
            continue
        differences.append(str(mutant))
        if mutant.
    return differences

old_rep = "/Users/tim/Code/commons-collections/pitReports/201703191437/mutations.xml"
new_rep = "/Users/tim/Code/commons-collections/pitReports/201703191437/mutations.xml"
usage_string = "python parser.py [old_report_path] [new_report_path]"

"""
Main
"""
if len(sys.argv) != 3 or sys.argv[2] < 1:
  print usage_string
  sys.exit()
old_rep = str(sys.argv[1])
new_rep = str(sys.argv[2])

differences = get_differences(old_rep, new_rep)
for mutant in differences:
    print str(mutant)
print "There were ",len(differences)," mutants"
