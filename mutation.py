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

    def __str__(self):
        return "[SCORE] Name: "+self.name+" Total mutants: "+str(self.total_mutants)+" Killed: "+str(self.killed)+" No Coverage: "+str(self.no_coverage)

class Mutant:
    """
    Helper class to store information of each mutation test performed by pit (this is gleamed from the pit XML report)
    """

    def __init__(self, detected, status, source_file, mut_class, mut_method, method_description, line_no, mutator, index, killing_test, description):
        self.detected = str(detected).lower()
        self.status = str(status).lower()
        self.source_file = str(source_file)
        self.mut_class = str(mut_class)
        self.mut_method = str(mut_method)
        self.method_description = str(method_description)
        self.line_no = str(line_no)
        self.mutator = str(mutator)
        self.index = str(index)#this is the index to the first instruction on which the mutation occurs, it is specific to how ASM represents bytecode (MutationDetails.java:229)
        self.killing_test = str(killing_test)
        self.description = str(description) 
        self.line = None

    def key(self):
        """
        Used as a key to uniquely determine a mutation.
        """
        return self.source_file + \
        self.mut_class + \
        self.mut_method + \
        self.method_description + \
        self.mutator + \
        self.description + \
        self.killing_test + \
        self.line_no

    def __str__(self):
        """
        For human readable output of a mutant
        """
        return "[MUTANT] Detected: "+self.detected+" Status: "+self.status+" Src File: "+self.source_file+" Class: "+self.mut_class+ \
                " Method: "+self.mut_method+" Mutator: "+self.mutator+" Description: "+self.description+" Lineno: "+self.line_no+" Killing test: "+self.killing_test
