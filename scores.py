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
    """
    Abstract ish class
    """
    def __init__(self, name, parent, children=True):
        self.new = Score("[NEW] "+name)
        self.changed = Score("[CHANGED] "+name)
        self.unchanged = Score("[UNCHANGED] "+name)
        self.removed = Score("[REMOVED] "+name)
        self.parent = parent
        if children:
            self.children = {}

    def get_child_score(self, Class, key):
        if key not in self.children:
            self.children[key] = Class(key, self)
        return self.children[key]

    def update_new(self, mutant):
        self.new.update(mutant)

    def update_changed(self, mutant):
        self.changed.update(mutant)

    def update_unchanged(self, mutant):
        self.unchanged.update(mutant)

    def update_removed(self, mutant):
        self.removed.update(mutant)

class Method_score(Mutation_score):
    """
    Store scores for new/changed mutants across a method.
    """
    def __init__(self, name, src_class):
        Mutation_score.__init__(self, name, src_class, False)
        #append mutants within methods for output purposes?

class Class_score(Mutation_score):
    """
    Store scores for new/changed mutants across a class.
    """
    def update_new(self, mutant):
        Mutation_score.update_new(self, mutant)
        self.get_child_score(Method_score, mutant.mut_method).update_new(mutant)

    def update_changed(self, mutant):
        Mutation_score.update_changed(self, mutant)
        self.get_child_score(Method_score, mutant.mut_method).update_changed(mutant)

    def update_unchanged(self, mutant):
        Mutation_score.update_unchanged(self, mutant)
        self.get_child_score(Method_score, mutant.mut_method).update_unchanged(mutant)

    def update_removed(self, mutant):
        Mutation_score.update_removed(self, mutant)
        self.get_child_score(Method_score, mutant.mut_method).update_removed(mutant)

class File_score(Mutation_score):
    """
    Store scores for new/changed mutants across a source file..
    """
    def update_new(self, mutant):
        Mutation_score.update_new(self, mutant)
        self.get_child_score(Class_score, mutant.mut_class).update_new(mutant)

    def update_changed(self, mutant):
        Mutation_score.update_changed(self, mutant)
        self.get_child_score(Class_score, mutant.mut_class).update_changed(mutant)

    def update_unchanged(self, mutant):
        Mutation_score.update_unchanged(self, mutant)
        self.get_child_score(Class_score, mutant.mut_class).update_unchanged(mutant)

    def update_removed(self, mutant):
        Mutation_score.update_removed(self, mutant)
        self.get_child_score(Method_score, mutant.mut_method).update_removed(mutant)

class Report_score(Mutation_score):
    """
    Store scores for new/changed mutants across a report.
    """
    #Can refactor so interface has attribute which can be the class type of the children

    def update_new(self, mutant):
        Mutation_score.update_new(self, mutant)
        self.get_child_score(File_score, mutant.source_file).update_new(mutant)

    def update_changed(self, mutant):
        Mutation_score.update_changed(self, mutant)
        self.get_child_score(File_score, mutant.source_file).update_changed(mutant)

    def update_unchanged(self, mutant):
        Mutation_score.update_unchanged(self, mutant)
        self.get_child_score(File_score, mutant.source_file).update_unchanged(mutant)

    def update_removed(self, mutant):
        Mutation_score.update_removed(self, mutant)
        self.get_child_score(Method_score, mutant.mut_method).update_removed(mutant)

    def __str__(self):
        return str(self.new)+'\n'+str(self.changed)+'\n'+str(self.unchanged)+'\n'+str(self.removed)
