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
        self.index = str(index)#index to the first instruction where the mutation occurs, specific to ASM/bytecode representation (pit/MutationDetails.java:229)
        self.killing_test = str(killing_test)
        self.description = str(description) 
        self.target_line_no = None

    def key(self):
        """
        Used as a key to uniquely determine a mutation.
        """
        return self.source_file + self.line_no + self.mutator

    def __str__(self):
        """
        For human readable output of a mutant
        """
        return "[MUTANT] Detected: "+self.detected+" Status: "+self.status+" Src File: "+self.source_file+" Class: "+self.mut_class+ \
                " Method: "+self.mut_method+" Mutator: "+self.mutator+" Description: "+self.description+" Lineno: "+self.line_no+" Killing test: "+self.killing_test

class Score:
    """
    Store results of a set of mutants
    """

    def __init__(self, name, mutants=0, killed=0, survived=0, no_coverage=0):
        self.name=name
        self.mutants=mutants
        self.killed=killed
        self.survived=survived
        self.no_coverage=no_coverage

    def __str__(self):
        return self.name+" mutants: "+str(self.mutants)+" Killed: "+str(self.killed)+ \
        " Survived: "+str(self.survived)+" No Coverage: "+str(self.no_coverage)

    def update(self, mutant):
        """
        Update score given a mutant
        """
        self.mutants += 1
        if mutant.status == "no_coverage":
            self.no_coverage += 1
        elif mutant.status == "survived":
            self.survived += 1
        elif mutant.status == "killed": 
            self.killed += 1

class Mutation_score:
    def __init__(self, name):
        self.changed = Score("[CHANGED] "+name)
        self.new = Score("[NEW] "+name)
        self.unchanged = Score("[UNCHANGED] "+name)

class Method_score(Mutation_score):
    """
    Store scores for new/changed mutants across a method.
    """
    def __init__(self, name, src_class):
        Mutation_score.__init__(self, name)
        self.mutants = []
        self.src_class = src_class

    def update_new(self, mutant):
        self.new.update(mutant)
        self.mutants.append(mutant)

    def update_changed(self, mutant):
        self.changed.update(mutant)
        self.mutants.append(mutant) 

class Class_score(Mutation_score):
    """
    Store scores for new/changed mutants across a class.
    """
    def __init__(self, name, src_file):
        Mutation_score.__init__(self, name)
        self.methods = {}
        self.src_file = src_file

    def update_new(self, mutant):
        if mutant.mut_method not in self.methods:
            self.methods[mutant.mut_method] = Method_score(mutant.mut_method, self)
        self.new.update(mutant)
        self.methods[mutant.mut_method].update_new(mutant)
            
    def update_changed(self, mutant):
        if mutant.mut_method not in self.methods:
            self.methods[mutant.mut_method] = Method_score(mutant.mut_method, self)
        self.changed.update(mutant)
        self.methods[mutant.mut_method].update_changed(mutant) 

class File_score(Mutation_score):
    """
    Store scores for new/changed mutants across a source file..
    """
    def __init__(self, name, report):
        Mutation_score.__init__(self, name)
        self.classes = {}
        self.report = report

    def update_new(self, mutant):
        if mutant.mut_class not in self.classes:
            self.classes[mutant.mut_class] = Class_score(mutant.mut_class, self)
        self.new.update(mutant)
        self.classes[mutant.mut_class].update_new(mutant)
            
    def update_changed(self, mutant):
        if mutant.mut_class not in self.classes:
            self.classes[mutant.mut_class] = Class_score(mutant.mut_class, self)
        self.changed.update(mutant)
        self.classes[mutant.mut_class].update_changed(mutant)

class Report_score(Mutation_score):
    """
    Store scores for new/changed mutants across a report.
    """
    def __init__(self, name):
        Mutation_score.__init__(self, name)
        self.files = {}

    def add_file(self, filename):
        self.files[filename] = File_score()

    def get_file_score(self, filename):
        self.files[filename] = File_score() 

    def update_new(self, mutant):
        if mutant.source_file not in self.files:
            self.files[mutant.source_file] = File_score(mutant.source_file, self)
        self.new.update(mutant)
        self.files[mutant.source_file].update_new(mutant)
            
    def update_changed(self, mutant):
        if mutant.source_file not in self.files:
            self.files[mutant.source_file] = File_score(mutant.source_file, self)
        self.changed.update(mutant)
        self.files[mutant.source_file].update_changed(mutant)

    def __str__(self):
        return str(self.changed)+'\n'+str(self.new)
