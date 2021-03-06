class Mutant(object):
    """
    Helper class to store information of each mutation test performed by pit (this is gleamed from the pit XML report)
    """

    def __init__(self, detected, status, source_file, mut_class, mut_method, method_description, line_no, mutator, index, killing_test, description):
        self.detected = str(detected).lower() #false generally only comes with statuses of survived or no_coverage
        self.status = str(status).lower()
        self.source_file = str(source_file)
        self.mut_class = str(mut_class) # the class mutated
        self.mut_method = str(mut_method) # the method mutated
        self.method_description = str(method_description)
        self.line_no = int(line_no)
        self.mutator = str(mutator)
        self.index = str(index)#index to the first instruction where the mutation occurs, specific to ASM/bytecode representation (pit/MutationDetails.java:229)
        self.killing_test = str(killing_test)
        self.description = str(description) 

        self.target_line_no = None
        self.target_file = None
        self.previous_status = None
        self.previous_detected = None

    def get_index(self):
        """
        Used for indexing in the array of a changed score object
        """
        if self.status == "no_coverage":
            return 0
        elif self.status == "survived":
            return 1   
        elif self.status == "killed": 
            return 2
        elif self.status == "timed_out":
            return 3
        elif self.status == "memory_error":
            return 4
        elif self.status == "run_error":
            return 5
        elif self.status == "non_viable":
            return 6

    def key(self):
        """
        Used as a key to uniquely determine a mutation.
        """
        return self.source_file+str(self.line_no)+self.mutator+self.description

    def name_key(self):
        """
        Used to assign removed mutants to renamed methods/classes
        """
        return self.mut_class+" "+self.mut_method

    def __str__(self):
        """
        For human readable output of a mutant
        """
        return "[MUTANT] Detected: "+self.detected+" Status: "+self.status+" Src File: "+self.source_file+" Class: "+self.mut_class+ \
                " Method: "+self.mut_method+" Mutator: "+self.mutator+" Description: "+self.description+" Lineno: "+str(self.line_no)+" Killing test: "+self.killing_test
